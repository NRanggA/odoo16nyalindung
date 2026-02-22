from odoo import models, fields

class hr_employee_type(models.Model):
    _inherit           = 'hr.employee.type'

    payroll_sequence = fields.Integer(default=5)

class HrPayslipGroup(models.Model):
    _name = 'hr.payslip.group'
    _description = 'Payslip Group'

    name = fields.Char(string='Group', required=True)
    sequence = fields.Integer(default=5)

class Employee(models.Model):
    _inherit = 'hr.employee'

    blok_tanam_id = fields.Many2one('lhm.plant.block', string='Blok Tanam', groups="hr.group_hr_user")
    payslip_group_id = fields.Many2one('hr.payslip.group', string='Payslip Group')

class EmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    payslip_group_id = fields.Many2one('hr.payslip.group', string='Payslip Group')