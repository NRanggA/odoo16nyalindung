from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import base64
import io
import pandas as pd
import pytz
import json
import numpy as np


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in = fields.Datetime(string='Check In', required=False, default=False)


    @api.constrains('employee_id', 'check_in', 'check_out')
    def _check_validity(self):
        """Override the default check to allow creating attendance records
        even if the employee has not checked out from the previous record."""
        for attendance in self:
            # Jika ada check-in dan tidak ada check-out, lakukan pengecekan
            if attendance.check_in and not attendance.check_out:
                existing_attendance = self.search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '!=', False),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], limit=1)
                if existing_attendance:
                    continue
    
    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                continue

class HrAttendanceBatch(models.Model):
    _name           = 'hr.attendance.batch'
    _description    = 'Model Attendance Batch'
    _rec_name       = 'date'

    date                    = fields.Date(string='Tanggal', required=True, default=lambda self: fields.Date.context_today(self))
    file                    = fields.Binary(string='Upload File', attachment=True, required=True)
    attendance_ids          = fields.Many2many('hr.attendance', string='Absensi')
    attendance_sheet_ids    = fields.Many2many('hr.attendance.sheet', string='Attendance Sheet')
    attendance_data         = fields.Text(string='Attendance Data')  
    state                   = fields.Selection([
                                ('draft', 'Draft'),
                                ('processed', 'Processed'),
                                ('valid', 'Valid'),
                            ], string='Status', default="draft")
                            

    def action_show_sheet(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Sheets',
            'res_model': 'hr.attendance.sheet',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', self.attendance_sheet_ids.ids)],
        }

    def do_import(self):
        def cell_to_string(cell_value):
            if cell_value and (isinstance(cell_value, (float, np.floating)) or isinstance(cell_value, (int, np.integer))):
                return str(int(cell_value)) if not np.isnan(cell_value) else ''
            else:
                return cell_value.strip()
        
        if not self.file:
            raise UserError(_("Upload File Terlebih Dahulu"))
        
        data = base64.b64decode(self.file)
        excel_file = io.BytesIO(data)

        df = pd.read_excel(excel_file, header=0)

        indonesia_tz = pytz.timezone('Asia/Jakarta')
        date_str = self.date.strftime('%Y-%m-%d')

        attendance_ids = []
        attendance_data = []
        employees_with_full_attendance  = []

        # Periksa apakah ada record batch lain dengan tanggal yang sama
        existing_batch = self.search([('date', '=', self.date), ('id', '!=', self.id)], limit=1)

        if existing_batch:
            existing_batch.unlink()

            # Mengumpulkan data check-in dan check-out dari file Excel
        for index, row in df.iterrows():
            employee = self.env['hr.employee'].search([('no_induk', '=', cell_to_string(row['Nik'])), ('name', '=', row['Nama'])], limit=1)                
            if not employee:
                raise ValidationError(f"Karyawan dengan nip {row['Nik']} tidak ditemukan!")

            try:
                check_in_str = None
                if not pd.isna(row['Check-in']):
                    check_in            = pd.to_datetime(row['Check-in'])
                    check_in_localized  = indonesia_tz.localize(check_in)
                    check_in_utc        = check_in_localized.astimezone(pytz.utc)
                    check_in_str        = check_in_utc.strftime('%Y-%m-%d %H:%M:%S')

                    # Validasi apakah tanggal check-in di Excel sama dengan tanggal input di form
                    excel_check_in_date_str  = check_in_localized.strftime('%Y-%m-%d')
                    # if check_in_utc.date!=self.date:
                    if excel_check_in_date_str  != date_str:
                        raise ValidationError(f"Tanggal Check-in pada Excel ({excel_check_in_date_str}) tidak sesuai dengan tanggal yang diinput ({date_str}).")

                check_out_str = None
                if not pd.isna(row['Check-out']):
                    check_out           = pd.to_datetime(row['Check-out'])
                    check_out_localized = indonesia_tz.localize(check_out)
                    check_out_utc       = check_out_localized.astimezone(pytz.utc)
                    check_out_str       = check_out_utc.strftime('%Y-%m-%d %H:%M:%S')

                    # Validasi apakah tanggal check-out di Excel sama dengan tanggal input di form
                    excel_check_out_date_str = check_out_localized.strftime('%Y-%m-%d')
                    if excel_check_out_date_str != date_str:
                        raise ValidationError(f"Tanggal Check-out pada Excel ({excel_check_out_date_str}) tidak sesuai dengan tanggal yang diinput ({date_str}).")

            except ValueError as e:
                raise ValueError(f"Kesalahan format tanggal: {e}")
            query = """select ha.id from hr_attendance ha, hr_employee he where 
                ha.employee_id=he.id
                and he.no_induk = '%(nik)s'
                and ((extract(day from (check_in::timestamp at time zone 'UTC') at time zone 'Asia/Jakarta')=%(day)s
                    and extract(month from (check_in::timestamp at time zone 'UTC') at time zone 'Asia/Jakarta')=%(month)s
                    and extract(year from (check_in::timestamp at time zone 'UTC') at time zone 'Asia/Jakarta')=%(year)s)
                    or 
                    (extract(day from (check_out::timestamp at time zone 'UTC') at time zone 'Asia/Jakarta')=%(day)s
                    and extract(month from (check_out::timestamp at time zone 'UTC') at time zone 'Asia/Jakarta')=%(month)s
                    and extract(year from (check_out::timestamp at time zone 'UTC') at time zone 'Asia/Jakarta')=%(year)s))"""
            if check_in_str:
                self.env.cr.execute(query%({'nik': employee.no_induk, 'day': self.date.day, 'month': self.date.month, 'year': self.date.year}))
                res_query = self.env.cr.fetchone()
                if res_query:
                    existing_att_id = res_query[0]
                    existing_att_obj = self.env['hr.attendance'].browse(existing_att_id)
                    vals_to_update = {}
                    if not existing_att_obj.check_in:
                        vals_to_update.update({'check_in': check_in_str})
                    if check_out_str:
                        vals_to_update.update({'check_out': check_out_str})
                    if vals_to_update:
                        existing_att_obj.write(vals_to_update)
                else:
                    vals_to_create = {
                        'employee_id': employee.id,
                        'check_in': check_in_str
                    }
                    if check_out_str:
                        vals_to_create.update({'check_out': check_out_str})
                    existing_att_id = self.env['hr.attendance'].create(vals_to_create).id
                attendance_ids.append(existing_att_id)
            elif check_out_str:
                self.env.cr.execute(query%({'nik': employee.no_induk, 'day': self.date.day, 'month': self.date.month, 'year': self.date.year}))
                res_query = self.env.cr.fetchone()
                if res_query:
                    existing_att_id = res_query[0]
                    self.env['hr.attendance'].browse(existing_att_id).write({'check_out': check_out_str})
                else:
                    vals_to_create = {
                        'employee_id': employee.id,
                        'check_out': check_out_str
                    }
                    existing_att_id = self.env['hr.attendance'].create(vals_to_create).id
                attendance_ids.append(existing_att_id)
            
            # Tentukan kode jenis absensi
            attendance_type_code = 'KJ' if check_out_str else 'M'
            attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

            if not attendance_type:
                continue

            # Buat data absensi baru jika belum ada
            attendance_data.append({
                'employee_id': employee.id,
                'type_id': attendance_type.id,
                'date': date_str,
            })

        # Validasi karyawan yang sudah check-in dan check-out di tanggal yang sama
        # if employees_with_full_attendance:
        #     names_list = ", ".join(employees_with_full_attendance)
        #     raise ValidationError(f"Karyawan berikut sudah check-in dan check-out di tanggal yang sama: {names_list}.")
        self.attendance_ids = [(6, 0, attendance_ids)]
        self.attendance_data = json.dumps(attendance_data)
        return True

    def push_to_sheet(self):
        attendance_sheets = []
        attendance_data = json.loads(self.attendance_data)


        for attendance, data in zip(self.attendance_ids, attendance_data):
            employee_id = data.get('employee_id')
            date    = data.get('date')

            # Tentukan jenis kehadiran berdasarkan kehadiran Check-in dan Check-out
            if attendance.check_in and attendance.check_out:
                type_id = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1).id
            else:
                type_id = self.env['hr.attendance.type'].search([('code', '=', 'M')], limit=1).id

            # Periksa Sheet Attendance yang ada dengan karyawan dan tanggal check-in yang sama
            existing_attendance_sheet = self.env['hr.attendance.sheet'].search([
                ('employee_id', '=', employee_id),
                ('date', '=', date)
            ], limit=1)

            if existing_attendance_sheet:
                # Update data yang sudah di buat oleh cron
                existing_attendance_sheet.write({
                    'type_id': type_id,
                    'check_in': attendance.check_in,
                    'check_out': attendance.check_out 
                })
                attendance_sheets.append(existing_attendance_sheet.id)
            else:
                employee = self.env['hr.employee'].search([('id', '=', employee_id)], limit=1)
                raise ValidationError(f"Data absensi untuk user {employee.name} pada tanggal {date} belum dibuat di dalam Sheet Absensi.")
        
        self.write({'state': 'processed'})
        self.attendance_sheet_ids = [(6, 0, attendance_sheets)]
        return True

    def action_confirm(self):
        self.state = 'valid'

    def set_to_draft(self):
        self.state = 'draft'