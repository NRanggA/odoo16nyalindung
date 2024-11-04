from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class HrAttendanceCorrection(models.Model):
    _inherit           = 'hr.attendance.correction'

    kemandoran_id   = fields.Many2one('hr.foreman', string="Kemandoran", required=True)

    @api.onchange('attendance_type_id' ,'date_attendance', 'kemandoran_id')
    def _onchange_date_attendance_kemandoran(self):
        if self.date_attendance and self.kemandoran_id:
            # Cari absensi dari hr.attendance.sheet berdasarkan tanggal absensi
            # attendance_records = self.env['hr.attendance.sheet'].search([
            #     ('date', '=', self.date_attendance),
            #     ('employee_id', 'in', self.kemandoran_id.employee_ids.ids),
            #     '|',
            #     '&',
            #     ('check_in', '!=', False),  
            #     ('check_out', '=', False),  
            #     '&',
            #     ('check_in', '=', False),   
            #     ('check_out', '!=', False) 
            # ])

            # Filter absensi berdasarkan tipe absensi M
            # filtered_records = attendance_records.filtered(
            #     lambda rec: rec.type_id == self.attendance_type_id.id
            # )

            attendance_records = self.env['hr.attendance.sheet'].search([
                ('date', '=', self.date_attendance),
                ('employee_id', 'in', self.kemandoran_id.employee_ids.ids),
                ('type_id', '=', self.attendance_type_id.id),
            ])
            
            if not attendance_records:
                raise ValidationError(f"Tidak ada employee pada kemandoran {self.kemandoran_id.name} di dalam Sheet Absensi dengan tipe absensi {self.attendance_type_id.code}")

            # Kosongkan line sebelumnya
            self.line_ids = [(5, 0, 0)]

            # Tambahkan line baru berdasarkan filtered_records
            self.line_ids = [(0, 0, {
                'employee_id': rec.employee_id.id,
                'attendance_sheet_id': rec.id,
                'check_in': rec.check_in,
                'check_out': rec.check_out,
            }) for rec in attendance_records]
        else:
            # Kosongkan line jika kondisi tidak terpenuhi
            self.line_ids = [(5, 0, 0)]
