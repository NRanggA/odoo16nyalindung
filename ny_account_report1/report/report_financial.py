# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError
from odoo.addons.accounting_pdf_reports.report import report_financial

class ReportFinancial(report_financial.ReportFinancial):
    _name = "report.ny_account_report1.report_financial2"
    
    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search(
            [('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            comparison_res = self.with_context(
                data.get('comparison_context'))._compute_report_balance(
                child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']
        print("::::::::::::::::::", data['pnl_per_org'], data['comparison_org_ctx'])
        if data['pnl_per_org'] and data['comparison_org_ctx']:
            for comparison_org_ctx in data['comparison_org_ctx']:
                print("................", comparison_org_ctx)
                varieties_id = comparison_org_ctx.get('varieties_id', 0)
                comparison_org_pnl = self.with_context(comparison_org_ctx)._compute_report_balance(child_reports)
                for report_id, value in comparison_org_pnl.items():
                    res[report_id][f"comp_dr_{varieties_id}"] = value['debit']
                    res[report_id][f"comp_cr_{varieties_id}"] = value['credit']
                    res[report_id][f"comp_bal_{varieties_id}"] = value['balance']
                    report_acc = res[report_id].get('account')
                    if report_acc:
                        for account_id, val in comparison_org_pnl[report_id].get('account').items():
                            report_acc[account_id][f"comp_dr_{varieties_id}"] = val['debit']
                            report_acc[account_id][f"comp_cr_{varieties_id}"] = val['credit']
                            report_acc[account_id][f"comp_bal_{varieties_id}"] = val['balance']
        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * float(report.sign),
                'type': 'report',
                'level': report.level,
                'is_child': False,
                'account_type': report.type or False, #used to underline the financial report balances
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * float(report.sign)
            if data['pnl_per_org'] and data['comparison_org_ctx']:
                for comparison_org_ctx in data['comparison_org_ctx']:
                    varieties_id = comparison_org_ctx.get('varieties_id', 0)
                    vals[f"debit_cmp_{varieties_id}"] = res[report.id][f"comp_dr_{varieties_id}"] * float(report.sign)
                    vals[f"credit_cmp_{varieties_id}"] = res[report.id][f"comp_cr_{varieties_id}"] * float(report.sign)
                    vals[f"balance_cmp_{varieties_id}"] = res[report.id][f"comp_bal_{varieties_id}"] * float(report.sign)


            lines.append(vals)
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * float(report.sign) or 0.0,
                        'type': 'account',
                        'level': report.level + 1,
                        'is_child': True,
                        'account_type': account.account_type,
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * float(report.sign)
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if data['pnl_per_org'] and data['comparison_org_ctx']:
                        for comparison_org_ctx in data['comparison_org_ctx']:
                            varieties_id = comparison_org_ctx.get('varieties_id', 0)
                            vals[f"debit_cmp_{varieties_id}"] = value[f"comp_dr_{varieties_id}"] * float(report.sign)
                            vals[f"credit_cmp_{varieties_id}"] = value[f"comp_cr_{varieties_id}"] * float(report.sign)
                            vals[f"balance_cmp_{varieties_id}"] = value[f"comp_bal_{varieties_id}"] * float(report.sign)
                            if not account.company_id.currency_id.is_zero(vals[f"balance_cmp_{varieties_id}"]):
                                flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        return lines
    
    def _compute_account_balance_with_domain(self, add_domains):
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        tables, where_clause, where_params = self.env['account.move.line']._query_get(add_domains)
        tables = tables.replace('"', '') if tables else "account_move_line"
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)

        request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                    " FROM " + tables + \
                    " WHERE account_id IN %s " \
                        + filters + \
                    " GROUP BY account_id"
        params = tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            res[row['id']] = row
        return res

    def _compute_report_balance(self, reports):
        report_type_code = reports.filtered(lambda r: r.type=='code')
        report_type_domain = reports.filtered(lambda r: r.type=='domain')
        print(":::::::::::::_compute_report_balance:::::::::::: context", self._context)
        res = super(ReportFinancial, self)._compute_report_balance(reports - report_type_code - report_type_domain)
        fields = ['credit', 'debit', 'balance']
        for report in report_type_code:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            
            accounts = self.env['account.account'].search(
                ['|',('code', '=', report.account_code),('code', '=ilike', f"{report.account_code}%")])

            res[report.id]['account'] = self._compute_account_balance(accounts)
            for value in res[report.id]['account'].values():
                for field in fields:
                    res[report.id][field] += value.get(field)
        for report in report_type_domain:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            
            accounts = self.env['account.account'].search(
                ['|',('code', '=', report.account_code),('code', '=ilike', f"{report.account_code}%")])

            res[report.id]['account'] = self._compute_account_balance_with_domain(eval(report.domain))
            for value in res[report.id]['account'].values():
                for field in fields:
                    res[report.id][field] += value.get(field)
        return res