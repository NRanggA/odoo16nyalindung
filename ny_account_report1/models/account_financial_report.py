# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountFinancialReport(models.Model):
    _inherit = "account.financial.report"

    fna_type = fields.Selection([('bs','Balance Sheet'),('pnl','Profit and Loss')], string='Report Type')
    type = fields.Selection(selection_add=[('code','Code start with'),('domain','Domain Formula')])
    account_code = fields.Char('Account Code')
    domain = fields.Char('Domain Formula', help="Example. [('account_id.code','=','100000'),('parent_state','=','posted')]")