# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    varieties_id = fields.Many2one('plant.varieties', string='ORG')

    def _print_report(self, data):
        if self.env.context.get('xlsx'):
            data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move', 'varieties_id'])[0])
            data['form']['used_context'].update({'is_pnl': self.account_report_id.name=='Profit and Loss'})
            if self.varieties_id:
                data['form']['used_context'].update({'varieties_id': self.varieties_id.id})
            return self.env.ref('ny_account_report1.action_report_financial_xlsx').report_action(self, data=data, config=False)
        else:
            return super()._print_report(data)