# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrRatePph(models.Model):
    _name = 'hr.rate.pp58'
    _description = 'Tarif Efektif PPH 21 Berdasarkan PP 58 Tahun 2023'

    tier_type = fields.Selection([('tier_a','Tier A'),('tier_b','Tier B'),('tier_c','Tier C')], string='Tier', required=True)
    range_start = fields.Float('Lebih dari')
    range_stop = fields.Float('sampai dengan')
    percentage = fields.Float('% Tax', required=True)