from odoo import models, fields, api, _

class Company(models.Model):
    _inherit = 'res.company'

    company_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    company_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    attendance_radius_distance = fields.Float('Attendance Radius Distance (km)')