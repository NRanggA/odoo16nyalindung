from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    lat_acuan = fields.Char()
    long_acuan = fields.Char()
    value_jarak = fields.Char()