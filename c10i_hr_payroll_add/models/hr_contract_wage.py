from odoo import fields, models, api, _


class HrContractWage(models.Model):
    _name           = 'hr.contract.wage'
    _description    = 'Employee Salary Wage'

    name = fields.Char('Name', required=True)
    