from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_latitude = fields.Float(related='company_id.company_latitude', readonly=False)
    company_longitude = fields.Float(related='company_id.company_longitude', readonly=False)
    attendance_radius_distance = fields.Float(related='company_id.attendance_radius_distance', readonly=False)