from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import io
import pandas as pd
import pytz
import json

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
                                ('valid', 'Valid')
                            ], string='Status', default="draft")

    # def do_import(self):
    #     data = base64.b64decode(self.file)
    #     excel_file = io.BytesIO(data)

    #     df = pd.read_excel(excel_file, header=0)

    #     indonesia_tz = pytz.timezone('Asia/Jakarta')

    #     date_str = self.date.strftime('%Y-%m-%d')

    #     # existing_record = self.search([('date', '=', self.date), ('id', '!=', self.id)], limit=1)

    #     attendance_records              = []
    #     attendance_data                 = []
    #     employees_with_full_attendance  = []

    #     # Mengumpulkan data check-in dan check-out dari file Excel
    #     for index, row in df.iterrows():
    #         employee = self.env['hr.employee'].search([('no_induk', '=', row['Nik']), ('name', '=', row['Nama'])], limit=1)
    #         if not employee:
    #             raise ValidationError(f"Karyawan dengan nip {row['Nik']} tidak ditemukan!")

    #         try:
    #             check_in = pd.to_datetime(row['Check-in'])
    #             check_in_localized = indonesia_tz.localize(check_in)
    #             check_in_utc = check_in_localized.astimezone(pytz.utc)
    #             check_in_str = check_in_utc.strftime('%Y-%m-%d %H:%M:%S')

    #             check_out_str = None
    #             if not pd.isna(row['Check-out']):
    #                 check_out = pd.to_datetime(row['Check-out'])
    #                 check_out = indonesia_tz.localize(check_out)
    #                 check_out = check_out.astimezone(pytz.utc)
    #                 check_out_str = check_out.strftime('%Y-%m-%d %H:%M:%S')

    #         except ValueError as e:
    #             raise ValueError(f"Kesalahan format tanggal: {e}")

    #         # Periksa keberadaan absensi pada tanggal yang sama
    #         existing_attendance = self.env['hr.attendance'].search([
    #             ('employee_id', '=', employee.id),
    #             ('check_in', '>=', check_in_utc.replace(hour=0, minute=0, second=0, microsecond=0)),
    #             ('check_in', '<', check_in_utc.replace(hour=23, minute=59, second=59, microsecond=999999))
    #         ], limit=1)

    #         if existing_attendance:
    #             # Jika ada check-out dalam data impor dan absensi yang ada tidak memiliki check-out, perbarui
    #             if check_out_str:
    #                 if not existing_attendance.check_out:
    #                     existing_attendance.write({'check_out': check_out_str})
    #                     attendance_records.append(existing_attendance.id)
    #                 else:
    #                     # Jika absensi sudah memiliki check-out, tandai sebagai lengkap
    #                     employees_with_full_attendance.append(employee.name)
    #             else:
    #                 # Jika tidak ada check-out dalam data impor, jangan ubah entri ini
    #                 attendance_records.append(existing_attendance.id)
            
    #             attendance_type_code = 'KJ' if check_out_str else 'M'
    #             attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

    #             if attendance_type:
    #                 attendance_data.append({
    #                     'employee_id': employee.id,
    #                     'type_id': attendance_type.id,
    #                     'date': date_str
    #                 })
    #             continue
            
    #         # Tentukan kode jenis absensi
    #         attendance_type_code = 'KJ' if check_out_str else 'M'
    #         attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

    #         if not attendance_type:
    #             continue

    #         # Buat data absensi baru jika belum ada
    #         new_attendance_values = {
    #             'employee_id': employee.id,
    #             'check_in': check_in_str,
    #         }
    #         if check_out_str:
    #             new_attendance_values['check_out'] = check_out_str

    #         new_attendance = self.env['hr.attendance'].create(new_attendance_values)
    #         attendance_records.append(new_attendance.id)

    #         attendance_data.append({
    #             'employee_id': employee.id,
    #             'type_id': attendance_type.id,
    #             'date' :  date_str
    #         })

    #     # Validasi karyawan yang sudah check-in dan check-out di tanggal yang sama
    #     if employees_with_full_attendance:
    #         names_list = ", ".join(employees_with_full_attendance)
    #         raise ValidationError(f"Karyawan berikut sudah check-in dan check-out di tanggal yang sama: {names_list}.")

    #     self.attendance_ids = [(6, 0, attendance_records)]
    #     self.attendance_data = json.dumps(attendance_data)

    #     return True

    def do_import(self):
        data = base64.b64decode(self.file)
        excel_file = io.BytesIO(data)

        df = pd.read_excel(excel_file, header=0)

        indonesia_tz = pytz.timezone('Asia/Jakarta')

        date_str = self.date.strftime('%Y-%m-%d')

        attendance_records = []
        attendance_data = []
        employees_with_full_attendance = []

        # Periksa apakah ada record batch lain dengan tanggal yang sama
        existing_batch = self.search([('date', '=', self.date), ('id', '!=', self.id)], limit=1)

        if existing_batch:
            # Mengumpulkan data check-in dan check-out dari file Excel
            for index, row in df.iterrows():
                employee = self.env['hr.employee'].search([('no_induk', '=', row['Nik']), ('name', '=', row['Nama'])], limit=1)
                if not employee:
                    raise ValidationError(f"Karyawan dengan nip {row['Nik']} tidak ditemukan!")

                try:
                    check_in = pd.to_datetime(row['Check-in'])
                    check_in_localized = indonesia_tz.localize(check_in)
                    check_in_utc = check_in_localized.astimezone(pytz.utc)
                    check_in_str = check_in_utc.strftime('%Y-%m-%d %H:%M:%S')

                    check_out_str = None
                    if not pd.isna(row['Check-out']):
                        check_out = pd.to_datetime(row['Check-out'])
                        check_out = indonesia_tz.localize(check_out)
                        check_out = check_out.astimezone(pytz.utc)
                        check_out_str = check_out.strftime('%Y-%m-%d %H:%M:%S')

                except ValueError as e:
                    raise ValueError(f"Kesalahan format tanggal: {e}")

                # Periksa keberadaan absensi pada tanggal yang sama
                existing_attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', check_in_utc.replace(hour=0, minute=0, second=0, microsecond=0)),
                    ('check_in', '<', check_in_utc.replace(hour=23, minute=59, second=59, microsecond=999999))
                ], limit=1)

                if existing_attendance:
                    # Jika ada check-out dalam data impor dan absensi yang ada tidak memiliki check-out, perbarui
                    if check_out_str:
                        if not existing_attendance.check_out:
                            existing_attendance.write({'check_out': check_out_str})
                            attendance_records.append(existing_attendance.id)
                        else:
                            # Jika absensi sudah memiliki check-out, tandai sebagai lengkap
                            employees_with_full_attendance.append(employee.name)
                    else:
                        # Jika tidak ada check-out dalam data impor, jangan ubah entri ini
                        attendance_records.append(existing_attendance.id)

                    attendance_type_code = 'KJ' if check_out_str else 'M'
                    attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

                    if attendance_type:
                        attendance_data.append({
                            'employee_id': employee.id,
                            'type_id': attendance_type.id,
                            'date': date_str
                        })
                    continue

                # Tentukan kode jenis absensi
                attendance_type_code = 'KJ' if check_out_str else 'M'
                attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

                if not attendance_type:
                    continue

                # Buat data absensi baru jika belum ada
                new_attendance_values = {
                    'employee_id': employee.id,
                    'check_in': check_in_str,
                }
                if check_out_str:
                    new_attendance_values['check_out'] = check_out_str

                new_attendance = self.env['hr.attendance'].create(new_attendance_values)
                attendance_records.append(new_attendance.id)

                attendance_data.append({
                    'employee_id': employee.id,
                    'type_id': attendance_type.id,
                    'date': date_str
                })

            # Validasi karyawan yang sudah check-in dan check-out di tanggal yang sama
            if employees_with_full_attendance:
                names_list = ", ".join(employees_with_full_attendance)
                raise ValidationError(f"Karyawan berikut sudah check-in dan check-out di tanggal yang sama: {names_list}.")

            self.attendance_ids = [(6, 0, attendance_records)]
            self.attendance_data = json.dumps(attendance_data)

            # Menghapus batch setelah update checkout
            existing_batch.unlink()

        else:
            # Jika tidak ada batch lain, buat batch baru dan absensi
            for index, row in df.iterrows():
                employee = self.env['hr.employee'].search([('no_induk', '=', row['Nik']), ('name', '=', row['Nama'])], limit=1)
                if not employee:
                    raise ValidationError(f"Karyawan dengan nip {row['Nik']} tidak ditemukan!")

                try:
                    check_in = pd.to_datetime(row['Check-in'])
                    check_in_localized = indonesia_tz.localize(check_in)
                    check_in_utc = check_in_localized.astimezone(pytz.utc)
                    check_in_str = check_in_utc.strftime('%Y-%m-%d %H:%M:%S')

                    check_out_str = None
                    if not pd.isna(row['Check-out']):
                        check_out = pd.to_datetime(row['Check-out'])
                        check_out = indonesia_tz.localize(check_out)
                        check_out = check_out.astimezone(pytz.utc)
                        check_out_str = check_out.strftime('%Y-%m-%d %H:%M:%S')

                except ValueError as e:
                    raise ValueError(f"Kesalahan format tanggal: {e}")

                # Tentukan kode jenis absensi
                attendance_type_code = 'KJ' if check_out_str else 'M'
                attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

                if not attendance_type:
                    continue

                # Buat data absensi baru
                new_attendance_values = {
                    'employee_id': employee.id,
                    'check_in': check_in_str,
                }
                if check_out_str:
                    new_attendance_values['check_out'] = check_out_str

                new_attendance = self.env['hr.attendance'].create(new_attendance_values)
                attendance_records.append(new_attendance.id)

                attendance_data.append({
                    'employee_id': employee.id,
                    'type_id': attendance_type.id,
                    'date': date_str
                })

            self.attendance_ids = [(6, 0, attendance_records)]
            self.attendance_data = json.dumps(attendance_data)

        return True

    def push_to_sheet(self):
        attendance_sheets = []
        attendance_data = json.loads(self.attendance_data)

        print(f"==== Data Attendance : {attendance_data}")

        for attendance, data in zip(self.attendance_ids, attendance_data):
            employee_id = data.get('employee_id')
            type_id = data.get('type_id')
            date    = data.get('date')

            # Tentukan jenis kehadiran berdasarkan kehadiran Check-in dan Check-out
            if attendance.check_in and attendance.check_out:
                type_id = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1).id

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
                raise ValidationError(f"Data absensi pada tanggal {date} belum dibuat di dalam Sheet Absensi.")

        self.attendance_sheet_ids = [(6, 0, attendance_sheets)]
        return True

    def action_confirm(self):
        self.state = 'valid'

    def set_to_draft(self):
        self.state = 'draft'

    # def do_import(self):
    #     data = base64.b64decode(self.file)
    #     excel_file = io.BytesIO(data)

    #     df = pd.read_excel(excel_file, header=0)

    #     indonesia_tz = pytz.timezone('Asia/Jakarta')

    #     date_str = self.date.strftime('%Y-%m-%d')

    #     existing_record = self.search([('date', '=', self.date), ('id', '!=', self.id)], limit=1)

    #     attendance_records = []
    #     attendance_data = []
    #     employees_with_full_attendance = []

    #     # Periksa apakah ada data absensi pada tanggal yang sama
    #     if existing_record:
    #         for attendance in existing_record.attendance_ids:
    #             if not attendance.check_out:
    #                 # Jika ada data check_out yang kosong, akan diupdate
    #                 for index, row in df.iterrows():
    #                     employee = self.env['hr.employee'].search(
    #                         [('no_induk', '=', row['Nik']), ('name', '=', row['Nama'])], limit=1)
    #                     if not employee:
    #                         raise ValidationError(f"Karyawan dengan nip {row['Nik']} tidak ditemukan!")

    #                     if employee.id == attendance.employee_id.id:
    #                         check_out_str = None
    #                         if not pd.isna(row['Check-out']):
    #                             check_out = pd.to_datetime(row['Check-out'])
    #                             check_out = indonesia_tz.localize(check_out)
    #                             check_out = check_out.astimezone(pytz.utc)
    #                             check_out_str = check_out.strftime('%Y-%m-%d %H:%M:%S')
    #                             attendance.write({'check_out': check_out_str})
    #                             attendance_records.append(attendance.id)
    #                             break
    #             else:
    #                 # Jika semua data lengkap, beri peringatan
    #                 employees_with_full_attendance.append(attendance.employee_id.name)

    #             attendance_type_code = 'KJ' if check_out_str else 'M'
    #             attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

    #             if attendance_type:
    #                 attendance_data.append({
    #                     'employee_id': employee.id,
    #                     'type_id': attendance_type.id,
    #                     'date': date_str
    #                 })
    #             continue

    #         if not attendance_records:
    #             # Semua data sudah lengkap
    #             if employees_with_full_attendance:
    #                 names_list = ", ".join(employees_with_full_attendance)
    #                 raise ValidationError(f"Karyawan berikut sudah check-in dan check-out di tanggal yang sama: {names_list}.")
    #     else:
    #         # Jika tidak ada record untuk tanggal tersebut, buat baru
    #         for index, row in df.iterrows():

    #             employee = self.env['hr.employee'].search(
    #                 [('no_induk', '=', row['Nik']), ('name', '=', row['Nama'])], limit=1)
    #             if not employee:
    #                 raise ValidationError(f"Karyawan dengan nip {row['Nik']} tidak ditemukan!")

    #             try:
    #                 check_in = pd.to_datetime(row['Check-in'])
    #                 check_in_localized = indonesia_tz.localize(check_in)
    #                 check_in_utc = check_in_localized.astimezone(pytz.utc)
    #                 check_in_str = check_in_utc.strftime('%Y-%m-%d %H:%M:%S')

    #                 check_out_str = None
    #                 if not pd.isna(row['Check-out']):
    #                     check_out = pd.to_datetime(row['Check-out'])
    #                     check_out = indonesia_tz.localize(check_out)
    #                     check_out = check_out.astimezone(pytz.utc)
    #                     check_out_str = check_out.strftime('%Y-%m-%d %H:%M:%S')

    #             except ValueError as e:
    #                 raise ValueError(f"Kesalahan format tanggal: {e}")

    #             # Periksa keberadaan absensi pada tanggal yang sama
    #             existing_attendance = self.env['hr.attendance'].search([
    #                 ('employee_id', '=', employee.id),
    #                 ('check_in', '>=', check_in_utc.replace(hour=0, minute=0, second=0, microsecond=0)),
    #                 ('check_in', '<', check_in_utc.replace(hour=23, minute=59, second=59, microsecond=999999))
    #             ], limit=1)

    #             if existing_attendance:
    #                 # Jika ada check-out dalam data impor dan absensi yang ada tidak memiliki check-out, perbarui
    #                 if check_out_str:
    #                     if not existing_attendance.check_out:
    #                         existing_attendance.write({'check_out': check_out_str})
    #                         attendance_records.append(existing_attendance.id)
    #                     else:
    #                         # Jika absensi sudah memiliki check-out, tandai sebagai lengkap
    #                         employees_with_full_attendance.append(employee.name)
    #                 else:
    #                     # Jika tidak ada check-out dalam data impor, jangan ubah entri ini
    #                     attendance_records.append(existing_attendance.id)
    #                 continue

    #             # Tentukan kode jenis absensi
    #             attendance_type_code = 'KJ' if check_out_str else 'M'
    #             attendance_type = self.env['hr.attendance.type'].search([('code', '=', attendance_type_code)], limit=1)

    #             if not attendance_type:
    #                 continue

    #             # Buat data absensi baru jika belum ada
    #             new_attendance_values = {
    #                 'employee_id': employee.id,
    #                 'check_in': check_in_str,
    #             }
    #             if check_out_str:
    #                 new_attendance_values['check_out'] = check_out_str

    #             new_attendance = self.env['hr.attendance'].create(new_attendance_values)
    #             attendance_records.append(new_attendance.id)

    #             attendance_data.append({
    #                 'employee_id': employee.id,
    #                 'type_id': attendance_type.id,
    #                 'date': date_str,
    #             })

    #         # Validasi karyawan yang sudah check-in dan check-out di tanggal yang sama
    #         if employees_with_full_attendance:
    #             names_list = ", ".join(employees_with_full_attendance)
    #             raise ValidationError(f"Karyawan berikut sudah check-in dan check-out di tanggal yang sama: {names_list}.")

    #     self.attendance_ids = [(6, 0, attendance_records)]
    #     self.attendance_data = json.dumps(attendance_data)

    #     return True
