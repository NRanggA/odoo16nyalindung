# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class c10i_hr_payroll_add(models.Model):
#     _name = 'c10i_hr_payroll_add.c10i_hr_payroll_add'
#     _description = 'c10i_hr_payroll_add.c10i_hr_payroll_add'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
