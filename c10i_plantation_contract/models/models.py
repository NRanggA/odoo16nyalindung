# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class c10i_plantation_contract(models.Model):
#     _name = 'c10i_plantation_contract.c10i_plantation_contract'
#     _description = 'c10i_plantation_contract.c10i_plantation_contract'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
