from odoo import models, fields, api, _

class AttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    is_data_from_my_daya = fields.Boolean(compute='_compute_mydaya_att', store=True, string='Data From My Daya Apps')
    att_log_ids = fields.One2many('ny.attendance.log', 'attendance_sheet_id', string='MyDaya Attendance')

    @api.depends('att_log_ids')
    def _compute_mydaya_att(self):
        for rec in self:
            rec.is_data_from_my_daya = True if rec.att_log_ids else False

    def update_sheet_from_log(self):
        self.ensure_one()
        if self.att_log_ids:
            check_in = check_out = False
            for tt in self.att_log_ids.sorted(key=lambda x: x.waktu):
                if not check_in:
                    check_in = tt.waktu
                    continue
                # elif check_in > tt.waktu:
                #     check_in = tt.waktu
                
                if not check_out and check_in:
                    check_out = tt.waktu
                elif check_out < tt.waktu:
                    check_out = tt.waktu
                
            self.write({'check_in': check_in, 'check_out': check_out})
            # TODO: update attendance to KJ
            if check_in and check_out:
                type_id = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1).id
                self.type_id = type_id
        check_out