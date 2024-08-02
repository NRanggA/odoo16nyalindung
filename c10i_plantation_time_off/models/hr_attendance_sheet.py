from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HrAttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    # Fungsi asli ditaro di atas
    # @api.model
    # def create_attendance_sheets(self):
    #     # Panggil metode asli
    #     super(HrAttendanceSheet, self).create_attendance_sheets()

    #     today_date = fields.Date.context_today(self)
    #     employees_with_leave = self.env['hr.leave'].search([
    #         ('state', '=', 'validate'),
    #         ('date_from', '<=', today_date),
    #         ('date_to', '>=', today_date)
    #     ]).mapped('employee_id')

    #     for employee in employees_with_leave:
    #         leave = self.env['hr.leave'].search([
    #             ('employee_id', '=', employee.id),
    #             ('state', '=', 'validate'),
    #             ('date_from', '<=', today_date),
    #             ('date_to', '>=', today_date)
    #         ], limit=1)

    #         if leave:
    #             attendance_type = leave.holiday_status_id.attendance_type_id
    #             if not attendance_type:
    #                 _logger.error(f"Attendance type tidak ditemukan untuk cuti dengan ID {leave.id}")
    #                 continue

    #             existing_sheet = self.env['hr.attendance.sheet'].search([
    #                 ('employee_id', '=', employee.id),
    #                 ('date', '=', today_date)
    #             ], limit=1)

    #             if existing_sheet:
    #                 existing_sheet.write({'type_id': attendance_type.id})
    #                 _logger.info(f"=== Updated attendance sheet for employee {employee.id} on {today_date} with type {attendance_type.id}")

    #     return True
    

    # fungsi asli ditaro di bawah
    @api.model
    def create_attendance_sheets(self):
        # Logika tambahan sebelum memanggil fungsi asli
        employees = self.env['hr.employee'].search([])
        today_date = fields.Date.context_today(self)

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

        # Memanggil fungsi asli
        result = super(HrAttendanceSheet, self).create_attendance_sheets()

        return result
