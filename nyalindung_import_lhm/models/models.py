# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class nyalindung_import_lhm(models.Model):
#     _name = 'nyalindung_import_lhm.nyalindung_import_lhm'
#     _description = 'nyalindung_import_lhm.nyalindung_import_lhm'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
