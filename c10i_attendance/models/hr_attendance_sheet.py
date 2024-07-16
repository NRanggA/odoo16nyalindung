from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)

class HrAttendanceSheet(models.Model):
    _name = 'hr.attendance.sheet'
    _description = 'Attendance Sheet'

    employee_id = fields.Many2one('hr.employee', string='Karyawan')
    date 		= fields.Date(string='Tanggal')
    type_id 	= fields.Many2one('hr.attendance.type', string='Tipe Absensi')

    # @api.model
    def update_attendance_type(self):
        attendance_type_m = self.env['hr.attendance.type'].search([('code', '=', 'M')], limit=1)

        if not attendance_type_m:
            _logger.error("Attendance type 'M' tidak ditemukan")
            raise ValueError("Attendance type 'M' tidak ditemukan")

        attendance_sheets = self.search([])

        if not attendance_sheets:
            _logger.info(" attendance sheets Tidak ditemukan")
            return True

        invalid_records = attendance_sheets.filtered(lambda sheet: not sheet.type_id)
        if invalid_records:
            _logger.error(f"Invalid type_id ditemukan di attendance sheets: {invalid_records.ids}")

        valid_records = attendance_sheets.filtered(lambda sheet: sheet.type_id)
        valid_records.write({'type_id': attendance_type_m.id})
        _logger.info(f"Sukses updated type_id untuk {len(valid_records)} baris attendance sheets")

        invalid_records.write({'type_id': attendance_type_m.id})
        _logger.info(f"Gagal update type_id di attendance sheets: {invalid_records.ids}")

        return True
