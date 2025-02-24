from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardReportDetailReceipt(models.TransientModel):
    _name           = 'wizard.report.detail.receipt'
    _description    = 'Wizard Report Detail Receipt'
    
    from_date               = fields.Date('From Date')
    to_date                 = fields.Date('To Date')
    picking_type_id         = fields.Many2one("stock.picking.type", string="Operation Type", ondelete="restrict", required=True, default=1)
    with_accounting_journal = fields.Boolean(string="With Accounting Journal")

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Detail Receipt !"))

        return self.env.ref('c10i_stock.action_report_detail_receipt_xlsx').report_action(self)