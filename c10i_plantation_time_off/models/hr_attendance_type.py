from odoo import models, fields, api, _

class HrAttendanceType(models.Model):
    _inherit = 'hr.attendance.type'

    leave_type_id   = fields.Many2one('hr.leave.type', string="Time off type")
