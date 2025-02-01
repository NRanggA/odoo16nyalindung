# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAgedTrialBalance(models.TransientModel):
    _inherit = "account.aged.trial.balance"

    account_ids = fields.Many2many('account.account', 'aged_tb_account_rel', string='Accounts')

    def _print_report(self, data):
        if self.env.context.get('xlsx'):
            data = self._get_report_data(data)
            if self.account_ids:
                data['form']['used_context'].update({'account_ids': self.account_ids.ids})
            return self.env.ref('ny_account_report1.action_report_aged_partner_balance_xlsx').report_action(self, data=data)
        else:
            return super()._print_report(data)
