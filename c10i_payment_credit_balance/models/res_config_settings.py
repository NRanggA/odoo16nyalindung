from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_credit_balance_id = fields.Many2one(
        related='company_id.account_credit_balance_id',
        string='Customer Credit Balance Account',
        domain=[('reconcile', '=', True),('deprecated', '=', False)],
        help='Account to use for customer credit balances.',
        readonly=False
    )