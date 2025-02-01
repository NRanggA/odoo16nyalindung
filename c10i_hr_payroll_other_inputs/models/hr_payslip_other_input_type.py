# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrPayslipOtherInputType(models.Model):
    _name = 'hr.payslip.other.input.type'
    _description = 'Payroll Other Input Type'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True)
    active = fields.Boolean(default=True)