from odoo import models, fields, api, _

class AttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    is_data_from_my_daya = fields.Boolean('Data From My Daya Apps')