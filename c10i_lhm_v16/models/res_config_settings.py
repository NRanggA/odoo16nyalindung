from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    contractor_default_journal_id   = fields.Many2one(comodel_name='account.journal', string="Journal", help='Please complete the help')
    account_payable_contractor_id   = fields.Many2one('account.account', 'Account Payable Perantara Buku Kontraktor')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    contractor_default_journal_id = fields.Many2one(comodel_name='account.journal', related='company_id.contractor_default_journal_id', readonly=False, string="Journal", help='Please complete the help')
    account_payable_contractor_id = fields.Many2one(comodel_name='account.account', related='company_id.account_payable_contractor_id', readonly=False, string="Account Payable Perantara Buku Kontraktor", help='Please complete the help')