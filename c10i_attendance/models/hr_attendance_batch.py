from odoo import models, fields, api
import base64
import io
import pandas as pd
import pytz
import json

import logging

_logger = logging.getLogger(__name__)

class HrAttendanceBatch(models.Model):
    _name = 'hr.attendance.batch'
    _description = 'Model Attendance Batch'

    date                    = fields.Date(string='Tanggal', required=True)
    file                    = fields.Binary(string='Upload File', attachment=True, required=True)
    attendance_ids          = fields.Many2many('hr.attendance', string='Absensi')
    attendance_sheet_ids    = fields.Many2many('hr.attendance.sheet', string='Attendance Sheet')
    attendance_data         = fields.Text(string='Attendance Data')  # Temporary storage for additional data

    def do_import(self):
        data = base64.b64decode(self.file)
        excel_file = io.BytesIO(data)

        df = pd.read_excel(excel_file, header=0)

        indonesia_tz = pytz.timezone('Asia/Jakarta')

        attendance_records = []
        attendance_data = []
        for index, row in df.iterrows():
            employee = self.env['hr.employee'].search([('name', '=', row['Nama'])], limit=1)
            attendance_type = self.env['hr.attendance.type'].search([('code', '=', row['Tipe Absensi'])], limit=1)

            if employee and attendance_type:
                try:
                    check_in = pd.to_datetime(row['Check-in'])
                    check_out = pd.to_datetime(row['Check-out'])

                    check_in = indonesia_tz.localize(check_in)
                    check_out = indonesia_tz.localize(check_out)

                    check_in = check_in.astimezone(pytz.utc)
                    check_out = check_out.astimezone(pytz.utc)

                    check_in_str = check_in.strftime('%Y-%m-%d %H:%M:%S')
                    check_out_str = check_out.strftime('%Y-%m-%d %H:%M:%S')

                except ValueError as e:
                    raise ValueError(f"Error in date format: {e}")

                existing_attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id)
                ], limit=1)

                if existing_attendance:
                    existing_attendance.write({
                        'check_in': check_in_str,
                        'check_out': check_out_str,
                    })
                    attendance_records.append(existing_attendance.id) 
                else:
                    new_attendance = self.env['hr.attendance'].create({
                        'employee_id': employee.id,
                        'check_in': check_in_str,
                        'check_out': check_out_str,
                    })
                    attendance_records.append(new_attendance.id) 

                attendance_data.append({
                    'employee_id': employee.id,
                    'type_id': attendance_type.id,
                })

        self.attendance_ids = [(6, 0, attendance_records)]

        self.attendance_data = json.dumps(attendance_data)

        return True

    def action_confirm(self):
        _logger.info('=== Starting action_confirm function')
        attendance_sheets = []
        attendance_data = json.loads(self.attendance_data)

        for attendance, data in zip(self.attendance_ids, attendance_data):
            employee_id = data.get('employee_id')
            type_id = data.get('type_id')

            if not employee_id or not type_id:
                _logger.warning(f"==== Invalid employee_id ({employee_id}) or type_id ({type_id})")
                continue

            if not self.env['hr.employee'].browse(employee_id).exists():
                _logger.error(f"==== Employee with ID {employee_id} does not exist")
                continue

            if not self.env['hr.attendance.type'].browse(type_id).exists():
                _logger.error(f"==== Attendance type with ID {type_id} does not exist")
                continue

            existing_attendance_sheet = self.env['hr.attendance.sheet'].search([
                ('employee_id', '=', employee_id),
            ], limit=1)

            if existing_attendance_sheet:
                existing_attendance_sheet.write({
                    'type_id': type_id,
                    'date': self.date,
                })
                attendance_sheets.append(existing_attendance_sheet.id)
            else:
                new_attendance_sheet = self.env['hr.attendance.sheet'].create({
                    'employee_id': employee_id,
                    'date': self.date,
                    'type_id': type_id,
                })
                attendance_sheets.append(new_attendance_sheet.id)

        self.attendance_sheet_ids = [(6, 0, attendance_sheets)]
        return True

