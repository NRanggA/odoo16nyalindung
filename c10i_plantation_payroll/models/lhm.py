# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class LhmTransactionLine(models.Model):
    _inherit = 'lhm.transaction.line'

    payslip_id = fields.Many2one('hr.payslip', string='Payslip')