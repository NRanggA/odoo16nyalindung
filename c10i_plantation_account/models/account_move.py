from odoo import api, fields, models, _, tools

class AccountMove(models.Model):
    _inherit = "account.move"
    
    operating_unit_id = fields.Many2one('operating.unit', string='Operation Unit', check_company=True)