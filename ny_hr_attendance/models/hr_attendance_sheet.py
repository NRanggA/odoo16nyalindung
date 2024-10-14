from odoo import models, fields, api, _

class AttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    is_data_from_my_daya = fields.Boolean('Data From My Daya Apps')
    att_log_ids = fields.One2many('ny.attendance.log', 'attendance_sheet_id', string='MyDaya Attendance')

    def update_sheet_from_log(self):
        self.ensure_one()
        if self.att_log_ids:
            check_in = check_out = False
            for tt in self.att_log_ids:
                if not check_in:
                    check_in = tt.waktu
                elif check_in > tt.waktu:
                    check_in = tt.waktu
                
                if not check_out:
                    check_out = tt.waktu
                elif check_out < tt.waktu:
                    check_out = tt.waktu
                
            self.write({'check_in': check_in, 'check_out': check_out})
            # TODO: update attendance to KJ
            # if check_in and check_out:
            #     type_id = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1).id
            #     self.type_id = type_id
        check_out