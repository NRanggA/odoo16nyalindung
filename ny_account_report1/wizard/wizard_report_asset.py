from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardReportAsset(models.Model):
    _name  = 'wizard.report.asset'
    _description = 'Wizard Report Asset'

    # from_date           = fields.Date('From Date', required=True)
    # to_date             = fields.Date('To Date', required=True)
    date                = fields.Date('Date', required=True)
    asset_category_ids  = fields.Many2many('account.asset.category', string='Asset Categories')
    company_id          = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def create_report(self):
        # if not self.from_date or not self.to_date:
        #     raise UserError(_("Masukkan Tanggal untuk memfilter Laporan !"))
        # print(f"====== Report akan digenenrate ======")
        return self.env.ref('ny_account_report1.action_report_asset').report_action(self)