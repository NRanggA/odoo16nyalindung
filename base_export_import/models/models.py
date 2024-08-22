# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class bpdpks_export_import(models.Model):
#     _name = 'bpdpks_export_import.bpdpks_export_import'
#     _description = 'bpdpks_export_import.bpdpks_export_import'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
