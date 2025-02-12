from odoo import models
from datetime import datetime, timedelta

class ReportProductionKebun(models.AbstractModel):
    _name = 'report.nyalindung_report.production_kebun_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Production Kebun Excel"

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

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        from_date = obj.from_date
        to_date = obj.to_date
        kemandoran_ids = obj.kemandoran_id

        if not kemandoran_ids:
            kemandoran_ids = self.env['hr.foreman'].search([])
        
        sheet3 = workbook.add_worksheet("Laporan Produksi Karet Per Kebun")
        row3 = 0

        for kemandoran in kemandoran_ids:
            sheet3.write(row3, 0, 'Laporan Produksi Per Kebun')
            row3 += 1
            sheet3.write(row3, 0,'BULAN')
            sheet3.write(row3, 1,':', wbf['content_center'])
            sheet3.write(row3, 2,f'{from_date.strftime("%d-%m-%Y")} s/d {to_date.strftime("%d-%m-%Y")}' if from_date and to_date else '')

            row3 += 2
            # Bagian Header 1
            sheet3.merge_range(row3, 0, row3 + 1, 2, kemandoran.name or '', wbf['kemandoran'])
            
            if from_date and to_date:
                delta = to_date - from_date
                date_columns = []
                for i in range(delta.days + 1):
                    current_date = from_date + timedelta(days=i)
                    date_columns.append(current_date.strftime('%d'))

            if from_date and to_date:
                jumlah_hasil_sadapan_lateks = 4
                sheet3.merge_range(row3, jumlah_hasil_sadapan_lateks, row3 + 1, jumlah_hasil_sadapan_lateks, 'JUMLAH HASIL SADAPAN', wbf['header'])
                
                second_date_start = jumlah_hasil_sadapan_lateks + 1
                second_date_end = second_date_start + len(date_columns) - 1
                
                sheet3.merge_range(row3, second_date_start, row3 + 1, second_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = second_date_start + i
                    sheet3.write(row3 + 2, col_index, date, wbf['header'])
                    sheet3.set_column(col_index, col_index, 5)

            if from_date and to_date:
                jumlah_hasil_sadapan_lump = second_date_end + 2
                sheet3.merge_range(row3, jumlah_hasil_sadapan_lump, row3 + 1, jumlah_hasil_sadapan_lump, 'JUMLAH HASIL SADAPAN', wbf['header'])
                
                third_date_start = jumlah_hasil_sadapan_lump + 1
                third_date_end = third_date_start + len(date_columns) - 1
                
                sheet3.merge_range(row3, third_date_start, row3 + 1, third_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = third_date_start + i
                    sheet3.write(row3 + 2, col_index, date, wbf['header'])
                    sheet3.set_column(col_index, col_index, 5)

            if from_date and to_date:
                average_drc_lateks = third_date_end + 2
                sheet3.merge_range(row3, average_drc_lateks, row3 + 1, average_drc_lateks, 'DRC SHI Avg.', wbf['header'])

                fourth_date_start = average_drc_lateks + 1
                fourth_date_end = fourth_date_start + len(date_columns) - 1
                sheet3.merge_range(row3, fourth_date_start, row3, fourth_date_end, 'DRC LATEKS', wbf['header'])
                sheet3.merge_range(row3 + 1, fourth_date_start, row3 + 1, fourth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fourth_date_start + i
                    sheet3.write(row3 + 2, col_index, date, wbf['header'])
                    sheet3.set_column(col_index, col_index, 5)

            if from_date and to_date:
                average_drc_lump = fourth_date_end + 2
                sheet3.merge_range(row3, average_drc_lump, row3 + 1, average_drc_lump, 'DRC SHI Avg.', wbf['header'])
                
                fifth_date_start = average_drc_lump + 1
                fifth_date_end = fifth_date_start + len(date_columns) - 1
                sheet3.merge_range(row3, fifth_date_start, row3, fifth_date_end, 'DRC LUMP', wbf['header'])
                sheet3.merge_range(row3 + 1, fifth_date_start, row3 + 1, fifth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fifth_date_start + i
                    sheet3.write(row3 + 2, col_index, date, wbf['header'])
                    sheet3.set_column(col_index, col_index, 5)
            
            if from_date and to_date:
                jumlah_hasil_konversi_lateks = fifth_date_end + 2
                sheet3.merge_range(row3, jumlah_hasil_konversi_lateks, row3 + 1, jumlah_hasil_konversi_lateks, 'JUMLAH HASIL KONVERSI', wbf['header'])
                
                sixth_date_start = jumlah_hasil_konversi_lateks + 1
                sixth_date_end = sixth_date_start + len(date_columns) - 1

                sheet3.merge_range(row3, sixth_date_start, row3 + 1, sixth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = sixth_date_start + i
                    sheet3.write(row3 + 2, col_index, date, wbf['header'])
                    sheet3.set_column(col_index, col_index, 5)

            if from_date and to_date:
                jumlah_hasil_konversi_lump = sixth_date_end + 2
                sheet3.merge_range(row3, jumlah_hasil_konversi_lump, row3 + 1, jumlah_hasil_konversi_lump, 'JUMLAH HASIL KONVERSI', wbf['header'])
                
                seventh_date_start = jumlah_hasil_konversi_lump + 1
                seventh_date_end = seventh_date_start + len(date_columns) - 1

                sheet3.merge_range(row3, seventh_date_start, row3 + 1, seventh_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = seventh_date_start + i
                    sheet3.write(row3 + 2, col_index, date, wbf['header'])
                    sheet3.set_column(col_index, col_index, 5)

            if from_date and to_date:
                jumlah_total_konversi = seventh_date_end + 2
                sheet3.merge_range(row3, jumlah_total_konversi, row3 + 1, jumlah_total_konversi, 'TOTAL HASIL KONVERSI', wbf['header'])
                
                eighth_date_start = jumlah_total_konversi + 1
                eighth_date_end = eighth_date_start + len(date_columns) - 1
                sheet3.merge_range(row3, eighth_date_start, row3 + 1, eighth_date_end, 'TANGGAL', wbf['header'])
                
                for i, date in enumerate(date_columns):
                    col_index = eighth_date_start + i
                    sheet3.write(row3 + 2, col_index, date, wbf['header'])
                    sheet3.set_column(col_index, col_index, 5)


            # Header 2
            sheet3.write(row3 + 2, 0, 'NO.', wbf['header'])
            sheet3.set_column(5, 0, 7)
            sheet3.write(row3 + 2, 1, 'LOKASI', wbf['header'])
            sheet3.set_column(5, 1, 16)
            sheet3.write(row3 + 2, 2, 'TOTAL HK', wbf['header'])
            
            lateks_row3_start = row3 + 2
            lateks_col_start = jumlah_hasil_sadapan_lateks
            sheet3.write(lateks_row3_start, lateks_col_start, 'LATEKS (L)', wbf['header'])

            lump_row3_start = row3 + 2
            lump_col_start = jumlah_hasil_sadapan_lump
            sheet3.write(lump_row3_start, lump_col_start, 'LUMP (Kg)', wbf['header'])

            drc_lateks = row3 + 2
            drc_lateks_start = average_drc_lateks
            sheet3.write(drc_lateks, drc_lateks_start, 'LATEKS (L)', wbf['header'])

            drc_lump = row3 + 2
            drc_lump_start = average_drc_lump
            sheet3.write(drc_lump, drc_lump_start, 'LUMP (Kg)', wbf['header'])

            clateks_row3_start = row3 + 2
            clateks_col_start = jumlah_hasil_konversi_lateks
            sheet3.write(clateks_row3_start, clateks_col_start, 'LATEKS (Kg)', wbf['header'])

            clump_row3_start = row3 + 2
            clump_col_start = jumlah_hasil_konversi_lump
            sheet3.write(clump_row3_start, clump_col_start, 'LUMP (Kg)', wbf['header'])

            tkonversi_row3_start = row3 + 2
            tkonversi_col_start = jumlah_total_konversi
            sheet3.write(tkonversi_row3_start, tkonversi_col_start, 'KARET (Kg)', wbf['header'])

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
                        trans_data.location_id,
                        loc.name AS location_name
                    FROM 
                        employee_data
                    LEFT JOIN
                        trans_data ON employee_data.emp_id = trans_data.employee_id
                    LEFT JOIN
                        lhm_location loc ON trans_data.location_id = loc.id
                    WHERE 
                        trans_data.location_id IS NOT NULL
                    GROUP BY  
                        trans_data.location_id,
                        loc.name
                    ORDER BY
                        loc.name;
            """

            self.env.cr.execute(query, (kemandoran.id, from_date, to_date))
            karyawan_data = self.env.cr.fetchall()

            row3 += 4
            nomor = 1

            mandor_name = kemandoran.kepala_mandor_id.sudo().name if kemandoran.kepala_mandor_id else ''
            asisten_mandor_name = kemandoran.mandor_id.sudo().name if kemandoran.mandor_id else ''
            kerani_name = kemandoran.assisten_id.sudo().name if kemandoran.assisten_id else ''

            for location_data in karyawan_data:
                location_id = location_data[0]
                location_name = location_data[1]
                sheet3.write(row3, 0, nomor, wbf['data_center'])
                sheet3.write(row3, 1, location_name, wbf['data_center'])
                sheet3.write(row3, 2, '-', wbf['data_center'])

                # Isi Jumlah Hasil Sadapan Lateks (L)
                total_hasil_baris_lateks = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = second_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ], ['hasil_1_nap'])

                    hasil_nap_lateks = sum(float(line['hasil_1_nap']) for line in nap_lines if line.get('hasil_1_nap')) if nap_lines else 0

                    total_hasil_baris_lateks += hasil_nap_lateks
                    sheet3.write(row3, col_index, hasil_nap_lateks, wbf['total_float'])

                total_column_index = jumlah_hasil_sadapan_lateks
                sheet3.write(row3, total_column_index, total_hasil_baris_lateks, wbf['total_float'])
                
                # Isi Jumlah Hasil Sadapan Lump (Kg)
                total_hasil_baris_lump = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = third_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ], ['hasil_2_nap'])

                    hasil_nap_lump = sum(float(line['hasil_2_nap']) for line in nap_lines if line.get('hasil_2_nap')) if nap_lines else 0

                    total_hasil_baris_lump += hasil_nap_lump
                    sheet3.write(row3, col_index, hasil_nap_lump, wbf['total_float'])

                total_column_index = jumlah_hasil_sadapan_lump
                sheet3.write(row3, total_column_index, total_hasil_baris_lump, wbf['total_float'])

                # Isi Average DRC
                # Isi Data DRC Lateks (L) dan Hitung Rata-rata
                total_a_drc_lateks = 0
                count_a_drc_lateks = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = fourth_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done')
                    ], ['drc_latex_nap'], limit=1)

                    drc_latex_nap = float(nap_lines[0]['drc_latex_nap']) if nap_lines and nap_lines[0]['drc_latex_nap'] else 0.0
                    total_a_drc_lateks += drc_latex_nap
                    count_a_drc_lateks += 1 if drc_latex_nap else 0
                    sheet3.write(row3, col_index, drc_latex_nap, wbf['total_float'])

                # Hitung rata-rata DRC Lateks
                shi_average_drc_lateks = total_a_drc_lateks / count_a_drc_lateks if count_a_drc_lateks > 0 else 0.0
                sheet3.write(row3, average_drc_lateks, shi_average_drc_lateks, wbf['total_float'])


                # Isi Data DRC Lump (Kg) dan Hitung Rata-rata
                total_a_drc_lump = 0
                count_a_drc_lump = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = fifth_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done')
                    ], ['drc_lump_nap'], limit=1)

                    drc_lump_nap = float(nap_lines[0]['drc_lump_nap']) if nap_lines and nap_lines[0]['drc_lump_nap'] else 0.0
                    total_a_drc_lump += drc_lump_nap
                    count_a_drc_lump += 1 if drc_lump_nap else 0
                    sheet3.write(row3, col_index, drc_lump_nap, wbf['total_float'])

                # Hitung rata-rata DRC Lump
                shi_average_drc_lump = total_a_drc_lump / count_a_drc_lump if count_a_drc_lump > 0 else 0.0
                sheet3.write(row3, average_drc_lump, shi_average_drc_lump, wbf['total_float'])


                # Isi Jumlah Hasil Konversi Lateks (L)
                total_hasil_konversi_lateks = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = sixth_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ], ['hasil_convert_latex'])

                    konversi_nap_lateks = sum(float(line['hasil_convert_latex']) for line in nap_lines if line['hasil_convert_latex']) if nap_lines else 0

                    total_hasil_konversi_lateks += konversi_nap_lateks
                    sheet3.write(row3, col_index, konversi_nap_lateks, wbf['total_float'])

                total_column_index = jumlah_hasil_konversi_lateks
                sheet3.write(row3, total_column_index, total_hasil_konversi_lateks, wbf['total_float'])


                # Isi Jumlah Hasil Konversi Lump (Kg)
                total_hasil_konversi_lump = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = seventh_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ], ['hasil_convert_lump'])

                    konversi_nap_lump = sum(float(line['hasil_convert_lump']) for line in nap_lines if line['hasil_convert_lump']) if nap_lines else 0

                    total_hasil_konversi_lump += konversi_nap_lump
                    sheet3.write(row3, col_index, konversi_nap_lump, wbf['total_float'])

                total_column_index = jumlah_hasil_konversi_lump
                sheet3.write(row3, total_column_index, total_hasil_konversi_lump, wbf['total_float'])


                # Jumlahkan hasil konversi Lateks + Lump
                total_konversi_lateks_lump = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = eighth_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search_read([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ], ['hasil_convert_latex', 'hasil_convert_lump'])

                    konversi_nap_lateks = sum(float(line['hasil_convert_latex']) for line in nap_lines if line['hasil_convert_latex']) if nap_lines else 0
                    konversi_nap_lump = sum(float(line['hasil_convert_lump']) for line in nap_lines if line['hasil_convert_lump']) if nap_lines else 0

                    total_hasil_konversi = konversi_nap_lateks + konversi_nap_lump
                    total_konversi_lateks_lump += total_hasil_konversi

                    sheet3.write(row3, col_index, total_hasil_konversi, wbf['total_float'])

                # Menulis total keseluruhan konversi Lateks + Lump ke dalam kolom yang sesuai
                total_column_index = jumlah_total_konversi
                sheet3.write(row3, total_column_index, total_konversi_lateks_lump, wbf['total_float'])

                row3 += 1
                nomor += 1

            # Logika untuk Mandor
            row3 += 1
            sheet3.write(row3, 0, "M-1", wbf['data_center'])
            sheet3.write(row3, 1, "-", wbf['data_center'])
            sheet3.write(row3, 2, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i
                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_sadapan_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_sadapan_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])
            
            # Isi Average Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = average_drc_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Average Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = average_drc_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_konversi_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_konversi_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Jumlahkan hasil konversi Lateks + Lump
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = eighth_date_start + i

                sheet3.write(row3, col_index, '-', wbf['data_center'])

            total_column_index = jumlah_total_konversi
            sheet3.write(row3, total_column_index, '-', wbf['data_center'])

            # Logika untuk Asisten Mandor
            row3 += 1
            sheet3.write(row3, 0, "M-2", wbf['data_center'])
            sheet3.write(row3, 1, "-", wbf['data_center'])
            sheet3.write(row3, 2, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_sadapan_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_sadapan_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])
            
            # Isi Average Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = average_drc_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Average Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = average_drc_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_konversi_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_konversi_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Jumlahkan hasil konversi Lateks + Lump
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = eighth_date_start + i

                sheet3.write(row3, col_index, '-', wbf['data_center'])

            total_column_index = jumlah_total_konversi
            sheet3.write(row3, total_column_index, '-', wbf['data_center'])

            # Logika untuk Kerani
            row3 += 1
            sheet3.write(row3, 0, "M-3", wbf['data_center'])
            sheet3.write(row3, 1, "-", wbf['data_center'])
            sheet3.write(row3, 2, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_sadapan_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_sadapan_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])
            
            # Isi Average Hasil Sadapan Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = average_drc_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Average Hasil Sadapan Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = average_drc_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lateks (L)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_konversi_lateks
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                sheet3.write(row3, col_index, "-", wbf['data_center'])

            total_column_index = jumlah_hasil_konversi_lump
            sheet3.write(row3, total_column_index, "-", wbf['data_center'])

            # Jumlahkan hasil konversi Lateks + Lump
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = eighth_date_start + i

                sheet3.write(row3, col_index, '-', wbf['data_center'])

            total_column_index = jumlah_total_konversi
            sheet3.write(row3, total_column_index, '-', wbf['data_center'])

            row3 += 1
            # nomor += 1

            # 1
            row3 += 1

            sheet3.merge_range(row3, 0, row3, 2, "JUMLAH TOTAL", wbf['jumlah_total'])

            #2
            total_keseluruhan_hasil_lateks = 0
            total_per_tanggal_lateks = {current_date: 0 for current_date in [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]}

            for location_data in karyawan_data:
                location_id = location_data[0]

                for i, current_date in enumerate(total_per_tanggal_lateks.keys()):
                    col_index = second_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ])

                    hasil_nap_lateks = sum(float(line.hasil_1_nap) for line in nap_lines if line.hasil_1_nap)

                    total_keseluruhan_hasil_lateks += hasil_nap_lateks
                    total_per_tanggal_lateks[current_date] += hasil_nap_lateks

            row_summary = row3
            for i, current_date in enumerate(total_per_tanggal_lateks.keys()):
                col_index = second_date_start + i
                total_hasil_per_tanggal = total_per_tanggal_lateks[current_date]
                sheet3.write(row_summary, col_index, total_hasil_per_tanggal, wbf['kuning'])

            total_column_index = jumlah_hasil_sadapan_lateks
            sheet3.write(row3, total_column_index, total_keseluruhan_hasil_lateks if total_keseluruhan_hasil_lateks > 0 else '-', wbf['hijau_tua'])


            #4
            total_keseluruhan_hasil_lump = 0
            total_per_tanggal_lump = {current_date: 0 for current_date in [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]}

            for location_data in karyawan_data:
                location_id = location_data[0]

                for i, current_date in enumerate(total_per_tanggal_lump.keys()):
                    col_index = third_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ])

                    hasil_nap_lump = sum(float(line.hasil_2_nap) for line in nap_lines if line.hasil_2_nap)

                    total_keseluruhan_hasil_lump += hasil_nap_lump
                    total_per_tanggal_lump[current_date] += hasil_nap_lump

            row_summary = row3
            for i, current_date in enumerate(total_per_tanggal_lump.keys()):
                col_index = third_date_start + i
                total_hasil_per_tanggal = total_per_tanggal_lump[current_date]

                sheet3.write(row_summary, col_index, total_hasil_per_tanggal if total_hasil_per_tanggal > 0 else '-', wbf['kuning'])

            total_column_index = jumlah_hasil_sadapan_lump
            sheet3.write(row3, total_column_index, total_keseluruhan_hasil_lump if total_keseluruhan_hasil_lump > 0 else '-', wbf['hijau_tua'])


            #7
            total_keseluruhan_konversi_lateks = 0
            total_per_tanggal_konversi_lateks = {current_date: 0 for current_date in [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]}

            for location_data in karyawan_data:
                location_id = location_data[0]

                for i, current_date in enumerate(total_per_tanggal_konversi_lateks.keys()):
                    col_index = sixth_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ])

                    hasil_konversi_lateks = sum(float(line.hasil_convert_latex) for line in nap_lines if line.hasil_convert_latex)

                    total_keseluruhan_konversi_lateks += hasil_konversi_lateks
                    total_per_tanggal_konversi_lateks[current_date] += hasil_konversi_lateks

            row_summary = row3
            for i, current_date in enumerate(total_per_tanggal_konversi_lateks.keys()):
                col_index = sixth_date_start + i
                total_hasil_per_tanggal = total_per_tanggal_konversi_lateks[current_date]

                sheet3.write(row_summary, col_index, total_hasil_per_tanggal if total_hasil_per_tanggal > 0 else '-', wbf['kuning'])

            total_column_index = jumlah_hasil_konversi_lateks
            sheet3.write(row3, total_column_index, total_keseluruhan_konversi_lateks if total_keseluruhan_konversi_lateks > 0 else '-', wbf['hijau_tua'])


            #8
            total_keseluruhan_konversi_lump = 0
            total_per_tanggal_konversi_lump = {current_date: 0 for current_date in [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]}

            for location_data in karyawan_data:
                location_id = location_data[0]

                for i, current_date in enumerate(total_per_tanggal_konversi_lump.keys()):
                    col_index = seventh_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ])

                    hasil_konversi_lump = sum(float(line.hasil_convert_lump) for line in nap_lines if line.hasil_convert_lump)

                    total_keseluruhan_konversi_lump += hasil_konversi_lump
                    total_per_tanggal_konversi_lump[current_date] += hasil_konversi_lump

            row_summary = row3
            for i, current_date in enumerate(total_per_tanggal_konversi_lump.keys()):
                col_index = seventh_date_start + i
                total_hasil_per_tanggal = total_per_tanggal_konversi_lump[current_date]

                sheet3.write(row_summary, col_index, total_hasil_per_tanggal if total_hasil_per_tanggal > 0 else '-', wbf['kuning'])

            total_column_index = jumlah_hasil_konversi_lump
            sheet3.write(row3, total_column_index, total_keseluruhan_konversi_lump if total_keseluruhan_konversi_lump > 0 else '-', wbf['hijau_tua'])

            #9
            total_keseluruhan_konversi_total = 0
            total_per_tanggal_konversi_total = {current_date: 0 for current_date in [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]}

            for location_data in karyawan_data:
                location_id = location_data[0]

                for i, current_date in enumerate(total_per_tanggal_konversi_total.keys()):
                    col_index = eighth_date_start + i

                    nap_lines = self.env['lhm.transaction.nap.line'].search([
                        ('lhm_transaction_line_id.location_id', '=', location_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                    ])

                    hasil_konversi_lateks = sum(float(line.hasil_convert_latex) for line in nap_lines if line.hasil_convert_latex)
                    hasil_konversi_lump = sum(float(line.hasil_convert_lump) for line in nap_lines if line.hasil_convert_lump)

                    hasil_konversi_total = hasil_konversi_lateks + hasil_konversi_lump
                    total_keseluruhan_konversi_total += hasil_konversi_total
                    total_per_tanggal_konversi_total[current_date] += hasil_konversi_total

            row_summary = row3
            for i, current_date in enumerate(total_per_tanggal_konversi_total.keys()):
                col_index = eighth_date_start + i
                total_hasil_per_tanggal = total_per_tanggal_konversi_total[current_date]

                sheet3.write(row_summary, col_index, total_hasil_per_tanggal if total_hasil_per_tanggal > 0 else '-', wbf['kuning'])

            total_column_index = jumlah_total_konversi
            sheet3.write(row3, total_column_index, total_keseluruhan_konversi_total if total_keseluruhan_konversi_total > 0 else '-', wbf['hijau_tua'])

            row3 += 4