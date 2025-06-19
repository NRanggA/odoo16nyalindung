from odoo import models, fields, api
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    approver_pr_id = fields.Many2one('hr.employee', string='Approver PR', help="The employee who approves purchase requests for this employee.")


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    approver_pr_id = fields.Many2one('hr.employee', string='Approver PR', readonly=True)
