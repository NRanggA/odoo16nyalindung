from odoo import models, fields, api, _

from geopy.distance import geodesic as GD

class AttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    is_data_from_my_daya = fields.Boolean(compute='_compute_mydaya_att', store=True, string='Data From My Daya Apps')
    att_log_ids = fields.One2many('ny.attendance.log', 'attendance_sheet_id', string='MyDaya Attendance')
    longitude_in = fields.Float()
    latitude_in = fields.Float()
    distance_in = fields.Float(compute='_compute_distance', store=True)
    longitude_out = fields.Float()
    latitude_out = fields.Float()
    distance_out = fields.Float(compute='_compute_distance', store=True)

    @api.depends('att_log_ids')
    def _compute_mydaya_att(self):
        for rec in self:
            rec.is_data_from_my_daya = True if rec.att_log_ids else False
    
    @api.depends('employee_id.company_id.company_latitude','employee_id.company_id.company_longitude',
        'latitude_in', 'longitude_in', 'latitude_out', 'longitude_out')
    def _compute_distance(self):
        for rec in self:
            if not rec.employee_id.company_id.company_latitude or not rec.employee_id.company_id.company_longitude:
                rec.distance_in = 0.0
                rec.distance_out = 0.0
            else:
                if not rec.latitude_in or not rec.longitude_in: 
                    rec.distance_in = 0.0
                else:
                    company_position =(rec.employee_id.company_id.company_latitude, rec.employee_id.company_id.company_longitude)
                    att_position =(rec.latitude_in, rec.longitude_in)
                    rec.distance_in = GD(company_position, att_position).km
                
                if not rec.latitude_out or not rec.longitude_out: 
                    rec.distance_out = 0.0
                else:
                    company_position =(rec.employee_id.company_id.company_latitude, rec.employee_id.company_id.company_longitude)
                    att_position =(rec.latitude_out, rec.longitude_out)
                    rec.distance_out = GD(company_position, att_position).km

    def update_sheet_from_log(self):
        self.ensure_one()
        if self.att_log_ids:
            check_in = check_out = False
            lat_in = lat_out = long_in = long_out = False
            for tt in self.att_log_ids.sorted(key=lambda x: x.waktu):
                if not check_in:
                    check_in = tt.waktu
                    lat_in = float(tt.latitude)
                    long_in = float(tt.longitude)
                    continue
                
                if not check_out and check_in:
                    check_out = tt.waktu
                    lat_out = float(tt.latitude)
                    long_out = float(tt.longitude)
                elif check_out < tt.waktu:
                    check_out = tt.waktu
                    lat_out = float(tt.latitude)
                    long_out = float(tt.longitude)
                
            self.write({'check_in': check_in, 
                'latitude_in': lat_in, 'longitude_in': long_in,
                'check_out': check_out,
                'latitude_out': lat_out, 'longitude_out': long_out,
                })
            if check_in and check_out:
                type_id = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1).id
                self.type_id = type_id
        check_out