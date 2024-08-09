from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HrAttendanceSheet(models.Model):
    _name = 'hr.attendance.sheet'
    _description = 'Attendance Sheet'
    _rec_name = 'date'

    employee_id  = fields.Many2one('hr.employee', string='Karyawan', ondelete="cascade")
    check_in     = fields.Datetime('Check-In')
    check_out    = fields.Datetime('Check-Out')
    type_id 	 = fields.Many2one('hr.attendance.type', string='Tipe Absensi', ondelete="cascade")
    date         = fields.Date('Tanggal')

    @api.model
    def create_attendance_sheets(self, **kwargs):
        
        attendance_type_m = self.env['hr.attendance.type'].search([('code', '=', 'M')], limit=1)
        
        if not attendance_type_m:
            _logger.error("Tipe absensi dengan kode 'M' tidak ditemukan.")
            return False

        employees = self.env['hr.employee'].search([])
        today_date = fields.Date.context_today(self)

        if kwargs.get("force_date"):
            today_date = kwargs['force_date']
        
        # print("====== DATA hr attendance sheet : {today_date} ", today_date)

        attendance_sheets_to_create = []

        for employee in employees:
            # Check if there's already an attendance sheet for the current date
            existing_sheet = self.env['hr.attendance.sheet'].search([
                ('employee_id', '=', employee.id),
                ('date', '=', today_date)
            ], limit=1)

            if not existing_sheet:
                vals = {
                    'employee_id': employee.id,
                    'type_id': attendance_type_m.id,
                    'date': today_date
                }
                attendance_sheets_to_create.append(vals)

        if attendance_sheets_to_create:
            self.env['hr.attendance.sheet'].create(attendance_sheets_to_create)
            _logger.info(f"=== Created {len(attendance_sheets_to_create)} new attendance sheets for today ({today_date}).")

        return True