from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    approver_mr_id = fields.Many2one('hr.employee', string='Approver MR', help="Select the employee who is the approver for material requests.")


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    approver_mr_id = fields.Many2one('hr.employee', string='Approver MR', readonly=True)
