from odoo import models, fields, api
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class SaleOrderLines(models.Model):
    _inherit = 'sale.order.line'
    pricelist_item_id2 = fields.Many2one(
    comodel_name='product.pricelist.item',
    compute='_compute_pricelist_item_id2')

    melon_line_ids = fields.One2many('sale.order.line.melon', 'order_line_id', string='melon')

    qty_butir = fields.Float(string='Qty Butir')

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_pricelist_item_id2(self):
        for line in self:
            if not line.product_id or line.display_type or not line.order_id.pricelist_id_2:
                line.pricelist_item_id2 = False
            else:
                line.pricelist_item_id2 = line.order_id.pricelist_id_2._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )
    
    def _get_pricelist_price(self):
        price = super()._get_pricelist_price()
        # self.ensure_one()
        # self.product_id.ensure_one()

        # pricelist_rule = self.pricelist_item_id
        # order_date = self.order_id.date_order or fields.Date.today()
        # product = self.product_id.with_context(**self._get_product_price_context())
        # qty = self.product_uom_qty or 1.0
        # uom = self.product_uom or self.product_id.uom_id
        # currency = self.currency_id or self.order_id.company_id.currency_id

        # if not pricelist_rule :
        if 'Grade ' in self.product_id.name :
            pricelist_rule = self.pricelist_item_id2
            order_date = self.order_id.date_order or fields.Date.today()
            product = self.product_id.with_context(**self._get_product_price_context())
            qty = self.product_uom_qty or 1.0
            uom = self.product_uom or self.product_id.uom_id
            currency = self.currency_id or self.order_id.company_id.currency_id
            
            price = pricelist_rule._compute_price(
                product, qty, uom, order_date, currency=currency)

        return price
