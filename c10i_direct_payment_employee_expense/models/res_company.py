from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_advance_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Employee Advance Account",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('internal_type', '=', 'other'), ('reconcile','=',True)",
        help='Please complete the help')