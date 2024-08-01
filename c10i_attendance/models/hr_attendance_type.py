from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

class hr_attendance_type(models.Model):
    _name           = 'hr.attendance.type'
    _description    = 'Employee Attendance Type'

    name            = fields.Char("Name")
    code            = fields.Char("Code")
    special         = fields.Boolean("Spesial")
    type            = fields.Selection([('in', 'Masuk'), ('out', 'Keluar'), ('na', 'N/A'), ('kj', 'KJ')], string='Type')
    type_hk         = fields.Selection([('hke', 'HKE'), ('hkne', 'HKNE')], string='HK Type')
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active          = fields.Boolean("Active", default=True)
    leave_type_id   = fields.Many2one('hr.leave.type', string="Time off type")

    @api.onchange('special')
    def _onchange_special(self):
        if self.special:
            pass
        else:
            self.type = False

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        hr_attendance_type = self.search(domain + args, limit=limit)
        return hr_attendance_type._name_get()

    def button_time_off(self):
        if self.leave_type_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Time Off Type',
                'res_model': 'hr.leave.type',
                'view_mode': 'form',
                'res_id': self.leave_type_id.id,
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Time Off Type',
                'res_model': 'hr.leave.type',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_attendance_type_id': self.id},
            }