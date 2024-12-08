# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def _prepare_liquidity_account_vals(self, company, code, vals):
        res = super(AccountJournal, self)._prepare_liquidity_account_vals(company=company, code=code, vals=vals)
        account_code_prefix = ''
        if res['account_type'] == 'asset_cash':
            account_code_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''
        parent_id = self.env['account.account'].with_context({'show_parent_account': True}).search([
			('code', '=', account_code_prefix),
			('company_id', '=', company.id),
			('account_type', '=', 'view')], limit=1)
        if parent_id:
            res.update({'parent_id': parent_id.id})
        return res
