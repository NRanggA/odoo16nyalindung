# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class c10i_hr_16(models.Model):
#     _name = 'c10i_hr_16.c10i_hr_16'
#     _description = 'c10i_hr_16.c10i_hr_16'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
