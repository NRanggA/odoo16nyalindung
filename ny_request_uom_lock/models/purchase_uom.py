from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mom_pr_uom_locked = fields.Boolean(compute='_compute_mom_pr_uom_locked')

    @api.depends('purchase_request_lines.request_id.mom_enforce_uom')
    def _compute_mom_pr_uom_locked(self):
        for line in self:
            line.mom_pr_uom_locked = any(line.purchase_request_lines.mapped('request_id.mom_enforce_uom'))

    @api.constrains('product_id', 'product_uom', 'purchase_request_lines')
    def _check_mom_pr_uom(self):
        for line in self:
            requests = line.purchase_request_lines.filtered('request_id.mom_enforce_uom')
            if requests and any(
                request.product_id != line.product_id or request.product_uom_id != line.product_uom
                for request in requests
            ):
                raise ValidationError(_(
                    'Produk dan satuan RFQ/PO harus mengikuti PR sumber: %s. '
                    'Satuan tidak dapat diganti pada baris pembelian ini.'
                ) % ', '.join(requests.mapped('request_id.name')))


class MakePurchaseOrderItem(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order.item'

    mom_source_uom_locked = fields.Boolean(related='line_id.request_id.mom_enforce_uom')

    @api.constrains('line_id', 'product_uom_id')
    def _check_source_uom(self):
        for item in self:
            if item.mom_source_uom_locked and item.product_uom_id != item.line_id.product_uom_id:
                raise ValidationError(_(
                    'Satuan pada Create RFQ harus mengikuti PR %(request)s: %(unit)s.',
                    request=item.line_id.request_id.name,
                    unit=item.line_id.product_uom_id.display_name,
                ))


class MakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        item._check_source_uom()
        vals = super()._prepare_purchase_order_line(po, item)
        if item.line_id.request_id.mom_enforce_uom:
            target = item.line_id.product_uom_id
            purchase_uom = item.product_id.uom_po_id or item.product_id.uom_id
            minimum = item.line_id._get_supplier_min_qty(item.product_id, po.partner_id)
            vals['product_qty'] = max(
                item.product_uom_id._compute_quantity(item.product_qty, target),
                purchase_uom._compute_quantity(minimum, target),
            )
            source = self.env['uom.uom'].browse(vals['product_uom'])
            vals['price_unit'] = source._compute_price(vals.get('price_unit', 0.0), target)
            vals['product_uom'] = target.id
        return vals


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        if not request_line.request_id.mom_enforce_uom or not po_line:
            return super()._calc_new_qty(request_line, po_line=po_line, new_pr_line=new_pr_line)
        target = po_line.product_uom
        minimum = 0.0
        if not po_line.order_id.dest_address_id:
            minimum = self._get_supplier_min_qty(po_line.product_id, po_line.order_id.partner_id)
            source = po_line.product_id.uom_po_id or po_line.product_id.uom_id
            minimum = source._compute_quantity(minimum, target)
        if new_pr_line:
            qty = po_line.product_uom_qty
        else:
            allocations = po_line.purchase_request_lines.purchase_request_allocation_ids.filtered(
                lambda allocation: allocation.purchase_line_id == po_line)
            qty = sum(a.product_uom_id._compute_quantity(a.requested_product_uom_qty, target) for a in allocations)
        return max(qty, minimum)
