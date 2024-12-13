# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    def _print_report(self, data):
        print(":::::::::::::::::::::::::", self.env.context)
        if self.env.context.get('xlsx'):
            data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
            return self.env.ref('ny_account_report1.action_report_financial_xlsx').report_action(self, data=data, config=False)
        else:
            return super()._print_report(data)