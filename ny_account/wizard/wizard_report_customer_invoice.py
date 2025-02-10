from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardReportCustomerInvoiceXlsx(models.Model):
    # _name  = 'wizard.general.ledger.xlsx'
    _name  = 'wizard.report.customer.invoice.xlsx'
    _description = 'Wizard Report Customer Invoice Excel'

    from_date       = fields.Date('From Date', required=True)
    to_date         = fields.Date('To Date', required=True)

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan !"))
        return self.env.ref('ny_account.action_report_customer_invoice_xlsx').report_action(self)