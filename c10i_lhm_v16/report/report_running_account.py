from odoo import models, fields, api

class ReportRunningAccount(models.AbstractModel):
    _name = 'report.c10i_lhm_v16.report_running_account_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Running Account Excel"

    # wbf = {}

    def generate_xlsx_report(self, workbook, data, objects):
        report_name = 'Laporan Running Account'
        sheet = workbook.add_worksheet(report_name[:31])
        
        # Add formats
        bold = workbook.add_format({'bold': True})
        text_right = workbook.add_format({'align': 'right'})

        # Write headers
        sheet.write(0, 0, 'PT KONSALTEN SOLUSI INDONESIA', bold)
        sheet.write(1, 0, 'LAPORAN RUNNING ACCOUNT', bold)
        sheet.write(2, 0, 'Periode : {}'.format(data['account_period_id']), bold)
        
        # Write column headers
        headers = ['No.', 'Tipe Lokasi', 'Kode Utilitas', 'Kode Aktivitas', 'Aktivitas', 'Nilai Running']
        for col, header in enumerate(headers):
            sheet.write(4, col, header, bold)
        
        # Write data
        for row_num, row_data in enumerate(data['report_data'], start=5):
            sheet.write(row_num, 0, row_data['seq'])
            sheet.write(row_num, 1, row_data['location_type'])
            sheet.write(row_num, 2, row_data['code'])
            sheet.write(row_num, 3, row_data['activity_code'])
            sheet.write(row_num, 4, row_data['activity'])
            sheet.write(row_num, 5, row_data['amount'], text_right)