from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardGeneralLedgerXlsx(models.Model):
    _name  = 'wizard.general.ledger.xlsx'
    _description = 'Wizard General Ledger Excell'

    from_date       = fields.Date('From Date', required=True)
    to_date         = fields.Date('To Date', required=True)
    journal_ids = fields.Many2many('account.journal', string='Journals')
    account_ids = fields.Many2many('account.account', string='Accounts')
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan !"))
        # print(f"====== Report akan digenenrate ======")
        return self.env.ref('ny_account_report1.action_general_ledger_xlsx').report_action(self)