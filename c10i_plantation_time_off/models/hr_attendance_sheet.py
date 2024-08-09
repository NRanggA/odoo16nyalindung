from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HrAttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    # fungsi asli ditaro di bawah
    @api.model
    def create_attendance_sheets(self, **kwargs):
        # Logika tambahan sebelum memanggil fungsi asli
        employees = self.env['hr.employee'].search([])
        today_date = fields.Date.context_today(self)

        if kwargs.get("force_date"):
            today_date = kwargs['force_date']
        
        for employee in employees:
            leave = self.env['hr.leave'].search([
                ('employee_ids', 'in', employee.id),
                ('date_from', '<=', today_date),
                ('date_to', '>=', today_date),
                ('state', '=', 'validate')
            ], limit=1)

            if leave:
                _logger.info(f"Employee {employee.name} has a leave from {leave.date_from} to {leave.date_to}")
                attendance_type = leave.holiday_status_id.attendance_type_id
                if attendance_type:
                    existing_sheet = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', employee.id),
                        ('date', '=', today_date)
                    ], limit=1)

                    if existing_sheet:
                        existing_sheet.write({'type_id': attendance_type.id})
                        _logger.info(f"Updated attendance sheet for {employee.name} with type {attendance_type.code}")
                    else:
                        # Membuat lembar kehadiran baru jika belum ada
                        new_sheet = self.env['hr.attendance.sheet'].create({
                            'employee_id': employee.id,
                            'date': today_date,
                            'type_id': attendance_type.id,
                        })
                        _logger.info(f"Created new attendance sheet for {employee.name} with type {attendance_type.code}")

        # Memanggil fungsi asli
        result = super(HrAttendanceSheet, self).create_attendance_sheets(force_date=today_date)

        return result
