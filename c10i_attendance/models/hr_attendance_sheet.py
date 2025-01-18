from odoo import models, fields, api, _
import logging

from datetime import datetime, time
import pytz
from pytz import timezone, utc

_logger = logging.getLogger(__name__)

class HrAttendanceSheet(models.Model):
    _name = 'hr.attendance.sheet'
    _description = 'Attendance Sheet'
    _rec_name = 'date'
    _order = 'date desc'

    employee_id  = fields.Many2one('hr.employee', string='Karyawan', ondelete="cascade", required=True)
    check_in     = fields.Datetime('Check-In')
    check_out    = fields.Datetime('Check-Out')
    type_id 	 = fields.Many2one('hr.attendance.type', string='Tipe Absensi', ondelete="cascade")
    date         = fields.Date('Tanggal')
    is_holiday = fields.Boolean(default=False)

    # Menambahkan boolean untuk menandakan ini dikoreksi atau engga
    is_correction = fields.Boolean('is_correction', default=False)

    @api.model
    def create_attendance_sheets(self, **kwargs):
        
        attendance_type_m = self.env['hr.attendance.type'].search([('code', '=', 'M')], limit=1)
        
        if not attendance_type_m:
            _logger.error("Tipe absensi dengan kode 'M' tidak ditemukan.")
            return False

        employees   = self.env['hr.employee'].search([])
        jakarta     = timezone('Asia/Jakarta')
        today_date  = utc.localize(fields.Datetime.now()).astimezone(jakarta)
        # today_date = fields.Date.context_today(self)

        if kwargs.get("force_date"):
            today_date = fields.Date.from_string(kwargs['force_date'])
        
        attendance_sheets_to_create = []

        for employee in employees:
            calendar        = employee.resource_calendar_id
            start_dt        = timezone(calendar.tz).localize(datetime.combine(today_date, time.min))
            end_dt          = timezone(calendar.tz).localize(datetime.combine(today_date, time.max))
            real_attendance = calendar._attendance_intervals_batch(start_dt, end_dt, employee.resource_id)[employee.resource_id.id] \
                     - calendar._leave_intervals_batch(start_dt, end_dt, None)[False]
            
            if real_attendance:
                schedule_start = schedule_end = False
                for start, stop, rca in real_attendance:
                    if not schedule_start or schedule_start > start:
                        schedule_start = start
                    if not schedule_end or schedule_end < stop:
                        schedule_end = stop
                if schedule_start:
                    schedule_start = schedule_start.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
                if schedule_end:
                    schedule_end = schedule_end.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            
            existing_sheet = self.env['hr.attendance.sheet'].search([
                ('employee_id', '=', employee.id),
                ('date', '=', today_date)
            ], limit=1)

            if not existing_sheet:
                vals = {
                    'employee_id': employee.id,
                    'type_id': attendance_type_m.id,
                    'date': today_date,
                    'is_holiday': False if real_attendance else True,
                }
                attendance_sheets_to_create.append(vals)

        if attendance_sheets_to_create:
            self.env['hr.attendance.sheet'].create(attendance_sheets_to_create)
        return True
    
    # @api.model
    # def _convert_to_utc(self, dt):
    #     """Konversi waktu dari Asia/Jakarta ke UTC sebelum disimpan"""
    #     if dt:
    #         local_tz = timezone('Asia/Jakarta')
    #         local_dt = local_tz.localize(dt, is_dst=None)
    #         return local_dt.astimezone(utc).replace(tzinfo=None)
    #     return dt
    
    # @api.model
    # def create(self, vals):
    #     if 'check_in' in vals:
    #         vals['check_in'] = self._convert_to_utc(fields.Datetime.from_string(vals['check_in']))
    #     if 'check_out' in vals:
    #         vals['check_out'] = self._convert_to_utc(fields.Datetime.from_string(vals['check_out']))
    #     return super(HrAttendanceSheet, self).create(vals)

    # def write(self, vals):
    #     if 'check_in' in vals:
    #         vals['check_in'] = self._convert_to_utc(fields.Datetime.from_string(vals['check_in']))
    #     if 'check_out' in vals:
    #         vals['check_out'] = self._convert_to_utc(fields.Datetime.from_string(vals['check_out']))
    #     return super(HrAttendanceSheet, self).write(vals)