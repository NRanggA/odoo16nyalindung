# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrPKP(models.Model):
    _name = 'hr.pkp'
    _description = 'Standar Pajak Progresif Pendapatan Kena Pajak'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char('Name', required=True)
    range_start = fields.Float('From')
    range_stop = fields.Float('To')
    percentage = fields.Float('% Tax', required=True)
    active = fields.Boolean('Active', required=True, default=True)