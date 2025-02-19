from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardReportStoreIssue(models.TransientModel):
    _name = 'wizard.report.store.issue'
    _descipton = 'Wizard Report Store Issue'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    operation_type_id = fields.Many2one('stock.picking.type', string='Operation Type', required=True)
    with_journal = fields.Boolean('With Accounting Journal', default=False)

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Mutasi !"))
        
        # print(f"===== AKAN =====")
        return self.env.ref('c10i_stock.action_store_issue_report_xlsx').report_action(self)