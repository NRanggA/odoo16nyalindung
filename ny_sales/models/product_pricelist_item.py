from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    quantity = fields.Float(string="Quantity")
    is_grade = fields.Boolean('is_grade')

    # Menambahkan field weight_from dan weight_to untuk menyimpan rentang berat melon
    weight_from = fields.Float(string='Weight From', default=0.0)
    weight_to = fields.Float(string='Weight To', default=0.0)
    

class ProductPricelistCostumer(models.Model):
    _inherit = 'product.pricelist'
    partner_id = fields.Many2one('res.partner', string='Costumer')
    is_grade = fields.Boolean('Grading')


    # untuk menandai apakah ini adalah pricelist melon atau bukan
    is_melon = fields.Boolean('Melon Pricelist', default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running')
    ], string='State', default='draft')

    def button_approve(self):
        for record in self:
            record.write({
                'state' : 'running'
            })