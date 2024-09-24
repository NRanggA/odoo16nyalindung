# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrContract(models.Model):
    _inherit = 'hr.contract'

    base_amount_bpjs_kes = fields.Float('Dasar Pengali BPJS Kesehatan')
    base_amount_bpjs_tk = fields.Float('Dasar Pengali BPJS Jamsostek')