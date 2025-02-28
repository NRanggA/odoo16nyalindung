from odoo import models
from datetime import datetime, timedelta

class ReportProduction(models.AbstractModel):
    _name = 'report.nyalindung_report.production_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Production Excel"

    wbf = {}

    def add_workbook_format(self, workbook):
        # Header format untuk judul utama (misalnya, judul laporan)
        self.wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'font_color': '#000000',
            'bg_color': '#D9D9D9'
        })
        # Format untuk header kolom tabel
        self.wbf['header'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 8,
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['header'].set_text_wrap()
        self.wbf['header'].set_border()

        # Format untuk header kolom tabel
        self.wbf['kemandoran'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 20,
            'font_color': '#FFFFFF',
            'bg_color': '#088404',
            'border': 1
        })
        self.wbf['header'].set_text_wrap()
        self.wbf['header'].set_border()

        self.wbf['jumlah_total'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 8,
            'font_color': '#FFFFFF',
            'bg_color': '#088404',
            'border': 1
        })
        self.wbf['jumlah_total'].set_text_wrap()
        self.wbf['jumlah_total'].set_border()

        # Format untuk kolom data
        self.wbf['data'] = workbook.add_format({
            'font_color': '#000000',
            'font_size': 8,
            'border': 1
        })
        self.wbf['data'].set_text_wrap()
        self.wbf['data'].set_border()

        # Format untuk kolom data center
        self.wbf['data_center'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'font_size': 8,
            'border': 1
        })
        self.wbf['data_center'].set_text_wrap()
        self.wbf['data_center'].set_border()

        # Format untuk kolom data center
        self.wbf['center_bold'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
        })
        self.wbf['data_center'].set_text_wrap()
        self.wbf['data_center'].set_border()

        # Format untuk footer (biasanya penutup dokumen, misal total atau sum)
        self.wbf['footer'] = workbook.add_format({
            'align': 'left',
            'font_size': 10,
        })
        self.wbf['footer'].set_bottom()

        # Format konten datetime
        self.wbf['content_datetime'] = workbook.add_format({
            'num_format': 'yyyy-mm-dd hh:mm:ss',
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_datetime'].set_border()

        # Format konten date (hanya tanggal)
        self.wbf['content_date'] = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_date'].set_border()

        # Format konten float (angka desimal)
        self.wbf['content_float'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            # 'num_format': '#,##0.00'
            'num_format': '#,##0.00;-#,##0.00;-',
        })
        self.wbf['content_float'].set_border()

        # Format untuk teks konten yang rata kiri
        self.wbf['content'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
        })
        self.wbf['content'].set_border()

        # Format untuk konten rata tengah
        self.wbf['content_center'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })
        # self.wbf['content_center'].set_border()

        # Format untuk konten rata kanan (angka tanpa desimal)
        self.wbf['content_number'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '0',
        })
        self.wbf['content_number'].set_border()

        # Format untuk konten persentase
        self.wbf['content_percent'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '0.00%'
        })
        self.wbf['content_percent'].set_border()

        # Format total float
        self.wbf['total_float'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0.00;-#,##0.00;-',
            'font_color': '#000000',
            'border': 1,
            'font_size' : 8
        })
        self.wbf['total_float'].set_border()

        # Format total float (untuk jumlah total yang bold dengan background kuning)
        self.wbf['total_float_kuning'] = workbook.add_format({
            'bold': True,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'num_format': '#,##0.00;-#,##0.00;-',
            'font_color': '#000000'
        })
        self.wbf['total_float_kuning'].set_border()

        # Format total number (untuk jumlah total tanpa desimal)
        self.wbf['total_number'] = workbook.add_format({
            'bold': True,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'font_color': '#000000'
        })
        self.wbf['total_number'].set_border()

        # Format total teks (untuk teks di footer atau total yang di tengah)
        self.wbf['total'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'font_color': '#000000'
        })
        self.wbf['total'].set_border()

        # Format untuk kolom data center berwarna
        self.wbf['biru_muda'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#4ACCE6',
            'font_size': 8,
            'border': 1
        })
        self.wbf['biru_muda'].set_text_wrap()
        self.wbf['biru_muda'].set_border()

        self.wbf['hijau_muda'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#4AE656',
            'font_size': 8,
            'border': 1
        })
        self.wbf['hijau_muda'].set_text_wrap()
        self.wbf['hijau_muda'].set_border()

        self.wbf['hijau_tua'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#188520',
            'font_size': 8,
            'border': 1
        })
        self.wbf['hijau_tua'].set_text_wrap()
        self.wbf['hijau_tua'].set_border()

        self.wbf['biru_tua'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#134869',
            'font_size': 8,
            'border': 1
        })
        self.wbf['biru_tua'].set_text_wrap()
        self.wbf['biru_tua'].set_border()

        self.wbf['kuning'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#F7DB0F',
            'font_size': 8,
            'border': 1
        })
        self.wbf['kuning'].set_text_wrap()
        self.wbf['kuning'].set_border()

        self.wbf['merah'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#DE1313',
            'font_size': 8,
            'border': 1
        })
        self.wbf['merah'].set_text_wrap()
        self.wbf['merah'].set_border()

        return workbook

    def generate_query_hasil_1(self, obj, kemandoran_id):
        from_date = obj.from_date.strftime("%Y-%m-%d")
        to_date = obj.to_date.strftime("%Y-%m-%d")

        start_date = datetime.strptime(from_date, "%Y-%m-%d")
        end_date = datetime.strptime(to_date, "%Y-%m-%d")

        date_generated = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        cases_attendance_id = [
            f"MAX(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN trans_data.attendance_id ELSE NULL END) AS \"{date.strftime('%d_%b_%y').upper()}_DATE\""
            for date in date_generated
        ]
        sum_cases_hasil_1 = [
            f"SUM(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN trans_data.hasil_1_nap ELSE 0 END) AS \"{date.strftime('%d_%b_%y').upper()}_HASIL_1_NAP\""
            for date in date_generated
        ]
        sum_cases_hasil_2 = [
            f"SUM(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN trans_data.hasil_2_nap ELSE 0 END) AS \"{date.strftime('%d_%b_%y').upper()}_HASIL_2_NAP\""
            for date in date_generated
        ]
        cases_drc_lateks = [
            f"SUM(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN trans_data.drc_latex_nap ELSE 0 END) AS \"{date.strftime('%d_%b_%y').upper()}_DRC_LATEKS\""
            for date in date_generated
        ]
        cases_drc_lump = [
            f"SUM(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN trans_data.drc_lump_nap ELSE 0 END) AS \"{date.strftime('%d_%b_%y').upper()}_DRC_LUMP\""
            for date in date_generated
        ]
        sum_cases_konversi_hasil_1 = [
            f"SUM(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN trans_data.hasil_convert_latex ELSE 0 END) AS \"{date.strftime('%d_%b_%y').upper()}_HASIL_CONVERT_LATEKS\""
            for date in date_generated
        ]
        sum_cases_konversi_hasil_2 = [
            f"SUM(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN trans_data.hasil_convert_lump ELSE 0 END) AS \"{date.strftime('%d_%b_%y').upper()}_HASIL_CONVERT_LUMP\""
            for date in date_generated
        ]

        sum_cases_total_konversi = [
            f"SUM(CASE WHEN trans_data.date = '{date.strftime('%Y-%m-%d')}' THEN COALESCE(trans_data.hasil_convert_latex, 0) + COALESCE(trans_data.hasil_convert_lump, 0) ELSE 0 END) AS \"{date.strftime('%d_%b_%y').upper()}_TOTAL_HASIL_CONVERT\""
            for date in date_generated
        ]

        queryhasil1 = f"""
        WITH employee_data AS (
            SELECT 
                emp.id AS emp_id,
                emp.name AS employee_name,
                emp.kemandoran_id AS kemandoran_emp,
                emp.no_induk as no_induk
            FROM 
                hr_employee emp
            WHERE 
                emp.active = TRUE
                AND emp.kemandoran_id = %s
        ),
        trans_data AS (
            SELECT 
                trans_nap_line.hasil_1_nap,  
                trans_nap_line.hasil_2_nap,  
                trans_nap_line.drc_latex_nap,  
                trans_nap_line.drc_lump_nap,  
                trans_nap_line.hasil_convert_latex,  
                trans_nap_line.hasil_convert_lump,  
                trans.date,
                trans_line.attendance_id, 
                trans_line.employee_id,
                trans_line.location_id
            FROM 
                lhm_transaction_nap_line trans_nap_line
            JOIN 
                lhm_transaction_line trans_line 
                ON trans_line.id = trans_nap_line.lhm_transaction_line_id
                AND trans_line.state = 'done'
            JOIN 
                lhm_transaction trans 
                ON trans.id = trans_line.lhm_id
            WHERE 
                trans.date BETWEEN %s AND %s
        )
        SELECT
            employee_data.employee_name,
            employee_data.no_induk,
            employee_data.kemandoran_emp,
            trans_data.location_id,
            SUM(COALESCE(trans_data.hasil_1_nap, 0)) AS total_hasil_1_nap,
            SUM(COALESCE(trans_data.hasil_2_nap, 0)) AS total_hasil_2_nap,
            SUM(COALESCE(trans_data.hasil_convert_latex, 0)) AS total_hasil_convert_latex,
            SUM(COALESCE(trans_data.hasil_convert_lump, 0)) AS total_hasil_convert_lump,
            SUM(COALESCE(trans_data.hasil_convert_latex, 0) + COALESCE(trans_data.hasil_convert_lump, 0)) AS total_hasil_convert,
            COUNT(trans_data.attendance_id) AS attendance_count,
            {','.join(cases_attendance_id)},
            {','.join(sum_cases_hasil_1)},
            {','.join(sum_cases_hasil_2)},
            {','.join(cases_drc_lateks)},
            {','.join(cases_drc_lump)},
            {','.join(sum_cases_konversi_hasil_1)},
            {','.join(sum_cases_konversi_hasil_2)},
            {','.join(sum_cases_total_konversi)}
        FROM 
            employee_data
        LEFT JOIN 
            trans_data ON employee_data.emp_id = trans_data.employee_id
        GROUP BY 
            employee_data.employee_name,
            employee_data.no_induk,
            employee_data.kemandoran_emp,
            trans_data.location_id
        ORDER BY
            employee_data.employee_name ASC,
            trans_data.location_id;
        """
        return queryhasil1, [kemandoran_id, from_date, to_date]

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf
        sheet = workbook.add_worksheet("Laporan Produksi Karet Detail")
        row = 0

        from_date = obj.from_date
        to_date = obj.to_date
        kemandoran_ids = obj.kemandoran_id.ids if obj.kemandoran_id else [140, 193, 194, 195]

        attendance_data = {}

        for kemandoran_id in kemandoran_ids:
            query1, params1 = self.generate_query_hasil_1(obj, kemandoran_id)
            self.env.cr.execute(query1, params1)
            list_hasil_1 = self.env.cr.dictfetchall()

            sheet.write(row, 0, 'Laporan Produksi Karet Detail')
            row += 1
            sheet.write(row, 0,'BULAN')
            sheet.write(row, 1,':', wbf['content_center'])
            sheet.write(row, 2,f'{from_date.strftime("%d-%m-%Y")} s/d {to_date.strftime("%d-%m-%Y")}' if from_date and to_date else '')
            row += 2
            kemandoran = self.env['hr.foreman'].browse(kemandoran_id)
            sheet.merge_range(row, 0, row + 1, 4, kemandoran.name or '', wbf['kemandoran'])
            sheet.write(row + 2, 0, 'NO.', wbf['header'])
            sheet.set_column(5, 0, 7)
            sheet.write(row + 2, 1,'NIK', wbf['header'])
            sheet.set_column(5, 1, 13)
            sheet.write(row + 2, 2,'NAMA', wbf['header'])
            sheet.set_column(5, 2, 13)
            sheet.write(row + 2, 3, 'KEMANDORAN', wbf['header'])
            sheet.set_column(5, 3, 13)
            sheet.write(row + 2, 4, 'LOKASI',  wbf['header'])
            sheet.set_column(5, 4, 16)
            sheet.set_column(5, 5, 8)

            mandor_name = kemandoran.kepala_mandor_id.sudo().name if kemandoran.kepala_mandor_id else ''
            mandor_nik = kemandoran.kepala_mandor_id.sudo().no_induk if kemandoran.kepala_mandor_id else ''
            asisten_mandor_name = kemandoran.mandor_id.sudo().name if kemandoran.mandor_id else ''
            asisten_mandor_nik = kemandoran.mandor_id.sudo().no_induk if kemandoran.mandor_id else ''
            kerani_name = kemandoran.assisten_id.sudo().name if kemandoran.assisten_id else ''
            kerani_nik = kemandoran.assisten_id.sudo().no_induk if kemandoran.assisten_id else ''

            if from_date and to_date:
                delta = to_date - from_date
                date_columns = []
                for i in range(delta.days + 1):
                    current_date = from_date + timedelta(days=i)
                    date_columns.append(current_date.strftime('%d_%b_%y').upper())
                
                attendance_data = {date: 0 for date in date_columns}

                hko_start = 5
                sheet.merge_range(row, hko_start, row + 1, hko_start + 5, 'JUMLAH HKO', wbf['header'])

                total_hk_start = hko_start + 6
                sheet.merge_range(row, total_hk_start, row + 2, total_hk_start, 'TOTAL HK', wbf['header'])

                start_col = total_hk_start + 1
                end_col = start_col + len(date_columns) - 1
                sheet.merge_range(row, start_col, row + 1, end_col, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    sheet.write(row + 2, start_col + i, date[:2], wbf['header'])
                    sheet.set_column(start_col + i, start_col + i, 5)
            hko_headers = ['HKO', 'L', 'S', 'P', 'CT', 'M']
            hko_formats = [self.wbf['biru_muda'], self.wbf['hijau_tua'], self.wbf['kuning'], self.wbf['biru_tua'], self.wbf['biru_muda'], self.wbf['merah']]

            for i, header in enumerate(hko_headers):
                sheet.write(row + 2, hko_start + i, header, hko_formats[i])

            for i, header in enumerate(hko_headers):
                sheet.write(row + 2, hko_start + i, header, hko_formats[i])

            #lateks
            if from_date and to_date:
                jumlah_hasil_sadapan_lateks = end_col + 2
                sheet.merge_range(row, jumlah_hasil_sadapan_lateks, row + 1, jumlah_hasil_sadapan_lateks, 'JUMLAH HASIL SADAPAN', wbf['header'])
                
                second_date_start = jumlah_hasil_sadapan_lateks + 1
                second_date_end = second_date_start + len(date_columns) - 1
                sheet.merge_range(row, second_date_start, row + 1, second_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = second_date_start + i
                    sheet.write(row + 2, col_index, date[:2], wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #lump
            if from_date and to_date:
                jumlah_hasil_sadapan_lump = second_date_end + 2
                sheet.merge_range(row, jumlah_hasil_sadapan_lump, row + 1, jumlah_hasil_sadapan_lump, 'JUMLAH HASIL SADAPAN', wbf['header'])
                
                third_date_start = jumlah_hasil_sadapan_lump + 1
                third_date_end = third_date_start + len(date_columns) - 1
                sheet.merge_range(row, third_date_start, row + 1, third_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = third_date_start + i
                    sheet.write(row + 2, col_index, date[:2], wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #drc lateks
            if from_date and to_date:
                fourth_date_start = third_date_end + 2
                fourth_date_end = fourth_date_start + len(date_columns) - 1
                sheet.merge_range(row, fourth_date_start, row, fourth_date_end, 'DRC LATEKS', wbf['header'])
                sheet.merge_range(row + 1, fourth_date_start, row + 1, fourth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fourth_date_start + i
                    sheet.write(row + 2, col_index, date[:2], wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #drc lump
            if from_date and to_date:
                fifth_date_start = fourth_date_end + 2
                fifth_date_end = fifth_date_start + len(date_columns) - 1
                sheet.merge_range(row, fifth_date_start, row, fifth_date_end, 'DRC LUMP', wbf['header'])
                sheet.merge_range(row + 1, fifth_date_start, row + 1, fifth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fifth_date_start + i
                    sheet.write(row + 2, col_index, date[:2], wbf['header'])
                    sheet.set_column(col_index, col_index, 5)
            
            #konversi lateks
            if from_date and to_date:
                jumlah_hasil_konversi_lateks = fifth_date_end + 2
                sheet.merge_range(row, jumlah_hasil_konversi_lateks, row + 1, jumlah_hasil_konversi_lateks, 'JUMLAH HASIL KONVERSI', wbf['header'])
                
                sixth_date_start = jumlah_hasil_konversi_lateks + 1
                sixth_date_end = sixth_date_start + len(date_columns) - 1
                sheet.merge_range(row, sixth_date_start, row + 1, sixth_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = sixth_date_start + i
                    sheet.write(row + 2, col_index, date[:2], wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #konversi lump
            if from_date and to_date:
                jumlah_hasil_konversi_lump = sixth_date_end + 2
                sheet.merge_range(row, jumlah_hasil_konversi_lump, row + 1, jumlah_hasil_konversi_lump, 'JUMLAH HASIL KONVERSI', wbf['header'])
                
                seventh_date_start = jumlah_hasil_konversi_lump + 1
                seventh_date_end = seventh_date_start + len(date_columns) - 1
                sheet.merge_range(row, seventh_date_start, row + 1, seventh_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = seventh_date_start + i
                    sheet.write(row + 2, col_index, date[:2], wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #total konversi lateks + lump
            if from_date and to_date:
                jumlah_total_konversi = seventh_date_end + 2
                sheet.merge_range(row, jumlah_total_konversi, row + 1, jumlah_total_konversi, 'TOTAL HASIL KONVERSI', wbf['header'])
                
                eighth_date_start = jumlah_total_konversi + 1
                eighth_date_end = eighth_date_start + len(date_columns) - 1
                sheet.merge_range(row, eighth_date_start, row + 1, eighth_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = eighth_date_start + i
                    sheet.write(row + 2, col_index, date[:2], wbf['header'])
                    sheet.set_column(col_index, col_index, 5)
            
            lateks_row_start = row + 2
            lateks_col_start = jumlah_hasil_sadapan_lateks
            sheet.write(lateks_row_start, lateks_col_start, 'LATEKS (L)', wbf['header'])

            lump_row_start = row + 2
            lump_col_start = jumlah_hasil_sadapan_lump
            sheet.write(lump_row_start, lump_col_start, 'LUMP (Kg)', wbf['header'])

            clateks_row_start = row + 2
            clateks_col_start = jumlah_hasil_konversi_lateks
            sheet.write(clateks_row_start, clateks_col_start, 'LATEKS (Kg)', wbf['header'])

            clump_row_start = row + 2
            clump_col_start = jumlah_hasil_konversi_lump
            sheet.write(clump_row_start, clump_col_start, 'LUMP (Kg)', wbf['header'])

            tkonversi_row_start = row + 2
            tkonversi_col_start = jumlah_total_konversi
            sheet.write(tkonversi_row_start, tkonversi_col_start, 'KARET (Kg)', wbf['header'])

            row += 3

            # Data
            row += 1
            nomor = 1
            total_kj_per_date = {date: 0 for date in date_columns}
            total_hasil_1_per_tanggal = {date: 0 for date in date_columns}
            total_hasil_2_per_tanggal = {date: 0 for date in date_columns}
            total_chasil_1_per_tanggal = {date: 0 for date in date_columns}
            total_chasil_2_per_tanggal = {date: 0 for date in date_columns}
            total_convert_per_tanggal = {date: 0 for date in date_columns}

            for line in list_hasil_1:
                # print(f"Row Data: {line}")
                sheet.write(row, 0, nomor, wbf['data_center'])

                no_induk = line.get("no_induk")
                sheet.write(row, 1, no_induk, wbf['data'])

                employee_name = line.get("employee_name", "N/A")
                sheet.write(row, 2, employee_name, wbf['data'])

                kemandoran_emp = line.get("kemandoran_emp")
                kemandoran_name = self.env["hr.foreman"].browse(kemandoran_emp).name if kemandoran_emp else "-"
                sheet.write(row, 3, kemandoran_name, wbf['data'])
                
                location_id = line.get("location_id")
                location_name = self.env["lhm.location"].browse(location_id).name if location_id else "-"
                sheet.write(row, 4, location_name, wbf['data'])

                attendance_count = line.get("attendance_count", 0)
                sheet.write(row, hko_start, attendance_count, wbf['biru_muda'])
                sheet.write(row, hko_start + 1, 0, wbf['data_center'])
                sheet.write(row, hko_start + 2, 0, wbf['data_center'])
                sheet.write(row, hko_start + 3, 0, wbf['data_center'])
                sheet.write(row, hko_start + 4, 0, wbf['data_center'])
                sheet.write(row, hko_start + 5, 0, wbf['data_center'])
                sheet.write(row, total_hk_start, attendance_count, wbf['data_center'])

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    column_name = f"{date.strftime('%d_%b_%y').upper()}_DATE"
                    attendance_id = line.get(column_name)
                    attendance_code = self.env["hr.attendance.type"].browse(attendance_id).code if attendance_id else "-"
                    if attendance_code == "KJ":
                        total_kj_per_date[date_str] += 1
                    cell_format = wbf['hijau_muda'] if attendance_code == "KJ" else wbf['data_center']
                    sheet.write(row, start_col + i, attendance_code, cell_format)

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    col_index = second_date_start + i
                    column_key = f"{date.strftime('%d_%b_%y').upper()}_HASIL_1_NAP"
                    hasil_sadapan_lateks = line.get(column_key, 0)
                    total_hasil_1_tanggal = line.get("total_hasil_1_nap", 0)
                    total_hasil_1_per_tanggal[date_str] += hasil_sadapan_lateks
                    sheet.write(lateks_row_start + 2, second_date_start - 1, total_hasil_1_tanggal, wbf['total_float'])
                    sheet.write(lateks_row_start + 2, col_index, hasil_sadapan_lateks, wbf['total_float'])
                lateks_row_start += 1

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    col_index = third_date_start + i
                    column_key = f"{date.strftime('%d_%b_%y').upper()}_HASIL_2_NAP"
                    hasil_sadapan_lump = line.get(column_key, 0)
                    total_hasil_2_tanggal = line.get("total_hasil_2_nap", 0)
                    total_hasil_2_per_tanggal[date_str] += hasil_sadapan_lump
                    sheet.write(lump_row_start + 2, third_date_start - 1, total_hasil_2_tanggal, wbf['total_float'])
                    sheet.write(lump_row_start + 2, col_index, hasil_sadapan_lump, wbf['total_float'])
                lump_row_start += 1

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    col_index = fourth_date_start + i
                    column_key = f"{date.strftime('%d_%b_%y').upper()}_DRC_LATEKS"
                    drc_lateks = line.get(column_key, 0)
                    sheet.write(row, col_index, drc_lateks, wbf['total_float'])

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    col_index = fifth_date_start + i
                    column_key = f"{date.strftime('%d_%b_%y').upper()}_DRC_LUMP"
                    drc_lump = line.get(column_key, 0)
                    sheet.write(row, col_index, drc_lump, wbf['total_float'])

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    col_index = sixth_date_start + i
                    column_key = f"{date.strftime('%d_%b_%y').upper()}_HASIL_CONVERT_LATEKS"
                    hasil_convert_lateks = line.get(column_key, 0)
                    total_hasil_convert_lateks = line.get("total_hasil_convert_latex", 0)
                    total_chasil_1_per_tanggal[date_str] += hasil_convert_lateks
                    sheet.write(clateks_row_start + 2, sixth_date_start - 1, total_hasil_convert_lateks, wbf['total_float'])
                    sheet.write(clateks_row_start + 2, col_index, hasil_convert_lateks, wbf['total_float'])
                clateks_row_start += 1

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    col_index = seventh_date_start + i
                    column_key = f"{date.strftime('%d_%b_%y').upper()}_HASIL_CONVERT_LUMP"
                    hasil_convert_lump = line.get(column_key, 0)
                    total_hasil_convert_lump = line.get("total_hasil_convert_lump", 0)
                    total_chasil_2_per_tanggal[date_str] += hasil_convert_lump
                    sheet.write(clump_row_start + 2, seventh_date_start - 1, total_hasil_convert_lump, wbf['total_float'])
                    sheet.write(clump_row_start + 2, col_index, hasil_convert_lump, wbf['total_float'])
                clump_row_start += 1

                for i, date_str in enumerate(date_columns):
                    date = datetime.strptime(date_str, "%d_%b_%y")
                    col_index = eighth_date_start + i
                    column_key = f"{date.strftime('%d_%b_%y').upper()}_TOTAL_HASIL_CONVERT"
                    hasil_convert = line.get(column_key, 0)
                    total_hasil_convert = line.get("total_hasil_convert", 0)
                    total_convert_per_tanggal[date_str] += hasil_convert
                    sheet.write(tkonversi_row_start + 2, eighth_date_start - 1, total_hasil_convert, wbf['total_float'])
                    sheet.write(tkonversi_row_start + 2, col_index, hasil_convert, wbf['total_float'])
                tkonversi_row_start += 1

                row += 1
                nomor += 1

            row += 1
            sheet.write(row, 0, "M-1", wbf['data_center'])
            sheet.write(row + 1, 0, "M-2", wbf['data_center'])
            sheet.write(row + 2, 0, "M-3", wbf['data_center'])

            sheet.write(row, 1, mandor_nik, wbf['data'])
            sheet.write(row + 1, 1, asisten_mandor_nik, wbf['data'])
            sheet.write(row + 2, 1, kerani_nik, wbf['data'])

            sheet.write(row, 2, mandor_name, wbf['data'])
            sheet.write(row + 1, 2, asisten_mandor_name, wbf['data'])
            sheet.write(row + 2, 2, kerani_name, wbf['data'])

            sheet.write(row, 3, kemandoran_name, wbf['data'])
            sheet.write(row + 1, 3, kemandoran_name, wbf['data'])
            sheet.write(row + 2, 3, kemandoran_name, wbf['data'])

            sheet.write(row, 4, "-", wbf['data'])
            sheet.write(row + 1, 4, "-", wbf['data'])
            sheet.write(row + 2, 4, "-", wbf['data'])

            sheet.write(row, hko_start, "-", wbf['biru_muda'])
            sheet.write(row, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row, total_hk_start, "-", wbf['data_center'])

            sheet.write(row + 1, hko_start, "-", wbf['biru_muda'])
            sheet.write(row + 1, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row + 1, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row + 1, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row + 1, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row + 1, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row + 1, total_hk_start, "-", wbf['data_center'])

            sheet.write(row + 2, hko_start, "-", wbf['biru_muda'])
            sheet.write(row + 2, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row + 2, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row + 2, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row + 2, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row + 2, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row + 2, total_hk_start, "-", wbf['data_center'])

            for i, date in enumerate(date_columns):
                sheet.write(row, start_col + i, "-", wbf['header'])
                sheet.write(row + 1, start_col + i, "-", wbf['header'])
                sheet.write(row + 2, start_col + i, "-", wbf['header'])

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index_2 = second_date_start + i
                col_index_3 = third_date_start + i
                col_index_4 = fourth_date_start + i
                col_index_5 = fifth_date_start + i
                col_index_6 = sixth_date_start + i
                col_index_7 = seventh_date_start + i
                col_index_8 = eighth_date_start + i

                sheet.write(row, col_index_2, "-", cell_format)
                sheet.write(row + 1, col_index_2, "-", cell_format)
                sheet.write(row + 2, col_index_2, "-", cell_format)

                sheet.write(row, col_index_3, "-", cell_format)
                sheet.write(row + 1, col_index_3, "-", cell_format)
                sheet.write(row + 2, col_index_3, "-", cell_format)

                sheet.write(row, col_index_4, "-", cell_format)
                sheet.write(row + 1, col_index_4, "-", cell_format)
                sheet.write(row + 2, col_index_4, "-", cell_format)

                sheet.write(row, col_index_5, "-", cell_format)
                sheet.write(row + 1, col_index_5, "-", cell_format)
                sheet.write(row + 2, col_index_5, "-", cell_format)

                sheet.write(row, col_index_6, "-", cell_format)
                sheet.write(row + 1, col_index_6, "-", cell_format)
                sheet.write(row + 2, col_index_6, "-", cell_format)

                sheet.write(row, col_index_7, "-", cell_format)
                sheet.write(row + 1, col_index_7, "-", cell_format)
                sheet.write(row + 2, col_index_7, "-", cell_format)

                sheet.write(row, col_index_8, "-", cell_format)
                sheet.write(row + 1, col_index_8, "-", cell_format)
                sheet.write(row + 2, col_index_8, "-", cell_format)

                total_column_index_2 = jumlah_hasil_sadapan_lateks
                total_column_index_3 = jumlah_hasil_sadapan_lump
                total_column_index_6 = jumlah_hasil_konversi_lateks
                total_column_index_7 = jumlah_hasil_konversi_lump
                total_column_index_8 = jumlah_total_konversi

                sheet.write(row, total_column_index_2, "-", wbf['data_center'])
                sheet.write(row + 1, total_column_index_2, "-", wbf['data_center'])
                sheet.write(row + 2, total_column_index_2, "-", wbf['data_center'])

                sheet.write(row, total_column_index_3, "-", wbf['data_center'])
                sheet.write(row + 1, total_column_index_3, "-", wbf['data_center'])
                sheet.write(row + 2, total_column_index_3, "-", wbf['data_center'])

                sheet.write(row, total_column_index_6, "-", wbf['data_center'])
                sheet.write(row + 1, total_column_index_6, "-", wbf['data_center'])
                sheet.write(row + 2, total_column_index_6, "-", wbf['data_center'])

                sheet.write(row, total_column_index_7, "-", wbf['data_center'])
                sheet.write(row + 1, total_column_index_7, "-", wbf['data_center'])
                sheet.write(row + 2, total_column_index_7, "-", wbf['data_center'])

                sheet.write(row, total_column_index_8, "-", wbf['data_center'])
                sheet.write(row + 1, total_column_index_8, "-", wbf['data_center'])
                sheet.write(row + 2, total_column_index_8, "-", wbf['data_center'])
            row += 4

            # Line Total Paling Bawah
            sheet.merge_range(row, 0, row, 4, "JUMLAH TOTAL", wbf['jumlah_total'])
            
            total_attendance = 0
            grandtotal_hasil_1 = 0 
            grandtotal_hasil_2 = 0 
            grandtotal_chasil_1 = 0 
            grandtotal_chasil_2 = 0 
            grandtotal_konversi = 0 
            for line in list_hasil_1:
                attendance_count = line.get("attendance_count", 0)
                total_hasil_1_tanggal = line.get("total_hasil_1_nap", 0)
                total_attendance += attendance_count

                sheet.write(row, hko_start, total_attendance, wbf['hijau_tua'])
                sheet.write(row, hko_start + 1, 0, wbf['hijau_tua'])
                sheet.write(row, hko_start + 2, 0, wbf['hijau_tua'])
                sheet.write(row, hko_start + 3, 0, wbf['hijau_tua'])
                sheet.write(row, hko_start + 4, 0, wbf['hijau_tua'])
                sheet.write(row, hko_start + 5, 0, wbf['hijau_tua'])
                sheet.write(row, hko_start + 6, total_attendance, wbf['hijau_tua'])

            for i, date_str in enumerate(date_columns):
                total_kj = total_kj_per_date.get(date_str, 0)
                sheet.write(row, start_col + i, total_kj, wbf['kuning'])

            for i, date_str in enumerate(date_columns):
                total_hasil_1 = total_hasil_1_per_tanggal.get(date_str, 0)
                grandtotal_hasil_1 += total_hasil_1
                sheet.write(row, second_date_start - 1, grandtotal_hasil_1, wbf['hijau_tua'])
                sheet.write(row, second_date_start + i, total_hasil_1, wbf['kuning'])

            for i, date_str in enumerate(date_columns):
                total_hasil_2 = total_hasil_2_per_tanggal.get(date_str, 0)
                grandtotal_hasil_2 += total_hasil_2
                sheet.write(row, third_date_start - 1, grandtotal_hasil_2, wbf['hijau_tua'])
                sheet.write(row, third_date_start + i, total_hasil_2, wbf['kuning'])

            for i, date_str in enumerate(date_columns):
                total_chasil_1 = total_chasil_1_per_tanggal.get(date_str, 0)
                grandtotal_chasil_1 += total_chasil_1
                sheet.write(row, sixth_date_start - 1, grandtotal_chasil_1, wbf['hijau_tua'])
                sheet.write(row, sixth_date_start + i, total_chasil_1, wbf['kuning'])

            for i, date_str in enumerate(date_columns):
                total_chasil_2 = total_chasil_2_per_tanggal.get(date_str, 0)
                grandtotal_chasil_2 += total_chasil_2
                sheet.write(row, seventh_date_start - 1, grandtotal_chasil_2, wbf['hijau_tua'])
                sheet.write(row, seventh_date_start + i, total_chasil_2, wbf['kuning'])

            for i, date_str in enumerate(date_columns):
                total_konversi = total_convert_per_tanggal.get(date_str, 0)
                grandtotal_konversi += total_konversi
                sheet.write(row, eighth_date_start - 1, grandtotal_konversi, wbf['hijau_tua'])
                sheet.write(row, eighth_date_start + i, total_konversi, wbf['kuning'])
            
            row += 5


    def generate_xlsx_report_old(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        from_date = obj.from_date
        to_date = obj.to_date
        kemandoran_ids = obj.kemandoran_id

        if not kemandoran_ids:
            kemandoran_ids = self.env['hr.foreman'].search([])
        
        sheet  = workbook.add_worksheet("Laporan Produksi Karet Detail")
        row = 0


        for kemandoran in kemandoran_ids:

            # Judul Laporan
            sheet.write(row, 0, 'Laporan Produksi Karet Detail')
            row += 1
            sheet.write(row, 0,'BULAN')
            sheet.write(row, 1,':', wbf['content_center'])
            sheet.write(row, 2,f'{from_date.strftime("%d-%m-%Y")} s/d {to_date.strftime("%d-%m-%Y")}' if from_date and to_date else '')
            row += 2
            # Bagian Header 1
            sheet.merge_range(row, 0, row + 1, 4, kemandoran.name or '', wbf['kemandoran'])

            if from_date and to_date:
                delta = to_date - from_date
                date_columns = []
                for i in range(delta.days + 1):
                    current_date = from_date + timedelta(days=i)
                    date_columns.append(current_date.strftime('%d'))

                hko_start = 5
                sheet.merge_range(row, hko_start, row + 1, hko_start + 5, 'JUMLAH HKO', wbf['header'])

                total_hk_start = hko_start + 6
                sheet.merge_range(row, total_hk_start, row + 2, total_hk_start, 'TOTAL HK', wbf['header'])

                start_col = total_hk_start + 1
                end_col = start_col + len(date_columns) - 1
                sheet.merge_range(row, start_col, row + 1, end_col, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    sheet.write(row + 2, start_col + i, date, wbf['header'])
                    sheet.set_column(start_col + i, start_col + i, 5)

            #lateks
            if from_date and to_date:
                jumlah_hasil_sadapan_lateks = end_col + 2
                sheet.merge_range(row, jumlah_hasil_sadapan_lateks, row + 1, jumlah_hasil_sadapan_lateks, 'JUMLAH HASIL SADAPAN', wbf['header'])
                
                second_date_start = jumlah_hasil_sadapan_lateks + 1
                second_date_end = second_date_start + len(date_columns) - 1
                sheet.merge_range(row, second_date_start, row + 1, second_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = second_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #lump
            if from_date and to_date:
                jumlah_hasil_sadapan_lump = second_date_end + 2
                sheet.merge_range(row, jumlah_hasil_sadapan_lump, row + 1, jumlah_hasil_sadapan_lump, 'JUMLAH HASIL SADAPAN', wbf['header'])
                
                third_date_start = jumlah_hasil_sadapan_lump + 1
                third_date_end = third_date_start + len(date_columns) - 1
                sheet.merge_range(row, third_date_start, row + 1, third_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = third_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #drc lateks
            if from_date and to_date:
                fourth_date_start = third_date_end + 2
                fourth_date_end = fourth_date_start + len(date_columns) - 1
                sheet.merge_range(row, fourth_date_start, row, fourth_date_end, 'DRC LATEKS', wbf['header'])
                sheet.merge_range(row + 1, fourth_date_start, row + 1, fourth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fourth_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #drc lump
            if from_date and to_date:
                fifth_date_start = fourth_date_end + 2
                fifth_date_end = fifth_date_start + len(date_columns) - 1
                sheet.merge_range(row, fifth_date_start, row, fifth_date_end, 'DRC LUMP', wbf['header'])
                sheet.merge_range(row + 1, fifth_date_start, row + 1, fifth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fifth_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)
            
            #konversi lateks
            if from_date and to_date:
                jumlah_hasil_konversi_lateks = fifth_date_end + 2
                sheet.merge_range(row, jumlah_hasil_konversi_lateks, row + 1, jumlah_hasil_konversi_lateks, 'JUMLAH HASIL KONVERSI', wbf['header'])
                
                sixth_date_start = jumlah_hasil_konversi_lateks + 1
                sixth_date_end = sixth_date_start + len(date_columns) - 1
                sheet.merge_range(row, sixth_date_start, row + 1, sixth_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = sixth_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #konversi lump
            if from_date and to_date:
                jumlah_hasil_konversi_lump = sixth_date_end + 2
                sheet.merge_range(row, jumlah_hasil_konversi_lump, row + 1, jumlah_hasil_konversi_lump, 'JUMLAH HASIL KONVERSI', wbf['header'])
                
                seventh_date_start = jumlah_hasil_konversi_lump + 1
                seventh_date_end = seventh_date_start + len(date_columns) - 1
                sheet.merge_range(row, seventh_date_start, row + 1, seventh_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = seventh_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            #total konversi lateks + lump
            if from_date and to_date:
                jumlah_total_konversi = seventh_date_end + 2
                sheet.merge_range(row, jumlah_total_konversi, row + 1, jumlah_total_konversi, 'TOTAL HASIL KONVERSI', wbf['header'])
                
                eighth_date_start = jumlah_total_konversi + 1
                eighth_date_end = eighth_date_start + len(date_columns) - 1
                sheet.merge_range(row, eighth_date_start, row + 1, eighth_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = eighth_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            # Header 2
            sheet.write(row + 2, 0, 'NO.', wbf['header'])
            sheet.set_column(5, 0, 7)
            sheet.write(row + 2, 1,'NIK', wbf['header'])
            sheet.set_column(5, 1, 13)
            sheet.write(row + 2, 2,'NAMA', wbf['header'])
            sheet.set_column(5, 2, 13)
            sheet.write(row + 2, 3, 'KEMANDORAN', wbf['header'])
            sheet.set_column(5, 3, 13)
            sheet.write(row + 2, 4, 'LOKASI',  wbf['header'])
            sheet.set_column(5, 4, 16)

            hko_headers = ['HKO', 'L', 'S', 'P', 'CT', 'M']
            hko_formats = [self.wbf['biru_muda'], self.wbf['hijau_tua'], self.wbf['kuning'], self.wbf['biru_tua'], self.wbf['biru_muda'], self.wbf['merah']]

            for i, header in enumerate(hko_headers):
                sheet.write(row + 2, hko_start + i, header, hko_formats[i])
            
            lateks_row_start = row + 2
            lateks_col_start = jumlah_hasil_sadapan_lateks
            sheet.write(lateks_row_start, lateks_col_start, 'LATEKS (L)', wbf['header'])

            lump_row_start = row + 2
            lump_col_start = jumlah_hasil_sadapan_lump
            sheet.write(lump_row_start, lump_col_start, 'LUMP (Kg)', wbf['header'])

            clateks_row_start = row + 2
            clateks_col_start = jumlah_hasil_konversi_lateks
            sheet.write(clateks_row_start, clateks_col_start, 'LATEKS (Kg)', wbf['header'])

            clump_row_start = row + 2
            clump_col_start = jumlah_hasil_konversi_lump
            sheet.write(clump_row_start, clump_col_start, 'LUMP (Kg)', wbf['header'])

            tkonversi_row_start = row + 2
            tkonversi_col_start = jumlah_total_konversi
            sheet.write(tkonversi_row_start, tkonversi_col_start, 'KARET (Kg)', wbf['header'])

            # Bagian Isi Data
            query = """
                WITH employee_data AS (
                    SELECT 
                        emp.id AS emp_id,
                        emp.name AS employee_name,
                        emp.kemandoran_id AS kemandoran_emp,
                        emp.no_induk as no_induk
                    FROM 
                        hr_employee emp
                    WHERE 
                        emp.kemandoran_id = %s
                        AND emp.active = TRUE
                ),
                trans_data AS (
                    SELECT 
                        trans_nap_line.hasil_1_nap,
                        trans_nap_line.hasil_2_nap,
                        trans_nap_line.hasil_convert_latex,
                        trans_nap_line.hasil_convert_lump,
                        trans_line.work_day,  
                        trans.date, 
                        trans_line.employee_id,
                        trans_line.location_id
                    FROM 
                        lhm_transaction_nap_line trans_nap_line
                    JOIN 
                        lhm_transaction_line trans_line ON trans_line.id = trans_nap_line.lhm_transaction_line_id
                    JOIN 
                        lhm_transaction trans ON trans.id = trans_line.lhm_id
                    WHERE 
                        trans.date BETWEEN %s AND %s
                )
                SELECT 
                    employee_data.emp_id,
                    employee_data.no_induk,
                    employee_data.employee_name,
                    employee_data.kemandoran_emp,
                    trans_data.location_id,
                    SUM(trans_data.work_day) AS total_work_day
                FROM 
                    employee_data
                LEFT JOIN 
                    trans_data ON employee_data.emp_id = trans_data.employee_id
                GROUP BY 
                    employee_data.emp_id,
                    employee_data.no_induk,
                    employee_data.kemandoran_emp, 
                    employee_data.employee_name,
                    trans_data.location_id,
                    trans_data.work_day
                ORDER BY 
                    employee_data.employee_name ASC,
                    trans_data.location_id ASC;
            """
            # query = """SELECT 
            #         ltl.employee_id,
            #         he.no_induk,
            #         he.name,
            #         lt.kemandoran_id,
            #         ltl.location_id
            #     FROM lhm_transaction_line ltl 
            #         inner join hr_employee he ON he.id=ltl.employee_id
            #         inner join lhm_transaction lt ON lt.id=ltl.lhm_id
            #         inner join lhm_transaction_nap_line ltnl ON ltnl.lhm_transaction_line_id=ltl.id
            #     WHERE lt.kemandoran_id = %s and ltl.date between %s and %s
            #     ORDER BY ltl.employee_id ASC, ltl.location_id ASC;"""

            self.env.cr.execute(query, (kemandoran.id, from_date, to_date))
            karyawan_data = self.env.cr.fetchall()

            row += 4
            nomor = 1

            mandor_name = kemandoran.kepala_mandor_id.sudo().name if kemandoran.kepala_mandor_id else ''
            mandor_nik = kemandoran.kepala_mandor_id.sudo().no_induk if kemandoran.kepala_mandor_id else ''
            asisten_mandor_name = kemandoran.mandor_id.sudo().name if kemandoran.mandor_id else ''
            asisten_mandor_nik = kemandoran.mandor_id.sudo().no_induk if kemandoran.mandor_id else ''
            kerani_name = kemandoran.assisten_id.sudo().name if kemandoran.assisten_id else ''
            kerani_nik = kemandoran.assisten_id.sudo().no_induk if kemandoran.assisten_id else ''

            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                sheet.write(row, 0, nomor, wbf['data_center'])
                sheet.write(row, 1, no_induk, wbf['data_center'])
                sheet.write(row, 2, employee_name, wbf['data'])
                kemandoran_name = self.env['hr.foreman'].browse(kemandoran_emp).name if kemandoran_emp else '-'
                sheet.write(row, 3, kemandoran_name, wbf['data'])
                location_name = self.env['lhm.location'].browse(location_id).name if location_id else '-'
                sheet.write(row, 4, location_name, wbf['data'])

                current_col = 12
                hko_count = 0
                l_count = 0
                s_count = 0
                p_count = 0
                ct_count = 0
                m_count = 0

                for i in range(delta.days + 1):
                    attendance = self.env['lhm.transaction.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                        ('location_id', '=', location_id)
                    ], fields=['attendance_id'], limit=1)

                    type_code = attendance[0]['attendance_id'][1] if attendance else '-'
                    sheet.write(row, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet.write(row, current_col, type_code, wbf['hijau_muda'])
                        hko_count += 1
                    elif type_code == 'NA':
                        sheet.write(row, current_col, type_code, wbf['hijau_tua'])
                        l_count += 1
                    elif type_code == 'S1':
                        sheet.write(row, current_col, type_code, wbf['kuning'])
                        s_count += 1
                    elif type_code == 'P1':
                        sheet.write(row, current_col, type_code, wbf['biru_tua'])
                        p_count += 1
                    elif type_code == 'CT':
                        sheet.write(row, current_col, type_code, wbf['biru_muda'])
                        ct_count += 1
                    elif type_code == 'M':
                        sheet.write(row, current_col, type_code, wbf['merah'])
                        m_count += 1
                    elif type_code is None:
                        sheet.write(row, current_col, '-', wbf['content_center'])
                        m_count += 1

                    current_col += 1

                sheet.write(row, hko_start, hko_count, wbf['biru_muda'])
                sheet.write(row, hko_start + 1, l_count, wbf['data_center'])
                sheet.write(row, hko_start + 2, s_count, wbf['data_center'])
                sheet.write(row, hko_start + 3, p_count, wbf['data_center'])
                sheet.write(row, hko_start + 4, ct_count, wbf['data_center'])
                sheet.write(row, hko_start + 5, m_count, wbf['data_center'])
                sheet.write(row, total_hk_start, '-', wbf['data_center'])

                # Isi Jumlah Hasil Sadapan Lateks (L)
                total_hasil_baris_lateks = 0
                
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = second_date_start + i
                    
                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_1_nap'], limit=1)
                    
                    if nap_line:
                        total_hasil_baris_lateks += float(nap_line[0]['hasil_1_nap'])
                        sheet.write(row, col_index, nap_line[0]['hasil_1_nap'], wbf['total_float'])
                    else:
                        sheet.write(row, col_index, 0, wbf['total_float'])
                
                total_column_index = jumlah_hasil_sadapan_lateks
                sheet.write(row, total_column_index, total_hasil_baris_lateks, wbf['total_float'])

                # Isi Jumlah Hasil Sadapan Lump (Kg)
                total_hasil_baris_lump = 0
                
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = third_date_start + i
                    
                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_2_nap'], limit=1)
                    
                    if nap_line:
                        total_hasil_baris_lump += float(nap_line[0]['hasil_2_nap'])
                        sheet.write(row, col_index, nap_line[0]['hasil_2_nap'], wbf['total_float'])
                    else:
                        sheet.write(row, col_index, 0, wbf['total_float'])
                
                total_column_index = jumlah_hasil_sadapan_lump
                sheet.write(row, total_column_index, total_hasil_baris_lump, wbf['total_float'])

                # Isi Data DRC Lateks (L)
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = fourth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['drc_latex_nap'], limit=1)

                    drc_lateks = nap_line[0]['drc_latex_nap'] if nap_line else '-'
                    cell_format = wbf['data_center']
                    sheet.write(row, col_index, drc_lateks, cell_format)

                # Isi Data DRC Lump (Kg)
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = fifth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['drc_lump_nap'], limit=1)

                    drc_lateks = nap_line[0]['drc_lump_nap'] if nap_line else '-'
                    cell_format = wbf['data_center']
                    sheet.write(row, col_index, drc_lateks, cell_format)

                # Isi Jumlah Hasil Konversi Lateks (L)
                total_hasil_konversi_lateks = 0
                
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = sixth_date_start + i
                    
                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_convert_latex'], limit=1)
                    
                    if nap_line:
                        total_hasil_konversi_lateks += float(nap_line[0]['hasil_convert_latex'])
                        sheet.write(row, col_index, nap_line[0]['hasil_convert_latex'], wbf['total_float'])
                    else:
                        sheet.write(row, col_index, 0, wbf['total_float'])
                
                total_column_index = jumlah_hasil_konversi_lateks
                sheet.write(row, total_column_index, total_hasil_konversi_lateks, wbf['total_float'])

                # Isi Jumlah Hasil Konversi Lump (Kg)
                total_hasil_konversi_lump = 0
                
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = seventh_date_start + i
                    
                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_convert_lump'],limit=1)
                    
                    if nap_line:
                        total_hasil_konversi_lump += float(nap_line[0]['hasil_convert_lump'])
                        sheet.write(row, col_index, nap_line[0]['hasil_convert_lump'], wbf['total_float'])
                    else:
                        sheet.write(row, col_index, 0, wbf['total_float'])
                
                total_column_index = jumlah_hasil_konversi_lump
                sheet.write(row, total_column_index, total_hasil_konversi_lump, wbf['total_float'])

                # Jumlahkan hasil konversi Lateks + Lump
                total_konversi_lateks_lump = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = eighth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_convert_latex', 'hasil_convert_lump'], limit=1)

                    if nap_line:
                        hasil_lateks = float(nap_line[0].get('hasil_convert_latex', 0))
                        hasil_lump = float(nap_line[0].get('hasil_convert_lump', 0))
                        total_hasil = hasil_lateks + hasil_lump

                        total_konversi_lateks_lump += total_hasil
                        sheet.write(row, col_index, total_hasil, wbf['total_float'])
                    else:
                        sheet.write(row, col_index, 0, wbf['total_float'])

                total_column_index = jumlah_total_konversi
                sheet.write(row, total_column_index, total_konversi_lateks_lump, wbf['total_float'])

                row += 1
                nomor += 1

            # Logika untuk Mandor
            row += 1
            sheet.write(row, 0, "M-1", wbf['data_center'])
            sheet.write(row, 1, mandor_nik, wbf['data'])
            sheet.write(row, 2, mandor_name, wbf['data'])
            sheet.write(row, 3, kemandoran_name, wbf['data'])
            sheet.write(row, 4, "-", wbf['data'])

            mandor_employee = self.env['hr.employee'].sudo().search([('name', '=', mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', mandor_employee.id),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)

                sheet.write(row, 12 + i, "-", wbf['data_center'])

            sheet.write(row, hko_start, "-", wbf['biru_muda'])
            sheet.write(row, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row, total_hk_start, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_sadapan_lateks
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_sadapan_lump
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Data DRC Lateks (L)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            # Isi Data DRC Lump (Kg)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            # Isi Jumlah Hasil Konversi Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_konversi_lateks
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_konversi_lump
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Jumlahkan hasil konversi Lateks + Lump
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = eighth_date_start + i

                sheet.write(row, col_index, '-', wbf['data_center'])

            total_column_index = jumlah_total_konversi
            sheet.write(row, total_column_index, '-', wbf['data_center'])

            # Logika untuk Asisten Mandor
            row += 1
            sheet.write(row, 0, "M-2", wbf['data_center'])
            sheet.write(row, 1, asisten_mandor_nik, wbf['data'])
            sheet.write(row, 2, asisten_mandor_name, wbf['data'])
            sheet.write(row, 3, kemandoran_name, wbf['data'])
            sheet.write(row, 4, "-", wbf['data'])

            asisten_employee = self.env['hr.employee'].sudo().search([('name', '=', asisten_mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', asisten_employee.id),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)

                sheet.write(row, 12 + i, "-", wbf['data_center'])

            sheet.write(row, hko_start, "-", wbf['biru_muda'])
            sheet.write(row, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row, total_hk_start, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_sadapan_lateks
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_sadapan_lump
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Data DRC Lateks (L)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            # Isi Data DRC Lump (Kg)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            # Isi Jumlah Hasil Konversi Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_konversi_lateks
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_konversi_lump
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Jumlahkan hasil konversi Lateks + Lump
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = eighth_date_start + i

                sheet.write(row, col_index, '-', wbf['data_center'])

            total_column_index = jumlah_total_konversi
            sheet.write(row, total_column_index, '-', wbf['data_center'])

            # Logika untuk Kerani
            row += 1
            sheet.write(row, 0, "M-3", wbf['data_center'])
            sheet.write(row, 1, kerani_nik, wbf['data'])
            sheet.write(row, 2, kerani_name, wbf['data'])
            sheet.write(row, 3, kemandoran_name, wbf['data'])
            sheet.write(row, 4, "-", wbf['data'])

            kerani_employee = self.env['hr.employee'].sudo().search([('name', '=', kerani_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', kerani_employee.id),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)

                sheet.write(row, 12 + i, "-", wbf['data_center'])

            sheet.write(row, hko_start, "-", wbf['biru_muda'])
            sheet.write(row, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row, total_hk_start, '-', wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_sadapan_lateks
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_sadapan_lump
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Data DRC Lateks (L)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            # Isi Data DRC Lump (Kg)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            # Isi Jumlah Hasil Konversi Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_konversi_lateks
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                sheet.write(row, col_index, "-", cell_format)

            total_column_index = jumlah_hasil_konversi_lump
            sheet.write(row, total_column_index, "-", wbf['data_center'])

            # Jumlahkan hasil konversi Lateks + Lump
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = eighth_date_start + i

                sheet.write(row, col_index, '-', wbf['data_center'])

            total_column_index = jumlah_total_konversi
            sheet.write(row, total_column_index, '-', wbf['data_center'])

            row += 1
            nomor += 1

            # 1
            row += 1
            total_hko_per_tanggal = [0] * len(date_columns)
            total_l_per_tanggal = [0] * len(date_columns)
            total_s_per_tanggal = [0] * len(date_columns)
            total_p_per_tanggal = [0] * len(date_columns)
            total_ct_per_tanggal = [0] * len(date_columns)
            total_m_per_tanggal = [0] * len(date_columns)

            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                current_col = 5
                for i in range(len(date_columns)):
                    attendance = self.env['lhm.transaction.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                        ('location_id', '=', location_id)
                    ], fields=['attendance_id'], limit=1)

                    type_code = attendance[0]['attendance_id'][1] if attendance else '-'
                    if type_code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

            for i in range(len(date_columns)):
                sheet.write(row, 12 + i, total_hko_per_tanggal[i], wbf['kuning'])

            #2
            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                current_col = 5
                for i in range(len(date_columns)):
                    attendance = self.env['lhm.transaction.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                        ('location_id', '=', location_id)
                    ], fields=['attendance_id'], limit=1)

                    type_code = attendance[0]['attendance_id'][1] if attendance else '-'
                    if type_code == 'KJ':
                        total_hko_per_tanggal[i] += 1
                    elif type_code == 'NA':
                        total_l_per_tanggal[i] += 1
                    elif type_code == 'S1':
                        total_s_per_tanggal[i] += 1
                    elif type_code == 'P1':
                        total_p_per_tanggal[i] += 1
                    elif type_code == 'CT':
                        total_ct_per_tanggal[i] += 1
                    elif type_code == 'M':
                        total_m_per_tanggal[i] += 1

            sheet.merge_range(row, 0, row, 4, "JUMLAH TOTAL", wbf['jumlah_total'])
            sheet.write(row, hko_start, sum(total_hko_per_tanggal) * 0.5, wbf['hijau_tua'])
            sheet.write(row, hko_start + 1, sum(total_l_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 2, sum(total_s_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 3, sum(total_p_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 4, sum(total_ct_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 5, sum(total_m_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, total_hk_start, '', wbf['hijau_tua'])

            #3
            total_keseluruhan_hasil_lateks = 0
            total_per_tanggal_lateks = {}

            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = second_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_1_nap'], limit=1)

                    hasil_nap_lateks = nap_lines[0]['hasil_1_nap'] if nap_lines else '-'

                    if hasil_nap_lateks and hasil_nap_lateks != '-':
                        hasil_nap_lateks_float = float(hasil_nap_lateks)
                        total_keseluruhan_hasil_lateks += hasil_nap_lateks_float
                        total_per_tanggal_lateks[current_date] = total_per_tanggal_lateks.get(current_date, 0) + hasil_nap_lateks_float
                        cell_format = wbf['kuning']
                    else:
                        hasil_nap_lateks_float = 0
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_lateks.get(current_date, 0), cell_format)

                total_column_index = jumlah_hasil_sadapan_lateks
                sheet.write(row, total_column_index, total_keseluruhan_hasil_lateks if total_keseluruhan_hasil_lateks > 0 else '-', wbf['hijau_tua'])

            #4
            total_keseluruhan_hasil_lump = 0
            total_per_tanggal_lump = {}
            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = third_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_2_nap'], limit=1)

                    hasil_nap_lump = nap_lines[0]['hasil_2_nap'] if nap_lines else '-'

                    if hasil_nap_lump and hasil_nap_lump != '-':
                        hasil_nap_lump_float = float(hasil_nap_lump)
                        total_keseluruhan_hasil_lump += hasil_nap_lump_float
                        total_per_tanggal_lump[current_date] = total_per_tanggal_lump.get(current_date, 0) + hasil_nap_lump_float
                        cell_format = wbf['kuning']
                    else:
                        hasil_nap_lump_float = 0
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_lump.get(current_date, 0), cell_format)

                total_column_index = jumlah_hasil_sadapan_lump
                sheet.write(row, total_column_index, total_keseluruhan_hasil_lump if total_keseluruhan_hasil_lump > 0 else '-', wbf['hijau_tua'])

            #7
            total_keseluruhan_konversi_lateks = 0
            total_per_tanggal_konversi_lateks = {}
            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = sixth_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_convert_latex'], limit=1)

                    hasil_nap_lateks = nap_lines[0]['hasil_convert_latex'] if nap_lines else '-'

                    if hasil_nap_lateks and hasil_nap_lateks != '-':
                        hasil_nap_lateks_float = float(hasil_nap_lateks)
                        total_keseluruhan_konversi_lateks += hasil_nap_lateks_float
                        total_per_tanggal_konversi_lateks[current_date] = total_per_tanggal_konversi_lateks.get(current_date, 0) + hasil_nap_lateks_float
                        cell_format = wbf['kuning']
                    else:
                        hasil_nap_lateks_float = 0
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_konversi_lateks.get(current_date, 0), cell_format)

                total_column_index = jumlah_hasil_konversi_lateks
                sheet.write(row, total_column_index, total_keseluruhan_konversi_lateks if total_keseluruhan_konversi_lateks > 0 else '-', wbf['hijau_tua'])

            #8
            total_keseluruhan_konversi_lump = 0
            total_per_tanggal_konversi_lump = {}
            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = seventh_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_convert_lump'], limit=1)

                    hasil_nap_lateks = nap_lines[0]['hasil_convert_lump'] if nap_lines else '-'

                    if hasil_nap_lateks and hasil_nap_lateks != '-':
                        hasil_nap_lateks_float = float(hasil_nap_lateks)
                        total_keseluruhan_konversi_lump += hasil_nap_lateks_float
                        total_per_tanggal_konversi_lump[current_date] = total_per_tanggal_konversi_lump.get(current_date, 0) + hasil_nap_lateks_float
                        cell_format = wbf['kuning']
                    else:
                        hasil_nap_lateks_float = 0
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_konversi_lump.get(current_date, 0), cell_format)

                total_column_index = jumlah_hasil_konversi_lump
                sheet.write(row, total_column_index, total_keseluruhan_konversi_lump if total_keseluruhan_konversi_lump > 0 else '-', wbf['hijau_tua'])

            #9
            total_keseluruhan_konversi_total = 0
            total_per_tanggal_konversi_total = {}

            for emp_id, no_induk, employee_name, kemandoran_emp, location_id, total_work_day in karyawan_data:
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = eighth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search_read([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], ['hasil_convert_latex', 'hasil_convert_lump'], limit=1)

                    hasil_nap_lateks = float(nap_line[0].get('hasil_convert_latex', 0)) if nap_line else 0
                    hasil_nap_lump = float(nap_line[0].get('hasil_convert_lump', 0)) if nap_line else 0

                    total_hasil = hasil_nap_lateks + hasil_nap_lump
                    total_keseluruhan_konversi_total += total_hasil
                    total_per_tanggal_konversi_total[current_date] = total_per_tanggal_konversi_total.get(current_date, 0) + total_hasil

                    cell_format = wbf['kuning'] if total_hasil > 0 else wbf['kuning']
                    sheet.write(row, col_index, total_per_tanggal_konversi_total[current_date], cell_format)

            total_column_index = jumlah_total_konversi
            sheet.write(row, total_column_index, total_keseluruhan_konversi_total if total_keseluruhan_konversi_total > 0 else '-', wbf['hijau_tua'])

            row += 4
