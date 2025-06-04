# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    fna_type = fields.Selection(related='account_report_id.fna_type', store=True)
    pnl_per_org = fields.Boolean(string='P&L per ORG')
    varieties_id = fields.Many2one('plant.varieties', string='ORG')
    varieties_ids = fields.Many2many('plant.varieties', string='ORGs')

    @api.onchange('account_report_id')
    def onchange_account_report_2(self):
        if self.account_report_id:
            self.fna_type = self.account_report_id.fna_type
    
    @api.onchange('fna_type')
    def _onchange_fna_type(self):
        if self.fna_type == 'pnl':
            self.debit_credit = True
        else:
            self.debit_credit = False

    def _build_comparison_varieties_context(self, data, varieties=False, not_varieties_ids=None):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['pnl_per_org'] = True
        if varieties:
            result['varieties_id'] = varieties.id
            result['title'] = varieties.name
        elif not_varieties_ids is not None:
            result['not_varieties_ids'] = not_varieties_ids
            result['title'] = "Other"
        return result

    def _print_report(self, data):
        if self.env.context.get('xlsx'):
            data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move', 'varieties_id'])[0])
            # data['form']['used_context'].update({'is_pnl': self.account_report_id.name=='Profit and Loss'})
            if self.fna_type == 'pnl' and self.pnl_per_org:
                data['form'].update({'pnl_per_org': True})
                comparison_org_context = []
                if self.varieties_ids:
                    for org in self.varieties_ids:
                        comparison_org_context.append(self._build_comparison_varieties_context(data, varieties=org))
                    comparison_org_context.append(self._build_comparison_varieties_context(data, not_varieties_ids=self.varieties_ids.ids))
                else:
                    for org in self.env['plant.varieties'].search([]):
                        comparison_org_context.apppend(self._build_comparison_varieties_context(data, varieties=org))
                data['form']['comparison_org_ctx'] = comparison_org_context
            # if self.varieties_id:
            #     data['form']['used_context'].update({'varieties_id': self.varieties_id.id})
            return self.env.ref('ny_account_report1.action_report_financial_xlsx').report_action(self, data=data, config=False)
        else:
            return super()._print_report(data)