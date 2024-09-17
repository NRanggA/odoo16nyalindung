from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    quantity = fields.Float(string="Quantity")
    is_grade = fields.Boolean('is_grade')
    
class ProductPricelistCostumer(models.Model):
    _inherit = 'product.pricelist'
    partner_id = fields.Many2one('res.partner', string='Costumer')
    is_grade = fields.Boolean('is Grade')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running')
    ], string='State', default='draft')

    def button_approve(self):
        for record in self:
            record.write({
                'state' : 'running'
            })