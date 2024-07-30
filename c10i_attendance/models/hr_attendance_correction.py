from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class HrAttendanceCorrection(models.Model):
    _name           = 'hr.attendance.correction'
    _description    = 'Attendance Correction'

    name            = fields.Char('Name', readonly=True)
    date            = fields.Date('Tanggal', required=True)
    kemandoran_id   = fields.Many2one('hr.foreman', string="Kemandoran", required=True)
    date_attendance = fields.Date('Tanggal Absensi', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('aprrove', 'Approve'),
        ('reject', 'Reject'),
        ('cancel', 'Cancel'),
        ('draft', 'Set to draft')
    ], string='state', default="new")
    line_ids = fields.One2many('hr.attendance.correction.line', 'correction_id', string="Correction Lines")
    
    def button_approve(self):
        for rec in self:
            rec.state = 'approve'

    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'
    
    def button_reject(self):
        for rec in self:
            rec.state = 'reject'

    def button_cancel(self):
        for rec in self:
            rec.state = 'cancel'
    
    def request_approval(self):
        print(f"==== Sending Request Aprroval ====")

    @api.onchange('date_attendance', 'kemandoran_id')
    def _onchange_date_attendance_kemandoran(self):
        if self.date_attendance and self.kemandoran_id:
            # Cari absensi dari hr.attendance.sheet berdasarkan tanggal absensi
            attendance_records = self.env['hr.attendance.sheet'].search([
                ('date', '=', self.date_attendance),
                ('employee_id', 'in', self.kemandoran_id.employee_ids.ids)
            ])
            
            print("Attendance Records: %s", attendance_records)

            # Filter absensi berdasarkan tipe absensi M
            filtered_records = attendance_records.filtered(
                lambda rec: rec.type_id.code == 'M'
            )
            print("Filtered Attendance Records: %s", filtered_records)

            # Kosongkan line sebelumnya
            self.line_ids = [(5, 0, 0)]

            # Tambahkan line baru berdasarkan filtered_records
            self.line_ids = [(0, 0, {
                'employee_id': rec.employee_id.id,
                'attendance_sheet_id': rec.id,
                'check_in': rec.check_in,
                'check_out': rec.check_out,
            }) for rec in filtered_records]
        else:
            # Kosongkan line jika kondisi tidak terpenuhi
            print("==== DATA KOSONG ====")
            self.line_ids = [(5, 0, 0)]

        # if self.date_attendance and self.kemandoran_id:
        #     # Mencari batch absensi berdasarkan tanggal absensi
        #     attendance_batches = self.env['hr.attendance.batch'].search([
        #         ('date', '=', self.date_attendance)
        #     ])
        #     print("Attendance Batches : %s", attendance_batches)
        #     if not attendance_batches:
        #             raise ValidationError("Tanggal absensi yang Anda masukkan tidak ada dalam daftar batch absensi.")

        #     # Mengumpulkan attendance_ids dari batch yang ditemukan
        #     attendance_records = self.env['hr.attendance.sheet']
        #     for batch in attendance_batches:
        #         attendance_records |= batch.attendance_sheet_ids
            
        #     print("Attendance Records: %s", attendance_records)

        #     # Menyaring attendance_records berdasarkan employee_ids di kemandoran_id
        #     filtered_records = attendance_records.filtered(
        #         # lambda rec: rec.employee_id in self.kemandoran_id.employee_ids
        #         lambda rec: rec.employee_id in self.kemandoran_id.employee_ids and rec.type_id.code == 'M'
        #     )
        #     print("Memfilter Attendance Records: %s", filtered_records)

        #     # Kosongkan line sebelumnya
        #     self.line_ids = [(5, 0, 0)]

        #     # Tambahkan line baru berdasarkan filtered_records
        #     self.line_ids = [(0, 0, {
        #         'employee_id': rec.employee_id.id,
        #         'attendance_sheet_id': rec.id,
        #         'check_in': rec.check_in,  
        #         'check_out': rec.check_out,
        #     }) for rec in filtered_records]
        # else:
        #     # Kosongkan line jika kondisi tidak terpenuhi
        #     print("==== DATA KOSONG ====")
        #     self.line_ids = [(5, 0, 0)]

    @api.model
    def create(self, vals):
        if 'name' not in vals or not vals.get('name'):
            # Mendapatkan sequence number
            sequence = self.env['ir.sequence'].next_by_code('hr.attendance.correction') or '001'
            # Mendapatkan tahun dan format tanggal
            now = datetime.now()
            year_suffix = now.strftime('%y')  # 2 digit terakhir tahun
            date_str = now.strftime('%m%d')   # Bulan dan tanggal
            vals['name'] = f"ATC/{year_suffix}/{date_str}/{sequence}"
        return super(HrAttendanceCorrection, self).create(vals)


class HrAttendanceCorrectionLine(models.Model):
    _name = 'hr.attendance.correction.line'
    _description = 'Attendance Correction Line'

    correction_id           = fields.Many2one('hr.attendance.correction', string="Correction", ondelete='cascade')
    employee_id             = fields.Many2one('hr.employee', string="Employee", required=True)
    nik                     = fields.Char(related='employee_id.no_induk', string="Nik")
    attendance_sheet_id     = fields.Many2one('hr.attendance.sheet', string="Attendance")
    attendance_type         = fields.Many2one(related='attendance_sheet_id.type_id', string="Tipe Absensi")
    check_in                = fields.Datetime(string='Check In')
    check_out               = fields.Datetime(string='Check Out')
    reason                  = fields.Char('Alasan Koreksi')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for line in self:
            if line.employee_id and line.correction_id.date_attendance:
                # Cari data absensi berdasarkan employee_id dan date_attendance
                attendance_record = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', line.employee_id.id),
                    ('date', '=', line.correction_id.date_attendance)
                ], limit=1)
                
                if attendance_record:
                    # Jika ditemukan, set field yang sesuai
                    line.attendance_sheet_id = attendance_record.id
                else:
                    # Jika tidak ditemukan, kosongkan field terkait
                    raise ValidationError("Tanggal absensi yang Anda masukkan tidak ada dalam daftar batch absensi.")

    @api.model
    def create(self, vals):
        record = super(HrAttendanceCorrectionLine, self).create(vals)
        if record.attendance_sheet_id:
            # Hanya perbarui type_id jika check_in dan check_out ada
            if record.check_in and record.check_out:
                attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
                record.attendance_sheet_id.write({
                    'check_in': record.check_in,
                    'check_out': record.check_out,
                    'type_id': attendance_type.id
                })
            else:
                record.attendance_sheet_id.write({
                    'check_in': record.check_in,
                    'check_out': record.check_out
                })
        return record

    def write(self, vals):
        res = super(HrAttendanceCorrectionLine, self).write(vals)
        for record in self:
            if 'check_in' in vals or 'check_out' in vals:
                if record.attendance_sheet_id:
                    # Hanya perbarui type_id jika check_in dan check_out ada
                    if record.check_in and record.check_out:
                        attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
                        record.attendance_sheet_id.write({
                            'check_in': record.check_in,
                            'check_out': record.check_out,
                            'type_id': attendance_type.id
                        })
                    else:
                        record.attendance_sheet_id.write({
                            'check_in': record.check_in,
                            'check_out': record.check_out
                        })
        return res