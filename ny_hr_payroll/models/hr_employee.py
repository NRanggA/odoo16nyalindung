from odoo import models, fields

class hr_employee_type(models.Model):
    _inherit           = 'hr.employee.type'

    payroll_sequence = fields.Integer(default=5)
    

class Employee(models.Model):
    _inherit = 'hr.employee'

    blok_tanam_id = fields.Many2one('lhm.plant.block', string='Blok Tanam', groups="hr.group_hr_user")