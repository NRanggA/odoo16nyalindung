from odoo import models, fields, api, _
import pytz
from pytz import timezone, utc

class NyAttendanceLog(models.Model):
    _name = 'ny.attendance.log'
    _description = 'My Daya Attendance Log'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    longitude = fields.Char()
    latitude = fields.Char()
    waktu = fields.Datetime() # 2024-09-19 14:53:53 
    # version = fields.Char()
    foto = fields.Binary(attachment=True)
    keterangan = fields.Text()
    statusmasuk = fields.Char() # WFO// isi dengan WFO,WFH

    attendance_sheet_id = fields.Many2one('hr.attendance.sheet', ondelete='restrict', string='Attendance Sheet')

    def find_attendance_sheet(self):
        for rec in self:
            jakarta = timezone('Asia/Jakarta')
            new_date= rec.waktu.astimezone(utc).astimezone(jakarta)
            att_found = self.env['hr.attendance.sheet'].search([('employee_id','=',rec.employee_id.id),
                                            ('date','=',new_date.date())])
            if att_found:
                rec.attendance_sheet_id = att_found.id
                att_found.update_sheet_from_log()