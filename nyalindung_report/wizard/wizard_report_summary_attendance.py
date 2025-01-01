from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardReportSummaryAttendance(models.TransientModel):
    _name           = 'wizard.report.summary.attendance'
    _description    = 'Wizard Report Summary Attendance'
    
    from_date           = fields.Date('From Date')
    to_date             = fields.Date('To Date')
    kemandoran_id       = fields.Many2many("hr.foreman", string="Kemandoran", ondelete="restrict", tracking=True)


    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Summary Attendance !"))

        return self.env.ref('nyalindung_report.action_summary_attendance_report_xlsx').report_action(self)