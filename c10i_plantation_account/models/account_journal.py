from odoo import api, fields, models, _, tools

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    operating_unit_id = fields.Many2one('operating.unit', string='Operation Unit', check_company=True)