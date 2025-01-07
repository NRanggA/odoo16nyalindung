from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pytz import timezone
import pytz
from datetime import datetime

from odoo.exceptions import UserError, ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    error_message   = fields.Text('Error Message')

    def action_approve(self):
        # Panggil fungsi asli terlebih dahulu
        res = super(HrLeave, self).action_approve()
        # Default attendance type jika ada
        default_attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'M')], limit=1)
        # Tanggal hari ini
        now = datetime.now()
        # Mengambil zona waktu indonesia (WIB)
        timezone = pytz.timezone("Asia/Jakarta")
        # Konversi ke waktu indonesia sekarang
        indonesia_timzone = now.astimezone(timezone)
        # Mengambil tanggalnya saja
        today = indonesia_timzone.date()

        error_message_list = []
        # Logika tambahan untuk mengupdate attendance sheet
        for holiday in self:
            if holiday.holiday_status_id.attendance_type_id:
                for employee in holiday.employee_ids:

                    lhm_datas = self.env['lhm.transaction.line'].search([
                        ('employee_id', '=', employee.id),
                        ('date', '>=', holiday.request_date_from),
                        ('date', '<=', holiday.request_date_to)
                    ])

                    if lhm_datas:
                        for lhm in lhm_datas:
                            error_message_list.append(f"Employee dengan nama {employee.name} - {employee.no_induk} sudah memiliki transaksi pada LHM {lhm.lhm_id.name} di tanggal {lhm.lhm_id.date}")

                    # Cari absensi yang relevan di model hr.attendance.sheet dalam range tanggal cuti yang baru
                    attendance_sheets_in_range = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', employee.id),
                        ('date', '>=', holiday.date_from.date()),
                        ('date', '<=', holiday.date_to.date())
                    ])
                    # Update field type_id pada hr.attendance.sheet dalam range tanggal cuti yang baru
                    if attendance_sheets_in_range:
                        attendance_sheets_in_range.write({'type_id': holiday.holiday_status_id.attendance_type_id.id})
                    # Cari absensi pada tanggal hari ini jika berada di luar rentang tanggal cuti yang baru
                    if today < holiday.date_from.date() or today > holiday.date_to.date():
                        attendance_sheet_today = self.env['hr.attendance.sheet'].search([
                            ('employee_id', '=', employee.id),
                            ('date', '=', today)
                        ])
                        # Update field type_id pada hr.attendance.sheet pada tanggal hari ini ke default
                        if default_attendance_type and attendance_sheet_today:
                            attendance_sheet_today.write({'type_id': default_attendance_type.id})

        if error_message_list:
            error_message = '\n'.join(error_message_list)
            self.error_message = error_message
            raise ValidationError(_("Data gagal dengan error berikut:\n%s") % error_message)

        return res
    