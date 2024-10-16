from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class PurchaseRequestMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    # supplier_id = fields.Many2one('res.partner', string='Supplier', required=False)
    supplier_ids = fields.Many2many('res.partner', string="Suppliers", domain="[('supplier_rank', '>', 0)]")

    def make_purchase_order(self):
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]

        for supplier in self.supplier_ids:
            purchase = False
            for item in self.item_ids:
                line = item.line_id
                if item.product_qty <= 0.0:
                    raise UserError(_("Enter a positive quantity."))
                if self.purchase_order_id:
                    purchase = self.purchase_order_id
                if not purchase:
                    po_data = self._prepare_purchase_order(
                        line.request_id.picking_type_id,
                        line.request_id.group_id,
                        line.company_id,
                        line.origin,
                    )
                    po_data.update({'partner_id': supplier.id})
                    purchase = purchase_obj.create(po_data)

                domain = self._get_order_line_search_domain(purchase, item)
                available_po_lines = po_line_obj.search(domain)
                new_pr_line = True
                if not line.product_uom_id:
                    line.product_uom_id = item.product_uom_id
                alloc_uom = line.product_uom_id
                wizard_uom = item.product_uom_id
                if available_po_lines and not item.keep_description:
                    new_pr_line = False
                    po_line = available_po_lines[0]
                    po_line.purchase_request_lines = [(4, line.id)]
                    po_line.move_dest_ids |= line.move_dest_ids
                    po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                        po_line.product_uom_qty, alloc_uom
                    )
                    wizard_product_uom_qty = wizard_uom._compute_quantity(
                        item.product_qty, alloc_uom
                    )
                    all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                    self.create_allocation(po_line, line, wizard_product_uom_qty, alloc_uom)
                else:
                    po_line_data = self._prepare_purchase_order_line(purchase, item)
                    if item.keep_description:
                        po_line_data["name"] = item.name
                    po_line = po_line_obj.create(po_line_data)
                    po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                        po_line.product_uom_qty, alloc_uom
                    )
                    wizard_product_uom_qty = wizard_uom._compute_quantity(
                        item.product_qty, alloc_uom
                    )
                    all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                    self.create_allocation(po_line, line, wizard_product_uom_qty, alloc_uom)
                new_qty = pr_line_obj._calc_new_qty(
                    line, po_line=po_line, new_pr_line=new_pr_line
                )
                po_line.product_qty = new_qty

                date_required = item.line_id.date_required
                po_line.date_planned = datetime(
                    date_required.year, date_required.month, date_required.day
                )

                res.append(purchase.id)

        return {
            "domain": [("id", "in", res)],
            "name": _("RFQ"),
            "view_mode": "tree,form",
            "res_model": "purchase.order",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }

    # def make_purchase_order(self):
    #     PurchaseOrder = self.env['purchase.order']
    #     for wizard in self:
    #         for supplier in wizard.supplier_ids:
    #             po_vals = {
    #                 'partner_id': supplier.id,
    #                 'order_line': [],
    #             }
    #             for line in wizard.item_ids:
    #                 po_line_vals = {
    #                     'product_id': line.product_id.id,
    #                     'name': line.name,
    #                     'product_qty': line.product_qty,
    #                     'product_uom': line.product_uom_id.id,
    #                     'price_unit': 0.0,
    #                     'date_planned': fields.Date.today(),
    #                 }
    #                 po_vals['order_line'].append((0, 0, po_line_vals))
    #             PurchaseOrder.create(po_vals)