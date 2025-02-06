from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    payroll_bill_account_id = fields.Many2one('account.account', string='Payroll Bill Account')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payroll_bill_account_id = fields.Many2one('account.account', related='company_id.payroll_bill_account_id', readonly=False)