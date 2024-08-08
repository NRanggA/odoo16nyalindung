from odoo import fields, models, api, _

class Contract(models.Model):
    _inherit = 'hr.contract'

    wage_id = fields.Many2one('hr.contract.wage', string='Wage Type')