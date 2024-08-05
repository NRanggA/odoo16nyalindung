from odoo import fields, models, api, _

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    attendance_type_id = fields.Many2one('hr.attendance.type', string="Tipe Absensi",  default=lambda self: self.env.context.get('default_attendance_type_id'))


    @api.model
    def create(self, vals):
        record = super(HrLeaveType, self).create(vals)
        if record.attendance_type_id:
            record.attendance_type_id.leave_type_id = record
        return record