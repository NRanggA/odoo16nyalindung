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
        ('draft', 'New'),
        ('done', 'Approve'),
        ('close', 'close')
    ], string='state', default="draft")
    line_ids = fields.One2many('hr.attendance.correction.line', 'correction_id', string="Correction Lines")
    
    @api.constrains('date_attendance')
    def _check_date_attendance(self):
        for record in self:
            if record.date_attendance:
                attendance_batches = self.env['hr.attendance.batch'].search([
                    ('date', '=', record.date_attendance)
                ])
                if not attendance_batches:
                    raise ValidationError("Tanggal absensi yang Anda masukkan tidak ada dalam daftar batch absensi.")


    # @api.depends('date_attendance', 'kemandoran_id')
    # def _compute_employee_attendance(self):
    #     for record in self:

    #         if record.date_attendance and record.kemandoran_id:
    #             # Mencari batch absensi berdasarkan tanggal absensi
    #             attendance_batches = self.env['hr.attendance.batch'].search([
    #                 ('date', '=', record.date_attendance)
    #             ])
    #             print("Attendance Batches:", attendance_batches)

    #             # Mengumpulkan attendance_ids dari batch yang ditemukan
    #             attendance_records = self.env['hr.attendance.sheet']
    #             for batch in attendance_batches:
    #                 attendance_records |= batch.attendance_sheet_ids

    #             print("Attendance Records Before Filtering:", attendance_records)

    #             # filter attendance_records berdasarkan employee_ids di kemandoran_id
    #             filtered_records = attendance_records.filtered(
    #                 lambda rec: rec.employee_id in record.kemandoran_id.employee_ids and rec.type_id.code == 'M'
    #                 # lambda rec: rec.employee_id in record.kemandoran_id.employee_ids
    #             )

    #             print("Filtered Attendance Records:", filtered_records)

    #             # Kosongkan line sebelumnya
    #             record.line_ids = [(5, 0, 0)]

    #             # Tambahkan line baru berdasarkan filtered_records
    #             record.line_ids = [(0, 0, {
    #                 'employee_id': rec.employee_id.id,
    #                 'attendance_sheet_id': rec.id,
    #             }) for rec in filtered_records]
    #         else:
    #             # Kosongkan line jika kondisi tidak terpenuhi
    #             record.line_ids = [(5, 0, 0)]
    
    @api.onchange('date_attendance', 'kemandoran_id')
    def _onchange_date_attendance_kemandoran(self):
        
        if self.date_attendance and self.kemandoran_id:
            # Mencari batch absensi berdasarkan tanggal absensi
            attendance_batches = self.env['hr.attendance.batch'].search([
                ('date', '=', self.date_attendance)
            ])
            print("Attendance Batches : %s", attendance_batches)

            # Mengumpulkan attendance_ids dari batch yang ditemukan
            attendance_records = self.env['hr.attendance.sheet']
            for batch in attendance_batches:
                attendance_records |= batch.attendance_sheet_ids
            
            print("Attendance Records: %s", attendance_records)

            # Menyaring attendance_records berdasarkan employee_ids di kemandoran_id
            filtered_records = attendance_records.filtered(
                # lambda rec: rec.employee_id in self.kemandoran_id.employee_ids
                lambda rec: rec.employee_id in self.kemandoran_id.employee_ids and rec.type_id.code == 'M'
            )
            print("Memfilter Attendance Records: %s", filtered_records)

            # Kosongkan line sebelumnya
            self.line_ids = [(5, 0, 0)]

            # Tambahkan line baru berdasarkan filtered_records
            self.line_ids = [(0, 0, {
                'employee_id': rec.employee_id.id,
                'attendance_sheet_id': rec.id,
                'check_in' : filtered_records.check_in,
                'check_out' : filtered_records.check_out,
            }) for rec in filtered_records]
        else:
            # Kosongkan line jika kondisi tidak terpenuhi
            self.line_ids = [(5, 0, 0)]

    @api.model
    def create(self, vals):
        # Mendapatkan tahun saat ini
        year = datetime.now().year
        # Membuat sequence
        if 'name' not in vals or not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.attendance.correction') or '/'
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
        attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
        if record.attendance_sheet_id:
            record.attendance_sheet_id.write({
                'check_in': record.check_in,
                'check_out': record.check_out,
                'type_id' : attendance_type.id
            })
        return record

    def write(self, vals):
        res = super(HrAttendanceCorrectionLine, self).write(vals)
        attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
        for record in self:
            if 'check_in' in vals or 'check_out' in vals:
                if record.attendance_sheet_id:
                    record.attendance_sheet_id.write({
                        'check_in': record.check_in,
                        'check_out': record.check_out,
                        'type_id' : attendance_type.id
                    })
        return res