# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountFinancialReport(models.Model):
    _inherit = "account.financial.report"

    type = fields.Selection(selection_add=[('code','Code start with')])
    account_code = fields.Char('Account Code')