# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################
from odoo import models, fields, api, _

class WizardRunningAccountReport(models.TransientModel):
    _name = "wizard.running.account.report"
    _description = "Running Account Report"

    report_type = fields.Selection([
        ('pdf', 'PDF'),
        ('xls', 'Excel')
    ], string="Document Type", default='pdf', required=True)
    account_period_id = fields.Many2one('account.period', 'Period', required=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company, required=True)

    def create_report(self):
        data = self.read()[-1]
        name = 'running_account_report'
        if data['report_type'] == 'xls':
            name = 'running_account_report_xls'
        return {
            'type': 'ir.actions.report',
            'report_name': name,
            'model': 'wizard.running.account.report',
            'report_type': data['report_type'],
            'datas': {
                'ids': self._context.get('active_ids', []) or [],
                'model': 'wizard.running.account.report',
                'form': data,
            },
            'nodestroy': False
        }
