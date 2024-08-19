from odoo import fields, models, api, _


class HrContractWageType(models.Model):
    _name           = 'hr.contract.wage.type'
    _description    = 'Employee Salary Wage Type'

    name = fields.Char('Name', required=True)
    