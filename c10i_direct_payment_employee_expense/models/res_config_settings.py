from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    employee_advance_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.employee_advance_account_id', readonly=False,
        string="Employee Advance Account",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('reconcile','=',True)]",
        help='Please complete the help')
    
    # ('internal_type', '=', 'other'),