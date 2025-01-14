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
            'num_format': '#,##0.00'
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

        # Format total float (untuk jumlah total yang bold dengan background kuning)
        self.wbf['total_float'] = workbook.add_format({
            'bold': True,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'num_format': '#,##0.00',
            'font_color': '#000000'
        })
        self.wbf['total_float'].set_border()

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
        
        sheet = workbook.add_worksheet("Laporan Produksi")
        row = 0

        for kemandoran in kemandoran_ids:
            # sheet_name = kemandoran.name if kemandoran.name else "Sheet"
            # sheet = workbook.add_worksheet(sheet_name[:31])

            # Judul Laporan
            sheet.write(row, 0, 'Laporan Produksi')
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

                start_col = 5
                end_col = start_col + len(date_columns) - 1
                
                sheet.merge_range(row, start_col, row + 1, end_col, 'TANGGAL', wbf['header'])
                for i, date in enumerate(date_columns):
                    sheet.write(row + 2, start_col + i, date, wbf['header'])
                    sheet.set_column(start_col + i, start_col + i, 5)

            hko_start = end_col + 1
            sheet.merge_range(row, hko_start, row + 1, hko_start + 5, 'JUMLAH HKO', wbf['header'])
            # for i in range(6):
            #     sheet.write(row + 2, hko_start + i, f'Sub-{i + 1}', wbf['header'])
            #     sheet.set_column(hko_start + i, hko_start + i, 10)

            total_hk_start = hko_start + 6
            sheet.merge_range(row, total_hk_start, row + 2, total_hk_start, 'TOTAL HK', wbf['header'])
            # sheet.set_column(total_hk_start, total_hk_start, 10)

            if from_date and to_date:
                second_date_start = total_hk_start + 2
                second_date_end = second_date_start + len(date_columns) - 1

                sheet.merge_range(row, second_date_start, row + 1, second_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = second_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            jumlah_hasil_sadapan_lateks = second_date_end + 1
            sheet.merge_range(row, jumlah_hasil_sadapan_lateks, row + 1, jumlah_hasil_sadapan_lateks, 'JUMLAH HASIL SADAPAN', wbf['header'])

            if from_date and to_date:
                third_date_start = jumlah_hasil_sadapan_lateks + 2
                third_date_end = third_date_start + len(date_columns) - 1

                sheet.merge_range(row, third_date_start, row + 1, third_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = third_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            jumlah_hasil_sadapan_lump = third_date_end + 1
            sheet.merge_range(row, jumlah_hasil_sadapan_lump, row + 1, jumlah_hasil_sadapan_lump , 'JUMLAH HASIL SADAPAN', wbf['header'])

            if from_date and to_date:
                fourth_date_start = jumlah_hasil_sadapan_lump + 2
                fourth_date_end = fourth_date_start + len(date_columns) - 1
                sheet.merge_range(row, fourth_date_start, row, fourth_date_end, 'DRC LATEKS', wbf['header'])
                sheet.merge_range(row + 1, fourth_date_start, row + 1, fourth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fourth_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            if from_date and to_date:
                fifth_date_start = fourth_date_end + 2
                fifth_date_end = fifth_date_start + len(date_columns) - 1
                sheet.merge_range(row, fifth_date_start, row, fifth_date_end, 'DRC LUMP', wbf['header'])
                sheet.merge_range(row + 1, fifth_date_start, row + 1, fifth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = fifth_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)
            
            if from_date and to_date:
                sixth_date_start = fifth_date_end + 2
                sixth_date_end = sixth_date_start + len(date_columns) - 1

                sheet.merge_range(row, sixth_date_start, row + 1, sixth_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = sixth_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            jumlah_hasil_konversi_lateks = sixth_date_end + 1
            sheet.merge_range(row, jumlah_hasil_konversi_lateks, row + 1, jumlah_hasil_konversi_lateks, 'JUMLAH HASIL KONVERSI', wbf['header'])

            if from_date and to_date:
                seventh_date_start = jumlah_hasil_konversi_lateks + 2
                seventh_date_end = seventh_date_start + len(date_columns) - 1

                sheet.merge_range(row, seventh_date_start, row + 1, seventh_date_end, 'TANGGAL', wbf['header'])

                for i, date in enumerate(date_columns):
                    col_index = seventh_date_start + i
                    sheet.write(row + 2, col_index, date, wbf['header'])
                    sheet.set_column(col_index, col_index, 5)

            jumlah_hasil_konversi_lump = seventh_date_end + 1
            sheet.merge_range(row, jumlah_hasil_konversi_lump, row + 1, jumlah_hasil_konversi_lump, 'JUMLAH HASIL KONVERSI', wbf['header'])

            # Header 2
            sheet.write(row + 2, 0, 'NO.', wbf['header'])
            sheet.set_column(5, 0, 7)
            sheet.merge_range(row + 2, 1, row + 2, 2, 'NAMA', wbf['header'])
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
            sheet.write(clateks_row_start, clateks_col_start, 'LATEKS (L)', wbf['header'])

            clump_row_start = row + 2
            clump_col_start = jumlah_hasil_konversi_lump
            sheet.write(clump_row_start, clump_col_start, 'LUMP (Kg)', wbf['header'])

            # Bagian Isi Data
            query = """
                WITH employee_data AS (
                    SELECT 
                        emp.id AS emp_id,
                        emp.name AS employee_name,
                        emp.kemandoran_id AS kemandoran_emp
                    FROM 
                        hr_employee emp
                    WHERE 
                        emp.kemandoran_id = %s
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
                    employee_data.emp_id,
                    employee_data.employee_name,
                    employee_data.kemandoran_emp,
                    trans_data.location_id
                FROM 
                    employee_data
                LEFT JOIN 
                    trans_data ON employee_data.emp_id = trans_data.employee_id
                GROUP BY 
                    employee_data.emp_id,
                    employee_data.kemandoran_emp, 
                    employee_data.employee_name,
                    trans_data.location_id;
            """

            self.env.cr.execute(query, (kemandoran.id, from_date, to_date))
            karyawan_data = self.env.cr.fetchall()

            row += 4
            nomor = 1

            # mandor_name = kemandoran.foreman_id.name if kemandoran.foreman_id else ''
            # asisten_mandor_name = kemandoran.foreman_id_1.name if kemandoran.foreman_id_1 else ''
            # kerani_name = kemandoran.admin_id.name if kemandoran.admin_id else ''
            mandor_name = kemandoran.kepala_mandor_id.name if kemandoran.kepala_mandor_id else ''
            asisten_mandor_name = kemandoran.mandor_id.name if kemandoran.mandor_id else ''
            kerani_name = kemandoran.assisten_id.name if kemandoran.assisten_id else ''

            for emp_id, employee_name, kemandoran_emp, location_id in karyawan_data:
                sheet.write(row, 0, nomor, wbf['data_center'])
                sheet.merge_range(row, 1, row, 2, employee_name, wbf['data'])
                kemandoran_name = self.env['hr.foreman'].browse(kemandoran_emp).name if kemandoran_emp else '-'
                sheet.write(row, 3, kemandoran_name, wbf['data'])
                location_name = self.env['lhm.location'].browse(location_id).name if location_id else '-'
                sheet.write(row, 4, location_name, wbf['data'])

                current_col = 5
                hko_count = 0
                l_count = 0
                s_count = 0
                p_count = 0
                ct_count = 0
                m_count = 0

                for i in range(delta.days + 1):
                    attendance = self.env['lhm.transaction.line'].search([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                        ('location_id', '=', location_id)
                    ], limit=1)

                    type_code = attendance.attendance_id.code if attendance else '-'
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

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    hasil_nap_lateks = nap_line.hasil_1_nap if nap_line else '-'

                    if hasil_nap_lateks and hasil_nap_lateks != '-':
                        try:
                            total_hasil_baris_lateks += float(hasil_nap_lateks)
                            cell_format = wbf['data_center']
                        except ValueError:
                            total_hasil_baris_lateks += 0
                            cell_format = wbf['data_center']
                    else:
                        cell_format = wbf['data_center']

                    sheet.write(row, col_index, hasil_nap_lateks, cell_format)
                if total_hasil_baris_lateks == 0:
                    total_hasil_baris_lateks = '-'

                total_column_index = second_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_hasil_baris_lateks, wbf['data_center'])

                # Isi Jumlah Hasil Sadapan Lump (Kg)
                total_hasil_baris_lump = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = third_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    hasil_nap_lump = nap_line.hasil_2_nap if nap_line else '-'

                    if hasil_nap_lump and hasil_nap_lump != '-':
                        try:
                            total_hasil_baris_lump += float(hasil_nap_lump)
                            cell_format = wbf['data_center']
                        except ValueError:
                            total_hasil_baris_lump += 0
                            cell_format = wbf['data_center']
                    else:
                        cell_format = wbf['data_center']
                    if hasil_nap_lump == 0:
                        hasil_nap_lump = '-'
                    sheet.write(row, col_index, hasil_nap_lump, cell_format)
                if total_hasil_baris_lump == 0:
                    total_hasil_baris_lump = '-'

                total_column_index = third_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_hasil_baris_lump, wbf['data_center'])

                # Isi Data DRC Lateks (L)
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = fourth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    drc_lateks = nap_line.drc_latex_nap if nap_line else '-'

                    if drc_lateks and drc_lateks != '-':
                        cell_format = wbf['data_center']
                    else:
                        cell_format = wbf['data_center']

                    sheet.write(row, col_index, drc_lateks, cell_format)

                # Isi Data DRC Lump (Kg)
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = fifth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    drc_lump = nap_line.drc_lump_nap if nap_line else '-'
                    if drc_lump == 0:
                        drc_lump = '-'
                    if drc_lump and drc_lump != '-':
                        cell_format = wbf['data_center']
                    else:
                        cell_format = wbf['data_center']

                    sheet.write(row, col_index, drc_lump, cell_format)

                # Isi Jumlah Hasil Konversi Lateks (L)
                total_hasil_konversi_lateks = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = sixth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    konversi_nap_lateks = nap_line.hasil_convert_latex if nap_line else '-'

                    if konversi_nap_lateks and konversi_nap_lateks != '-':
                        try:
                            total_hasil_konversi_lateks += float(konversi_nap_lateks)
                            cell_format = wbf['data_center']
                        except ValueError:
                            total_hasil_konversi_lateks += 0
                            cell_format = wbf['data_center']
                    else:
                        cell_format = wbf['data_center']

                    sheet.write(row, col_index, konversi_nap_lateks, cell_format)
                if total_hasil_konversi_lateks == 0:
                    total_hasil_konversi_lateks = '-'

                total_column_index = sixth_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_hasil_konversi_lateks, wbf['data_center'])

                # Isi Jumlah Hasil Konversi Lump (Kg)
                total_hasil_konversi_lump = 0

                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = seventh_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    konversi_nap_lump = nap_line.hasil_convert_lump if nap_line else '-'

                    if konversi_nap_lump and konversi_nap_lump != '-':
                        try:
                            total_hasil_konversi_lump += float(konversi_nap_lump)
                            cell_format = wbf['data_center']
                        except ValueError:
                            total_hasil_konversi_lump += 0
                            cell_format = wbf['data_center']
                    else:
                        cell_format = wbf['data_center']
                    if konversi_nap_lump == 0:
                        konversi_nap_lump = '-'
                    sheet.write(row, col_index, konversi_nap_lump, cell_format)
                if total_hasil_konversi_lump == 0:
                    total_hasil_konversi_lump = '-'

                total_column_index = seventh_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_hasil_konversi_lump, wbf['data_center'])

                row += 1
                nomor += 1

            # Logika untuk Mandor
            row += 1
            sheet.write(row, 0, "M-1", wbf['data_center'])
            sheet.merge_range(row, 1, row, 2, mandor_name, wbf['data'])
            sheet.write(row, 3, kemandoran_name, wbf['data'])
            sheet.write(row, 4, location_name, wbf['data'])

            mandor_hko_count = 0
            mandor_l_count = 0
            mandor_s_count = 0
            mandor_p_count = 0
            mandor_ct_count = 0
            mandor_m_count = 0

            mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)

                type_code = attendance.attendance_id.code if attendance else '-'
                sheet.write(row, 5 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet.write(row, 5 + i, type_code, wbf['hijau_muda'])
                    mandor_hko_count += 1
                elif type_code == 'NA':
                    sheet.write(row, 5 + i, type_code, wbf['hijau_tua'])
                    mandor_l_count += 1
                elif type_code == 'S1':
                    sheet.write(row, 5 + i, type_code, wbf['kuning'])
                    mandor_s_count += 1
                elif type_code == 'P1':
                    sheet.write(row, 5 + i, type_code, wbf['biru_tua'])
                    mandor_p_count += 1
                elif type_code == 'CT':
                    sheet.write(row, 5 + i, type_code, wbf['biru_muda'])
                    mandor_ct_count += 1
                elif type_code == 'M':
                    sheet.write(row, 5 + i, type_code, wbf['merah'])
                    mandor_m_count += 1

            sheet.write(row, hko_start, mandor_hko_count, wbf['biru_muda'])
            sheet.write(row, hko_start + 1, mandor_l_count, wbf['data_center'])
            sheet.write(row, hko_start + 2, mandor_s_count, wbf['data_center'])
            sheet.write(row, hko_start + 3, mandor_p_count, wbf['data_center'])
            sheet.write(row, hko_start + 4, mandor_ct_count, wbf['data_center'])
            sheet.write(row, hko_start + 5, mandor_m_count, wbf['data_center'])
            sheet.write(row, total_hk_start, '-', wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)
            total_hasil_baris_lateks = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                hasil_nap_lateks = nap_line.hasil_1_nap if nap_line else '-'

                if hasil_nap_lateks and hasil_nap_lateks != '-':
                    try:
                        total_hasil_baris_lateks += float(hasil_nap_lateks)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_baris_lateks += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, hasil_nap_lateks, cell_format)
            if total_hasil_baris_lateks == 0:
                total_hasil_baris_lateks = '-'

            total_column_index = second_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_baris_lateks, wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)
            total_hasil_baris_lump = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                hasil_nap_lump = nap_line.hasil_2_nap if nap_line else '-'

                if hasil_nap_lump and hasil_nap_lump != '-':
                    try:
                        total_hasil_baris_lump += float(hasil_nap_lump)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_baris_lump += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']
                if hasil_nap_lump == 0:
                    hasil_nap_lump = '-'
                sheet.write(row, col_index, hasil_nap_lump, cell_format)
            if total_hasil_baris_lump == 0:
                total_hasil_baris_lump = '-'

            total_column_index = third_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_baris_lump, wbf['data_center'])

            # Isi Data DRC Lateks (L)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                drc_lateks = nap_line.drc_latex_nap if nap_line else '-'

                if drc_lateks and drc_lateks != '-':
                    cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, drc_lateks, cell_format)

            # Isi Data DRC Lump (Kg)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                drc_lump = nap_line.drc_lump_nap if nap_line else '-'
                if drc_lump == 0:
                    drc_lump = '-'
                if drc_lump and drc_lump != '-':
                    cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, drc_lump, cell_format)

            # Isi Jumlah Hasil Konversi Lateks (L)
            total_hasil_konversi_lateks = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                konversi_nap_lateks = nap_line.hasil_convert_latex if nap_line else '-'

                if konversi_nap_lateks and konversi_nap_lateks != '-':
                    try:
                        total_hasil_konversi_lateks += float(konversi_nap_lateks)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_konversi_lateks += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, konversi_nap_lateks, cell_format)
            if total_hasil_konversi_lateks == 0:
                total_hasil_konversi_lateks = '-'

            total_column_index = sixth_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_konversi_lateks, wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)
            total_hasil_konversi_lump = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                konversi_nap_lump = nap_line.hasil_convert_lump if nap_line else '-'

                if konversi_nap_lump and konversi_nap_lump != '-':
                    try:
                        total_hasil_konversi_lump += float(konversi_nap_lump)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_konversi_lump += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']
                if konversi_nap_lump == 0:
                    konversi_nap_lump = '-'
                sheet.write(row, col_index, konversi_nap_lump, cell_format)
            if total_hasil_konversi_lump == 0:
                total_hasil_konversi_lump = '-'

            total_column_index = seventh_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_konversi_lump, wbf['data_center'])

            # Logika untuk Asisten Mandor
            row += 1
            sheet.write(row, 0, "M-2", wbf['data_center'])
            sheet.merge_range(row, 1, row, 2, asisten_mandor_name, wbf['data'])
            sheet.write(row, 3, kemandoran_name, wbf['data'])
            sheet.write(row, 4, location_name, wbf['data'])

            asisten_hko_count = 0
            asisten_l_count = 0
            asisten_s_count = 0
            asisten_p_count = 0
            asisten_ct_count = 0
            asisten_m_count = 0

            asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)

                type_code = attendance.attendance_id.code if attendance else '-'
                sheet.write(row, 5 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet.write(row, 5 + i, type_code, wbf['hijau_muda'])
                    asisten_hko_count += 1
                elif type_code == 'NA':
                    sheet.write(row, 5 + i, type_code, wbf['hijau_tua'])
                    asisten_l_count += 1
                elif type_code == 'S1':
                    sheet.write(row, 5 + i, type_code, wbf['kuning'])
                    asisten_s_count += 1
                elif type_code == 'P1':
                    sheet.write(row, 5 + i, type_code, wbf['biru_tua'])
                    asisten_p_count += 1
                elif type_code == 'CT':
                    sheet.write(row, 5 + i, type_code, wbf['biru_muda'])
                    asisten_ct_count += 1
                elif type_code == 'M':
                    sheet.write(row, 5 + i, type_code, wbf['merah'])
                    asisten_m_count += 1

            sheet.write(row, hko_start, asisten_hko_count, wbf['biru_muda'])
            sheet.write(row, hko_start + 1, asisten_l_count, wbf['data_center'])
            sheet.write(row, hko_start + 2, asisten_s_count, wbf['data_center'])
            sheet.write(row, hko_start + 3, asisten_p_count, wbf['data_center'])
            sheet.write(row, hko_start + 4, asisten_ct_count, wbf['data_center'])
            sheet.write(row, hko_start + 5, asisten_m_count, wbf['data_center'])
            sheet.write(row, total_hk_start, '-', wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)
            total_hasil_baris_lateks = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                hasil_nap_lateks = nap_line.hasil_1_nap if nap_line else '-'

                if hasil_nap_lateks and hasil_nap_lateks != '-':
                    try:
                        total_hasil_baris_lateks += float(hasil_nap_lateks)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_baris_lateks += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, hasil_nap_lateks, cell_format)
            if total_hasil_baris_lateks == 0:
                total_hasil_baris_lateks = '-'

            total_column_index = second_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_baris_lateks, wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)
            total_hasil_baris_lump = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                hasil_nap_lump = nap_line.hasil_2_nap if nap_line else '-'

                if hasil_nap_lump and hasil_nap_lump != '-':
                    try:
                        total_hasil_baris_lump += float(hasil_nap_lump)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_baris_lump += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']
                if hasil_nap_lump == 0:
                    hasil_nap_lump = '-'
                sheet.write(row, col_index, hasil_nap_lump, cell_format)
            if total_hasil_baris_lump == 0:
                total_hasil_baris_lump = '-'

            total_column_index = third_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_baris_lump, wbf['data_center'])

            # Isi Data DRC Lateks (L)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                drc_lateks = nap_line.drc_latex_nap if nap_line else '-'

                if drc_lateks and drc_lateks != '-':
                    cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, drc_lateks, cell_format)

            # Isi Data DRC Lump (Kg)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                drc_lump = nap_line.drc_lump_nap if nap_line else '-'
                if drc_lump == 0:
                    drc_lump = '-'
                if drc_lump and drc_lump != '-':
                    cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, drc_lump, cell_format)

            # Isi Jumlah Hasil Konversi Lateks (L)
            total_hasil_konversi_lateks = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                konversi_nap_lateks = nap_line.hasil_convert_latex if nap_line else '-'

                if konversi_nap_lateks and konversi_nap_lateks != '-':
                    try:
                        total_hasil_konversi_lateks += float(konversi_nap_lateks)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_konversi_lateks += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, konversi_nap_lateks, cell_format)
            if total_hasil_konversi_lateks == 0:
                total_hasil_konversi_lateks = '-'

            total_column_index = sixth_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_konversi_lateks, wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)
            total_hasil_konversi_lump = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                konversi_nap_lump = nap_line.hasil_convert_lump if nap_line else '-'

                if konversi_nap_lump and konversi_nap_lump != '-':
                    try:
                        total_hasil_konversi_lump += float(konversi_nap_lump)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_konversi_lump += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']
                if konversi_nap_lump == 0:
                    konversi_nap_lump = '-'
                sheet.write(row, col_index, konversi_nap_lump, cell_format)
            if total_hasil_konversi_lump == 0:
                total_hasil_konversi_lump = '-'

            total_column_index = seventh_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_konversi_lump, wbf['data_center'])

            # Logika untuk Kerani
            row += 1
            sheet.write(row, 0, "M-3", wbf['data_center'])
            sheet.merge_range(row, 1, row, 2, kerani_name, wbf['data'])
            sheet.write(row, 3, kemandoran_name, wbf['data'])
            sheet.write(row, 4, location_name, wbf['data'])

            kerani_hko_count = 0
            kerani_l_count = 0
            kerani_s_count = 0
            kerani_p_count = 0
            kerani_ct_count = 0
            kerani_m_count = 0

            kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)

                type_code = attendance.attendance_id.code if attendance else '-'
                sheet.write(row, 5 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet.write(row, 5 + i, type_code, wbf['hijau_muda'])
                    kerani_hko_count += 1
                elif type_code == 'NA':
                    sheet.write(row, 5 + i, type_code, wbf['hijau_tua'])
                    kerani_l_count += 1
                elif type_code == 'S1':
                    sheet.write(row, 5 + i, type_code, wbf['kuning'])
                    kerani_s_count += 1
                elif type_code == 'P1':
                    sheet.write(row, 5 + i, type_code, wbf['biru_tua'])
                    kerani_p_count += 1
                elif type_code == 'CT':
                    sheet.write(row, 5 + i, type_code, wbf['biru_muda'])
                    kerani_ct_count += 1
                elif type_code == 'M':
                    sheet.write(row, 5 + i, type_code, wbf['merah'])
                    kerani_m_count += 1

            sheet.write(row, hko_start, kerani_hko_count, wbf['biru_muda'])
            sheet.write(row, hko_start + 1, kerani_l_count, wbf['data_center'])
            sheet.write(row, hko_start + 2, kerani_s_count, wbf['data_center'])
            sheet.write(row, hko_start + 3, kerani_p_count, wbf['data_center'])
            sheet.write(row, hko_start + 4, kerani_ct_count, wbf['data_center'])
            sheet.write(row, hko_start + 5, kerani_m_count, wbf['data_center'])
            sheet.write(row, total_hk_start, '-', wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lateks (L)
            total_hasil_baris_lateks = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = second_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                hasil_nap_lateks = nap_line.hasil_1_nap if nap_line else '-'

                if hasil_nap_lateks and hasil_nap_lateks != '-':
                    try:
                        total_hasil_baris_lateks += float(hasil_nap_lateks)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_baris_lateks += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, hasil_nap_lateks, cell_format)
            if total_hasil_baris_lateks == 0:
                total_hasil_baris_lateks = '-'

            total_column_index = second_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_baris_lateks, wbf['data_center'])

            # Isi Jumlah Hasil Sadapan Lump (Kg)
            total_hasil_baris_lump = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = third_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                hasil_nap_lump = nap_line.hasil_2_nap if nap_line else '-'

                if hasil_nap_lump and hasil_nap_lump != '-':
                    try:
                        total_hasil_baris_lump += float(hasil_nap_lump)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_baris_lump += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']
                if hasil_nap_lump == 0:
                    hasil_nap_lump = '-'
                sheet.write(row, col_index, hasil_nap_lump, cell_format)
            if total_hasil_baris_lump == 0:
                total_hasil_baris_lump = '-'

            total_column_index = third_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_baris_lump, wbf['data_center'])

            # Isi Data DRC Lateks (L)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fourth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                drc_lateks = nap_line.drc_latex_nap if nap_line else '-'

                if drc_lateks and drc_lateks != '-':
                    cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, drc_lateks, cell_format)

            # Isi Data DRC Lump (Kg)
            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = fifth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                drc_lump = nap_line.drc_lump_nap if nap_line else '-'
                if drc_lump == 0:
                    drc_lump = '-'
                if drc_lump and drc_lump != '-':
                    cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, drc_lump, cell_format)

            # Isi Jumlah Hasil Konversi Lateks (L)
            total_hasil_konversi_lateks = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = sixth_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                konversi_nap_lateks = nap_line.hasil_convert_latex if nap_line else '-'

                if konversi_nap_lateks and konversi_nap_lateks != '-':
                    try:
                        total_hasil_konversi_lateks += float(konversi_nap_lateks)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_konversi_lateks += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']

                sheet.write(row, col_index, konversi_nap_lateks, cell_format)
            if total_hasil_konversi_lateks == 0:
                total_hasil_konversi_lateks = '-'

            total_column_index = sixth_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_konversi_lateks, wbf['data_center'])

            # Isi Jumlah Hasil Konversi Lump (Kg)
            total_hasil_konversi_lump = 0

            for i in range((to_date - from_date).days + 1):
                current_date = from_date + timedelta(days=i)
                col_index = seventh_date_start + i

                nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('lhm_transaction_line_id.date', '=', current_date),
                    ('lhm_transaction_line_id.state', '=', 'done'),
                    ('lhm_transaction_line_id.location_id', '=', location_id)
                ], limit=1)

                konversi_nap_lump = nap_line.hasil_convert_lump if nap_line else '-'

                if konversi_nap_lump and konversi_nap_lump != '-':
                    try:
                        total_hasil_konversi_lump += float(konversi_nap_lump)
                        cell_format = wbf['data_center']
                    except ValueError:
                        total_hasil_konversi_lump += 0
                        cell_format = wbf['data_center']
                else:
                    cell_format = wbf['data_center']
                if konversi_nap_lump == 0:
                    konversi_nap_lump = '-'
                sheet.write(row, col_index, konversi_nap_lump, cell_format)
            if total_hasil_konversi_lump == 0:
                total_hasil_konversi_lump = '-'

            total_column_index = seventh_date_start + (to_date - from_date).days + 1
            sheet.write(row, total_column_index, total_hasil_konversi_lump, wbf['data_center'])

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

            for emp_id, employee_name, kemandoran_emp, location_id in karyawan_data:
                current_col = 5
                for i in range(len(date_columns)):
                    attendance = self.env['lhm.transaction.line'].search([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                        ('location_id', '=', location_id)
                    ], limit=1)

                    type_code = attendance.attendance_id.code if attendance else '-'
                    if type_code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

            for i in range(len(date_columns)):
                mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)
                if attendance.attendance_id.code in ['KJ', 'KJI', 'KJO']:
                    total_hko_per_tanggal[i] += 1

                asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)
                if attendance.attendance_id.code in ['KJ', 'KJI', 'KJO']:
                    total_hko_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)
                if attendance.attendance_id.code in ['KJ', 'KJI', 'KJO']:
                    total_hko_per_tanggal[i] += 1


            for i in range(len(date_columns)):
                sheet.write(row, 5 + i, total_hko_per_tanggal[i], wbf['kuning'])

            #2
            for emp_id, employee_name, kemandoran_emp, location_id in karyawan_data:
                current_col = 5
                for i in range(len(date_columns)):
                    attendance = self.env['lhm.transaction.line'].search([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                        ('location_id', '=', location_id)
                    ], limit=1)

                    type_code = attendance.attendance_id.code if attendance else '-'
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

            for i in range(len(date_columns)):
                mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)
                if attendance.attendance_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'NA':
                    total_l_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'P1':
                    total_p_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'M':
                    total_m_per_tanggal[i] += 1

                asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)
                if attendance.attendance_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'NA':
                    total_l_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'P1':
                    total_p_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'M':
                    total_m_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                    ('location_id', '=', location_id)
                ], limit=1)
                if attendance.attendance_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'NA':
                    total_l_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'P1':
                    total_p_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.attendance_id.code == 'M':
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

            for emp_id, employee_name, kemandoran_emp, location_id in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = second_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    hasil_nap_lateks = nap_line.hasil_1_nap if nap_line else '-'

                    if hasil_nap_lateks and hasil_nap_lateks != '-':
                        try:
                            hasil_nap_lateks_float = float(hasil_nap_lateks)
                            total_keseluruhan_hasil_lateks += hasil_nap_lateks_float
                            total_per_tanggal_lateks[current_date] = total_per_tanggal_lateks.get(current_date, 0) + hasil_nap_lateks_float
                            cell_format = wbf['kuning']
                        except ValueError:
                            hasil_nap_lateks_float = 0
                            cell_format = wbf['kuning']
                    else:
                        hasil_nap_lateks_float = 0
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_lateks.get(current_date, 0), cell_format)

                total_column_index = second_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_keseluruhan_hasil_lateks if total_keseluruhan_hasil_lateks > 0 else '-', wbf['hijau_tua'])

            #4
            total_keseluruhan_hasil_lump = 0
            total_per_tanggal_lump = {}
            for emp_id, employee_name, kemandoran_emp, location_id in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = third_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    hasil_nap_lump = nap_line.hasil_2_nap if nap_line else '-'

                    if hasil_nap_lump and hasil_nap_lump != '-':
                        try:
                            hasil_nap_lump_float = float(hasil_nap_lump)
                            total_keseluruhan_hasil_lump += hasil_nap_lump_float
                            total_per_tanggal_lump[current_date] = total_per_tanggal_lump.get(current_date, 0) + hasil_nap_lump_float
                            cell_format = wbf['kuning']
                        except ValueError:
                            hasil_nap_lump_float = 0
                            cell_format = wbf['kuning']
                    else:
                        hasil_nap_lump_float = 0
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_lump.get(current_date, 0), cell_format)

                total_column_index = third_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_keseluruhan_hasil_lump if total_keseluruhan_hasil_lump > 0 else '-', wbf['hijau_tua'])

            #7
            total_keseluruhan_konversi_lateks = 0
            total_per_tanggal_konversi_lateks = {}
            for emp_id, employee_name, kemandoran_emp, location_id in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = sixth_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    hasil_nap_lateks = nap_line.hasil_convert_latex if nap_line else '-'

                    if hasil_nap_lateks and hasil_nap_lateks != '-':
                        try:
                            hasil_nap_lateks_float = float(hasil_nap_lateks)
                            total_keseluruhan_konversi_lateks += hasil_nap_lateks_float
                            total_per_tanggal_konversi_lateks[current_date] = total_per_tanggal_konversi_lateks.get(current_date, 0) + hasil_nap_lateks_float
                            cell_format = wbf['kuning']
                        except ValueError:
                            hasil_nap_lateks_float = 0
                            total_per_tanggal_konversi_lateks[current_date] = total_per_tanggal_konversi_lateks.get(current_date, 0) + 0
                            cell_format = wbf['kuning']
                    else:
                        hasil_nap_lateks_float = '-'
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_konversi_lateks.get(current_date, 0), cell_format)

                total_column_index = sixth_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_keseluruhan_konversi_lateks if total_keseluruhan_konversi_lateks > 0 else '-', wbf['hijau_tua'])

            #8
            total_keseluruhan_konversi_lump = 0
            total_per_tanggal_konversi_lump = {}
            for emp_id, employee_name, kemandoran_emp, location_id in karyawan_data:
                current_col = 5
                for i in range((to_date - from_date).days + 1):
                    current_date = from_date + timedelta(days=i)
                    col_index = seventh_date_start + i

                    nap_line = self.env['lhm.transaction.nap.line'].search([
                        ('employee_id', '=', emp_id),
                        ('lhm_transaction_line_id.date', '=', current_date),
                        ('lhm_transaction_line_id.state', '=', 'done'),
                        ('lhm_transaction_line_id.location_id', '=', location_id)
                    ], limit=1)

                    hasil_nap_lateks = nap_line.hasil_convert_lump if nap_line else '-'

                    if hasil_nap_lateks and hasil_nap_lateks != '-':
                        try:
                            hasil_nap_lateks_float = float(hasil_nap_lateks)
                            total_keseluruhan_konversi_lump += hasil_nap_lateks_float
                            total_per_tanggal_konversi_lump[current_date] = total_per_tanggal_konversi_lump.get(current_date, 0) + hasil_nap_lateks_float
                            cell_format = wbf['kuning']
                        except ValueError:
                            hasil_nap_lateks_float = 0
                            total_per_tanggal_konversi_lump[current_date] = total_per_tanggal_konversi_lump.get(current_date, 0) + 0
                            cell_format = wbf['kuning']
                    else:
                        hasil_nap_lateks_float = '-'
                        cell_format = wbf['kuning']

                    sheet.write(row, col_index, total_per_tanggal_konversi_lump.get(current_date, 0), cell_format)

                total_column_index = seventh_date_start + (to_date - from_date).days + 1
                sheet.write(row, total_column_index, total_keseluruhan_konversi_lump if total_keseluruhan_konversi_lump > 0 else '-', wbf['hijau_tua'])

            row += 4

