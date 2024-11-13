from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class HrAttendanceCorrection(models.Model):
    _name           = 'hr.attendance.correction'
    _description    = 'Attendance Correction'

    name            = fields.Char('Name', readonly=True)
    date            = fields.Date('Tanggal', required=True, default=lambda self: fields.Date.context_today(self))
    date_attendance = fields.Date('Tanggal Absensi', required=True)
    attendance_type_id = fields.Many2one('hr.attendance.type', string='Tipe Absensi')
    state = fields.Selection([
        ('draft', 'New'),
        ('progres', 'Progres'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('cancel', 'Cancel'),
        ('done', 'Done'),
    ], string='state', default="draft")
    line_ids = fields.One2many('hr.attendance.correction.line', 'correction_id', string="Correction Lines")
    
    def button_approve(self):
        for record in self:
            for line in record.line_ids:
                if line.attendance_sheet_id:
                    # Hanya perbarui type_id jika check_in dan check_out ada
                    if line.check_in and line.check_out:
                        attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
                        line.attendance_sheet_id.write({
                            'check_in': line.check_in,
                            'check_out': line.check_out,
                            'type_id': attendance_type.id,
                            'is_correction': True
                        })
                    else:
                        line.attendance_sheet_id.write({
                            'check_in': line.check_in,
                            'check_out': line.check_out
                        })
            record.state = 'approve'

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
        for rec in self:
            rec.state = 'progres'

    def button_done(self):
        for rec in self:
            rec.state = 'done'

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

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError("Data tidak dapat dihapus. Untuk menghapus, set status menjadi Draft terlebih dahulu.")
        return super(HrAttendanceCorrection, self).unlink()


class HrAttendanceCorrectionLine(models.Model):
    _name = 'hr.attendance.correction.line'
    _description = 'Attendance Correction Line'

    correction_id           = fields.Many2one('hr.attendance.correction', string="Correction", ondelete='cascade')
    employee_id             = fields.Many2one('hr.employee', string="Employee", required=True)
    nik                     = fields.Char(related='employee_id.no_induk', string="Nik")
    attendance_sheet_id     = fields.Many2one('hr.attendance.sheet', string="Attendance Sheet")
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

    # @api.model
    # def create(self, vals):
    #     record = super(HrAttendanceCorrectionLine, self).create(vals)
    #     if record.attendance_sheet_id:
    #         # Hanya perbarui type_id jika check_in dan check_out ada
    #         if record.check_in and record.check_out:
    #             attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
    #             record.attendance_sheet_id.write({
    #                 'check_in': record.check_in,
    #                 'check_out': record.check_out,
    #                 'type_id': attendance_type.id
    #             })
    #         else:
    #             record.attendance_sheet_id.write({
    #                 'check_in': record.check_in,
    #                 'check_out': record.check_out
    #             })
    #     return record

    # def write(self, vals):
    #     res = super(HrAttendanceCorrectionLine, self).write(vals)
    #     for record in self:
    #         if 'check_in' in vals or 'check_out' in vals:
    #             if record.attendance_sheet_id:
    #                 # Hanya perbarui type_id jika check_in dan check_out ada
    #                 if record.check_in and record.check_out:
    #                     attendance_type = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
    #                     record.attendance_sheet_id.write({
    #                         'check_in': record.check_in,
    #                         'check_out': record.check_out,
    #                         'type_id': attendance_type.id
    #                     })
    #                 else:
    #                     record.attendance_sheet_id.write({
    #                         'check_in': record.check_in,
    #                         'check_out': record.check_out
    #                     })
    #     return res