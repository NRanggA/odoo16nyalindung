from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # pricelist_id_2 = fields.Many2one('product.pricelist', string='Grading')
    route_id = fields.Many2one('stock.route', string='Route', domain=[('sale_selectable', '=', True)], ondelete='restrict', check_company=True)

    # Field relasi ke sale order line melon
    sale_order_line_melon_ids = fields.One2many('sale.order.line.melon', 'sale_order_id', string='Melon Order Lines')


    def _create_invoices(self, grouped=False, final=False):
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        for invoice in invoices:
            customer = invoice.partner_id
            if customer.l10n_id_pkp and customer.l10n_id_kode_transaksi == '08':
                for line in invoice.invoice_line_ids:
                    line.tax_ids = [(6, 0, [])]
        return invoices
    
    # @api.onchange('pricelist_id', 'pricelist_id_2')
    # def _onchange_pricelists(self):
    #     if self.pricelist_id and self.pricelist_id_2:
    #         for line in self.order_line:
    #             price1 = self._get_pricelist_price(self.pricelist_id, line)
    #             price2 = self._get_pricelist_price(self.pricelist_id_2, line)

    #             if price1 is not None and price2 is not None:
    #                 line.price_unit = (price1 + price2) / 2
    # def _get_pricelist_price(self, pricelist, line):
    #     product = line.product_id
    #     qty = line.product_uom_qty
    #     partner = self.partner_id
    #     date = self.date_order or fields.Date.today()
    #     result = pricelist._compute_price_rule(
    #         [(product, qty, partner)],
    #         date=date,
    #         uom_id=product.uom_id.id,
    #     )
    #     product_price = result.get(product.id)
    #     if product_price:
    #         return product_price[0]
    #     return None

    @api.onchange('route_id')
    def onchange_route(self):
        if self.route_id:
            for line in self.order_line:
                line.route_id = self.route_id.id
        else:
            for line in self.order_line:
                line.route_id = False


    def action_generate_order_lines(self):
        for order in self:
            if not order.sale_order_line_melon_ids:
                continue
            rounding_diff = 0.0
            for product in order.sale_order_line_melon_ids.product_id:
                order.order_line.filtered(lambda l: l.product_id == l.product_id).unlink()
                
                melon_lines = order.sale_order_line_melon_ids.filtered(lambda m: m.product_id == product)
                # Jumlahkan total berat dan harga (price Total)
                total_weight_gram = sum(melon_lines.mapped('total_weight'))
                # total_weight_kg = total_weight_gram / 1000.0
                total_weight_kg = total_weight_gram
                subtotal = sum(m.price_subtotal for m in melon_lines)

                if total_weight_kg <= 0:
                    raise UserError("Total berat melon harus lebih dari 0.")

                # Untuk Hitung harga per /kg
                price_unit_kg = subtotal / total_weight_kg
                price_unit_kg_rounded = round(price_unit_kg, 2)

                # Untuk Hitung selisih pembulatan
                calculated_total = round(price_unit_kg_rounded * total_weight_kg, 2)
                rounding_diff += round(subtotal - calculated_total, 2)


                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'route_id': order.route_id.id,
                    'product_id': product.id,
                    'product_uom_qty': total_weight_kg,
                    # 'product_uom': product.uom_id.id,
                    'product_uom': self.env['uom.uom'].search([('name','=','g'),('category_id','=',product.uom_id.category_id.id)]).id,
                    'price_unit': price_unit_kg_rounded,
                    'name': product.name,
                })

            rounding_product = self.env['product.product'].search([('name', '=', 'Selisih Rounding')], limit=1)
            if abs(rounding_diff) >= 0.01:
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': rounding_product.id,
                    'product_uom_qty': 1,
                    'product_uom': rounding_product.uom_id.id,
                    'price_unit': rounding_diff,
                    'name': 'Selisih Rounding',
                })
                # order.message_post(body=f"Order Line Melon digenerate. Harga/kg: {price_unit_kg_rounded}, Rounding: {rounding_diff}")

class SaleOrderLineMelon(models.Model):
    _name = 'sale.order.line.melon'
    _description = 'Sale Order Line Melon'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity', required=True, default=0.0)
    total_weight = fields.Float(string='Total Weight (g)', required=True)
    weight = fields.Float(compute='_compute_avg_weight', string='Avg. Weight (g)', 
        required=True, digits=0, 
        readonly=True, store=True)
    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)
    
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', 
        store=True)

    @api.depends('total_weight', 'product_qty')
    def _compute_avg_weight(self):
        for line in self:
            if line.product_qty:
                line.weight = line.total_weight / line.product_qty
            else:
                line.weight = 0.0

    @api.depends('product_id', 'weight', 'sale_order_id.pricelist_id')
    def _compute_price_unit(self):
        for line in self:
            price = 0.0
            pricelist = line.sale_order_id.pricelist_id
            if pricelist and pricelist.is_melon:
                domain = [
                    ('pricelist_id', '=', pricelist.id),
                    ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                    ('weight_from', '<=', line.weight),
                    ('weight_to', '>=', line.weight),
                ]
                matched_item = self.env['product.pricelist.item'].search(domain, limit=1)

                if matched_item:
                    price = matched_item.fixed_price or 0.0
            line.price_unit = price

    @api.depends('product_qty', 'weight')
    def _compute_price_subtotal(self):
            for line in self:
                line.price_subtotal = line.product_qty * line.price_unit