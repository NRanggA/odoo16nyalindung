from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pytz import timezone
import pytz




class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # def action_approve(self):
    #     # Cek jika permintaan cuti dalam status yang valid untuk persetujuan
    #     if any(holiday.state != 'confirm' for holiday in self):
    #         raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

    #     current_employee = self.env.user.employee_id
    #     # Mengatur status dan approver pertama jika validasi tipe cuti adalah 'both'
    #     self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})

    #     # Post a second message, more verbose than the tracking message
    #     for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
    #         user_tz = timezone(holiday.tz)
    #         utc_tz = pytz.utc.localize(holiday.date_from).astimezone(user_tz)
    #         holiday.message_post(
    #             body=_(
    #                 'Your %(leave_type)s planned on %(date)s has been accepted',
    #                 leave_type=holiday.holiday_status_id.display_name,
    #                 date=utc_tz.replace(tzinfo=None)
    #             ),
    #             partner_ids=holiday.employee_id.user_id.partner_id.ids)

    #     # Update attendance records based on the leave type
    #     for holiday in self:
    #         if holiday.holiday_status_id.attendance_type_id:
    #             # Cari absensi yang relevan di model hr.attendance.sheet
    #             attendance_sheets = self.env['hr.attendance.sheet'].search([
    #                 ('employee_id', '=', holiday.employee_id.id),
    #                 ('date', '>=', holiday.date_from.date()),
    #                 ('date', '<=', holiday.date_to.date())
    #             ])
                
    #             # Validasi jika tidak ada absensi untuk tanggal yang dimasukkan
    #             # if not attendance_sheets:
    #             #     raise UserError(_('No attendance records found for the selected dates. Please ensure the dates are correct and attendance records exist.'))

    #             # Update field type_id pada hr.attendance.sheet
    #             attendance_sheets.write({'type_id': holiday.holiday_status_id.attendance_type_id.id})

    #     # Validasi cuti jika tidak memerlukan proses persetujuan ganda
    #     self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
    #     if not self.env.context.get('leave_fast_create'):
    #         self.activity_update()
    #     return True
    

    
    def action_approve(self):
        # Panggil fungsi asli terlebih dahulu
        res = super(HrLeave, self).action_approve()

        # Logika tambahan untuk mengupdate attendance sheet
        for holiday in self:
            print(f"=== Processing holiday for employees {holiday.employee_ids.mapped('name')}")
            if holiday.holiday_status_id.attendance_type_id:
                for employee in holiday.employee_ids:
                    print(f"Checking attendance sheets for employee {employee.name}")
                    # Cari absensi yang relevan di model hr.attendance.sheet
                    attendance_sheets = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', employee.id),
                        ('date', '>=', holiday.date_from.date()),
                        ('date', '<=', holiday.date_to.date())
                    ])
                    
                    print(f"=== Found {len(attendance_sheets)} attendance sheets for employee {employee.name} for dates {holiday.date_from.date()} to {holiday.date_to.date()}")

                    # Update field type_id pada hr.attendance.sheet
                    if attendance_sheets:
                        attendance_sheets.write({'type_id': holiday.holiday_status_id.attendance_type_id.id})
                        print(f"==== Updated type_id for attendance sheets for employee {employee.name}")

        return res