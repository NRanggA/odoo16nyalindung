from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    account_credit_balance_id = fields.Many2one(
        'account.account',
        string='Credit Balance Account',
        help='Account used for credit balance operations.'
    )