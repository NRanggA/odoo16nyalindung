# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class NyPremiPenyadapGrade(models.Model):
    _name = 'ny.premi.penyadap.grade'
    _description = 'Grade Premi Penyadap'

    name = fields.Char('Grade')
    rate = fields.Float()