from odoo import models

class ReportProduksiPanen(models.AbstractModel):
    _name = 'report.c10i_lhm_v16.prudksi_panen_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Produksi Panen Excel"

    def generate_xlsx_report(self, workbook, data, objects):
        report_name = 'Laporan Produksi Panen'
        sheet = workbook.add_worksheet(report_name[:31])
        
        # Format
        bold            = workbook.add_format({'bold': True, 'font_name': 'SansSerif', 'font_size': 10})
        bold_center     = workbook.add_format({'bold': True, 'font_name': 'SansSerif', 'font_size': 10, 'align': 'center', 'border': 1})
        text_right      = workbook.add_format({'align': 'right', 'font_name': 'SansSerif', 'font_size': 10})
        normal          = workbook.add_format({'font_name': 'SansSerif', 'font_size': 10})
        bordered        = workbook.add_format({'border': 1, 'font_name': 'SansSerif', 'font_size': 10})
        bordered_center = workbook.add_format({'border': 1, 'align': 'center', 'font_name': 'SansSerif', 'font_size': 10})
        bordered_right  = workbook.add_format({'border': 1, 'align': 'right', 'font_name': 'SansSerif', 'font_size': 10})

        produksi_id = self.env['wizard.report.produksi'].browse(data['datas']['produksi_id'])

        afdeling_names = ", ".join([afdeling.name for afdeling in produksi_id.afdeling_ids])

        # Judul Laporan
        sheet.merge_range('A1:F1', 'PT KONSALTEN SOLUSI INDONESIA', bold)
        sheet.merge_range('A2:F2', 'LAPORAN PANEN', bold)
        sheet.merge_range('A3:F3', 'Periode : {}'.format(produksi_id.date_start.strftime('%d-%m-%Y') + ' s.d. ' + produksi_id.date_end.strftime('%d-%m-%Y')), bold)
        sheet.merge_range('A4:F4', 'Afdeling : {}'.format(afdeling_names), bold)

        # Header Tabel
        headers = ['No.', 'Kemandoran/Kontraktor', 'Tgl. Proses', 'Kode', 'Lokasi', 'Satuan', 'Hasil Kerja', 'Satuan 2', 'Hasil Kerja 2', 'Realisasi', 'HK']
        for col, header in enumerate(headers):
            sheet.write(5, col, header, bold_center)

        row = 6
        no = 1

        for panen in produksi_id.panen_ids:
            sheet.write(row, 0, no, bordered_center)
            sheet.write(row, 1, panen.hr_foreman_id.name or '', bordered)
            sheet.write(row, 2, str(panen.date) or '', bordered_center)
            sheet.write(row, 3, panen.location_code or '', bordered)
            sheet.write(row, 4, panen.location_id.name or '', bordered)
            sheet.write(row, 5, panen.uom_id.name or '', bordered)
            sheet.write(row, 6, panen.nilai or 0, bordered_right)
            sheet.write(row, 7, panen.uom_id2.name or '', bordered)
            sheet.write(row, 8, panen.nilai2 or 0, bordered_right)
            sheet.write(row, 9, panen.total or 0, bordered_right)
            sheet.write(row, 10, panen.hk or 0, bordered_right)
            row += 1
            no += 1

        print(f"==== Data objects   : {produksi_id}")
        
        

