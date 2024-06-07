from odoo import models

class ReportRunningAccount(models.AbstractModel):
    _name = 'report.c10i_lhm_v16.report_running_account_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Running Account Excel"

    def generate_xlsx_report(self, workbook, data, objects):
        report_name = 'Laporan Running Account'
        sheet = workbook.add_worksheet(report_name[:31])
        
        # Format
        bold            = workbook.add_format({'bold': True, 'font_name': 'SansSerif', 'font_size': 10})
        bold_center     = workbook.add_format({'bold': True, 'font_name': 'SansSerif', 'font_size': 10, 'align': 'center', 'border': 1})
        text_right      = workbook.add_format({'align': 'right', 'font_name': 'SansSerif', 'font_size': 10})
        normal          = workbook.add_format({'font_name': 'SansSerif', 'font_size': 10})
        bordered        = workbook.add_format({'border': 1, 'font_name': 'SansSerif', 'font_size': 10})
        bordered_center = workbook.add_format({'border': 1, 'align': 'center', 'font_name': 'SansSerif', 'font_size': 10})
        bordered_right  = workbook.add_format({'border': 1, 'align': 'right', 'font_name': 'SansSerif', 'font_size': 10})

        # Judul Laporan
        sheet.merge_range('A1:F1', 'PT KONSALTEN SOLUSI INDONESIA', bold)
        sheet.merge_range('A2:F2', 'LAPORAN RUNNING ACCOUNT', bold)
        sheet.merge_range('A3:F3', 'Periode : {}'.format(data['account_period_id']), bold)
        
        # Header Tabel
        headers = ['No.', 'Tipe Lokasi', 'Kode Utilitas', 'Kode Aktivitas', 'Aktivitas', 'Nilai Running']
        for col, header in enumerate(headers):
            sheet.write(4, col, header, bold_center)
        
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 10)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 40)
        sheet.set_column(5, 5, 15)

        # Data pada report
        row_num = 5
        current_location_type = ''
        for row_data in data['report_data']:
            if row_data['location_type'] != current_location_type:
                if current_location_type:
                    sheet.write(row_num, 0, '', bordered)
                    sheet.write(row_num, 1, '', bordered)
                    sheet.write(row_num, 2, '', bordered)
                    sheet.write(row_num, 3, '', bordered)
                    sheet.write(row_num, 4, 'Subtotal {}'.format(current_location_type), bordered)
                    sheet.write(row_num, 5, '', bordered_right)
                    row_num += 1
                current_location_type = row_data['location_type']
                sheet.write(row_num, 0, '', bold)
                sheet.write(row_num, 1, current_location_type, bold)
                sheet.write(row_num, 2, '', bold)
                sheet.write(row_num, 3, '', bold)
                sheet.write(row_num, 4, '', bold)
                sheet.write(row_num, 5, '', bold)
                row_num += 1

            sheet.write(row_num, 0, row_data['seq'], bordered_center)
            sheet.write(row_num, 1, row_data['location_type'], bordered_center)
            sheet.write(row_num, 2, row_data['code'], bordered_center)
            sheet.write(row_num, 3, row_data['activity_code'], bordered_center)
            sheet.write(row_num, 4, row_data['activity'], bordered)
            sheet.write(row_num, 5, row_data['amount'], bordered_right)
            row_num += 1
        
        sheet.write(row_num, 0, '', bordered)
        sheet.write(row_num, 1, '', bordered)
        sheet.write(row_num, 2, '', bordered)
        sheet.write(row_num, 3, '', bordered)
        sheet.write(row_num, 4, 'Subtotal {}'.format(current_location_type), bordered)
        sheet.write(row_num, 5, '', bordered_right)

