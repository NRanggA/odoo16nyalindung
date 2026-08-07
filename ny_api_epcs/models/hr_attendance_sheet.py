from odoo import models, fields, api, _

class AttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    break_out = fields.Datetime("Break Out")
    break_in = fields.Datetime("Break In")

    overtime_in = fields.Datetime("Overtime In")
    overtime_out = fields.Datetime("Overtime Out")

    def update_sheet_from_log(self):
        self.ensure_one()
        if self.att_log_ids:
            check_in = check_out = break_in = break_out = overtime_in = overtime_out = False
            lat_in = lat_out = long_in = long_out = False
            for tt in self.att_log_ids.sorted(key=lambda x: x.waktu):
                if tt.type in ['break-in','break-out']:
                    if not break_in and tt.type=='break-in':
                        break_in = tt.waktu
                    if not break_out and tt.type=='break-out':
                        break_out = tt.waktu
                elif tt.type in ['overtime-in', 'overtime-out']:
                    if not overtime_in and tt.type=='overtime-in':
                        overtime_in = tt.waktu
                    if not overtime_out and tt.type=='overtime-out':
                        overtime_out = tt.waktu
                else:
                    if not check_in and (not tt.type or tt.type == 'check-in'):
                        check_in = tt.waktu
                        lat_in = float(tt.latitude)
                        long_in = float(tt.longitude)
                        continue
                    
                    if tt.type == 'check-out':
                        check_out = tt.waktu
                        lat_out = float(tt.latitude)
                        long_out = float(tt.longitude)
                    else:
                        if not check_out and check_in:
                            check_out = tt.waktu
                            lat_out = float(tt.latitude)
                            long_out = float(tt.longitude)
                        elif check_out < tt.waktu:
                            check_out = tt.waktu
                            lat_out = float(tt.latitude)
                            long_out = float(tt.longitude)
            self.write({'check_in': check_in, 
                    'latitude_in': lat_in, 
                    'longitude_in': long_in,
                    'check_out': check_out,
                    'latitude_out': lat_out, 
                    'longitude_out': long_out,
                    'break_in': break_in,
                    'break_out': break_out,
                    'overtime_in': overtime_in,
                    'overtime_out': overtime_out,
                })
            if check_in and check_out:
                type_id = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1).id
                self.type_id = type_id

class NyAttendanceLog(models.Model):
    _inherit = 'ny.attendance.log'

    type = fields.Selection([
        ('check-in', 'Check In'),
        ('check-out', 'Check Out'),
        ('break-in', 'Break In'),
        ('break-out', 'Break Out'),
        ('overtime-in', 'Overtime In'),
        ('overtime-out', 'Overtime In')
    ])