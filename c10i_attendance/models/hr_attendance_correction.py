from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
from pytz import timezone, utc


class HrAttendanceCorrection(models.Model):
    _name           = 'hr.attendance.correction'
    _description    = 'Attendance Correction'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name            = fields.Char('Name', readonly=True)
    date            = fields.Date('Tanggal', required=True, default=lambda self: fields.Date.context_today(self))
    date_attendance = fields.Date('Tanggal Absensi', required=True)
    attendance_type_id = fields.Many2one('hr.attendance.type', string='Tipe Absensi')
    state = fields.Selection([
        ('draft', 'New'),
        ('progres', 'Waiting Approval'),
        ('review', 'Review'),
        ('cancel', 'Cancel'),
        ('reject', 'Reject'),
        ('approve', 'Approve'),
    ], string='state', default="draft")
    line_ids = fields.One2many('hr.attendance.correction.line', 'correction_id', string="Correction Lines")
    

    def button_approve(self):
        for record in self:
            for line in record.line_ids:
                if line.attendance_sheet_id:
                    # Perbarui hanya jika check_in dan check_out ada
                    if line.check_in and line.check_out:
                        attendance_type_kj = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)
                        line.attendance_sheet_id.write({
                            'check_in': line.check_in,
                            'check_out': line.check_out,
                            'type_id': attendance_type_kj.id,
                            'is_correction': line.correction
                        })
                    else:
                        attendance_type_m = self.env['hr.attendance.type'].search([('code', '=', 'M')], limit=1)
                        line.attendance_sheet_id.write({
                            'check_in': line.check_in,
                            'check_out': line.check_out,
                            'type_id': attendance_type_m.id,
                            'is_correction': line.correction

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

    def button_review(self):
        for rec in self:
            rec.state = 'review'

    # def button_done(self):
    #     for rec in self:
    #         rec.state = 'done'
    
    def _delete_false_corrections(self):
        for line in self.line_ids:
            if not line.correction:
                line.unlink()

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
        record = super(HrAttendanceCorrection, self).create(vals)
        record._delete_false_corrections()
        return record

    def write(self, vals):
        res = super(HrAttendanceCorrection, self).write(vals)
        self._delete_false_corrections()
        return res

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
    correction              = fields.Boolean('Koreksi', default=False)

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

    # @api.onchange('check_in', 'check_out')
    # def _onchange_check_in_check_out(self):
    #     for line in self:
    #         if line.correction_id and line.correction_id.date_attendance:
    #             date_attendance = line.correction_id.date_attendance
    #             if line.check_in and line.check_in.date() < date_attendance:
    #                 raise ValidationError(f"Tanggal Checkin tidak boleh sebelum tanggal absensi : {date_attendance}")
    #             if line.check_out and line.check_out.date() > date_attendance:
    #                 raise ValidationError(f"Tanggal Checkout tidak boleh sebelum tanggal absensi : {date_attendance}")

    @api.onchange('check_in', 'check_out')
    def _onchange_check_in_check_out(self):
        for line in self:
            if line.correction_id and line.correction_id.date_attendance:
                date_attendance = line.correction_id.date_attendance
                jakarta         = timezone('Asia/Jakarta')
                if line.check_in:
                    # Localize check_in waktu UTC ke Asia/Jakarta
                    check_in_utc    = fields.Datetime.from_string(line.check_in)
                    check_in_local  = utc.localize(check_in_utc).astimezone(jakarta)
                    if check_in_local.date() < date_attendance:
                        raise ValidationError(f"Tanggal 'Check-In' tidak boleh sebelum tanggal absensi: {date_attendance}")
                    if check_in_local.date() > date_attendance:
                        raise ValidationError(f"Tanggal 'Check-In' tidak boleh sesudah tanggal absensi: {date_attendance}")

                if line.check_out:
                    # Mengonversi check_out ke waktu lokal Asia/Jakarta menggunakan localize
                    check_out_utc = fields.Datetime.from_string(line.check_out)
                    check_out_local = utc.localize(check_out_utc).astimezone(jakarta)
                    if check_out_local.date() > date_attendance:
                        raise ValidationError(f"Tanggal 'Check-Out' tidak boleh sesudah tanggal absensi: {date_attendance}")
                    if check_out_local.date() < date_attendance:
                        raise ValidationError(f"Tanggal 'Check-Out' tidak boleh sebelum tanggal absensi: {date_attendance}")