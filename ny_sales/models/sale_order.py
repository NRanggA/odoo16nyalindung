from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pricelist_id_2 = fields.Many2one('product.pricelist', string='Grade')

#     @api.onchange('pricelist_id', 'pricelist_id_2')
#     def _onchange_pricelists(self):
#         if self.pricelist_id and self.pricelist_id_2:
#             for line in self.order_line:
#                 price1 = self._get_pricelist_price(self.pricelist_id, line)
#                 price2 = self._get_pricelist_price(self.pricelist_id_2, line)

#                 if price1 is not None and price2 is not None:
#                     line.price_unit = (price1 + price2) / 2

#     def _get_pricelist_price(self, pricelist, line):
#         product = line.product_id
#         qty = line.product_uom_qty
#         partner = self.partner_id
#         date = self.date_order or fields.Date.today()
#         result = pricelist._compute_price_rule(
#             [(product, qty, partner)],
#             date=date,
#             uom_id=product.uom_id.id,
#         )
#         product_price = result.get(product.id)
#         if product_price:
#             return product_price[0]
#         return None




# from odoo import models, fields, api

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     pricelist_id_2 = fields.Many2one('product.pricelist', string='Grade')

#     @api.onchange('pricelist_id', 'pricelist_id_2')
#     def _onchange_pricelists(self):
#         if self.pricelist_id and self.pricelist_id_2:
#             for line in self.order_line:
#                 price1 = line.product_id.with_context(pricelist=self.pricelist_id.id).price
#                 price2 = line.product_id.with_context(pricelist=self.pricelist_id_2.id).price
#                 line.price_unit = (price1 + price2) / 2