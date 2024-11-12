from odoo import api, models, fields, _
import csv
# from odoo.exceptions import Warning
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta

class WmsInventoryAgingReportCSV(models.AbstractModel):
    _name = 'report.ny_hr_payroll.payroll_report_csv'
    _description = "Payroll Report CSV"
    _inherit = 'report.report_csv.abstract'

    wbf = {}

    def _get_objs_for_report(self, docids, data):
        options = data.get('options', {})
        wizard = self.env['payroll.report.wizard'].browse(options['src_id'])
        print(".........................", wizard)
        return wizard.payslip_ids

    def generate_csv_report(self, writer, data, obj):
        # writer.writeheader()
        print(">>>>>>>>>>>>>>>>>>>>>>>> JALAN")
        writer.writerow({
            '1': 'BANK MANDIRI - ANDRE TUWAN'})
        totalamount = sum(obj.line_ids.filtered(lambda l: l.salary_rule_id.category_id.code=='NET').mapped('total'))
        writer.writerow({
            '1': 'P',
            '2': fields.Date.today().strftime('%Y%m%d'),
            '3': '1320028618891',
            '4': len(obj.ids),
            '5': totalamount})
        for payslip in obj:
            writer.writerow({
                '1': payslip.employee_id.bank_account_id.acc_number if payslip.employee_id.bank_account_id else '',
                '2': payslip.employee_id.name[:70],
                '3': payslip.employee_id.street or '',
                '4': '',
                '5': '',
                '6': 'IDR',
                '7': payslip.line_ids.filtered(lambda l: l.salary_rule_id.category_id.code=='NET').total,
                '8': '',
                '9': '',
                '10': 'IBU',
                '11': payslip.employee_id.bank_account_id.bank_id.bic if payslip.employee_id.bank_account_id and payslip.employee_id.bank_account_id.bank_id else '',
                '12': payslip.employee_id.bank_account_id.bank_id.name if payslip.employee_id.bank_account_id and payslip.employee_id.bank_account_id.bank_id else '',
                '13': 'BANDUNG',
                '14': '',
                '15': '',
                '16': '',
                '17': 'N',
                '18': '',
                '19': 'BEN',
                '20': '1',
                '21': 'E',
                '22': '',
                '23': '',
                '24': '',
            })
    
    def csv_report_options(self):
        res = super().csv_report_options()
        for i in range(1,25):
            res['fieldnames'].append(str(i))
        res['delimiter'] = ';'
        res['quoting'] = csv.QUOTE_ALL
        return res
