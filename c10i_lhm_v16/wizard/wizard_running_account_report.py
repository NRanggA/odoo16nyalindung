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
    ], string="Document Type", default='pdf')
    account_period_id = fields.Many2one('account.period', 'Period', required=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company, required=True)


    def action_print_report(self):
        
        query = """
                SELECT
                    (case ll.code when 'WS' then 1 when 'VH' then 2 when 'MA' then 3 else 4 end) as seq,
                    ll.code as location_type, lu.code as code, 
                    la.code as activity_code, la.name as activity, 
                    sum(ral.total) as amount
                FROM
                    running_account_line ral
                    INNER JOIN running_account ra ON ra.id=ral.running_account_id
                    INNER JOIN lhm_utility lu ON lu.id=ral.utility_id
                    INNER JOIN lhm_location_type ll ON ll.id=lu.location_type_id
                    INNER JOIN lhm_activity la ON la.id=ral.activity_id
                WHERE
                    ra.account_period_id=%s
                GROUP BY ll.code, lu.code, la.code, la.name
                ORDER BY seq, lu.code
        """

        self.env.cr.execute(query, (self.account_period_id.id,))
        result = self.env.cr.fetchall()

        report_data = []
        for row in result:
            report_data.append({
                'seq': row[0],
                'location_type': row[1],
                'code': row[2],
                'activity_code': row[3],
                'activity': row[4],
                'amount': row[5],
            })

        data = {
            'report_type': self.report_type,
            'account_period_id': self.account_period_id.name,
            'company_id': self.company_id.id,
            'report_data': report_data, 
        }

        if self.report_type == 'pdf':
            return self.env.ref('c10i_lhm_v16.action_running_account_report_pdf').report_action(self, data=data)
        else:
            return self.env.ref('c10i_lhm_v16.action_running_account_report_xlsx').report_action(self, data=data)
    

