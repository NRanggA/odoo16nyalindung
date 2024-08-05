from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    quantity = fields.Float(string="Quantity")
    
class ProductPricelistCostumer(models.Model):
    _inherit = 'product.pricelist'

    partner_id = fields.Many2one('res.partner', string='Costumer')