from odoo import models
from datetime import datetime, timedelta

class ReportSummaryBkm(models.AbstractModel):
    _name = 'report.nyalindung_report.summary_bkm_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Summary LHM Excel"

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
            'font_size': 10,
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
            'font_size': 10,
            'font_color': '#FFFFFF',
            'bg_color': '#088404',
            'border': 1
        })
        self.wbf['jumlah_total'].set_text_wrap()
        self.wbf['jumlah_total'].set_border()

        # Format untuk kolom data
        self.wbf['data'] = workbook.add_format({
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['data'].set_text_wrap()
        self.wbf['data'].set_border()
        
        # Format untuk kolom data center
        self.wbf['data_center'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
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
            'border': 1
        })
        self.wbf['biru_muda'].set_text_wrap()
        self.wbf['biru_muda'].set_border()

        self.wbf['hijau_muda'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#4AE656',
            'border': 1
        })
        self.wbf['hijau_muda'].set_text_wrap()
        self.wbf['hijau_muda'].set_border()

        self.wbf['hijau_tua'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#188520',
            'border': 1
        })
        self.wbf['hijau_tua'].set_text_wrap()
        self.wbf['hijau_tua'].set_border()

        self.wbf['biru_tua'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#134869',
            'border': 1
        })
        self.wbf['biru_tua'].set_text_wrap()
        self.wbf['biru_tua'].set_border()

        self.wbf['kuning'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#F7DB0F',
            'border': 1
        })
        self.wbf['kuning'].set_text_wrap()
        self.wbf['kuning'].set_border()

        self.wbf['merah'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#000000',
            'bg_color': '#DE1313',
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
        
        sheet = workbook.add_worksheet("Summary LHM")
        row = 0
        for kemandoran in kemandoran_ids:

            # Judul Laporan
            sheet.write(row, 0, 'BLOK')
            sheet.write(row, 1,':', wbf['content_center'])
            sheet.write(row, 2, kemandoran.name)
            row += 1
            sheet.write(row, 0, 'BULAN')
            sheet.write(row, 1,':', wbf['content_center'])
            sheet.write(row, 2, f'{from_date.strftime("%d-%m-%Y")} s/d {to_date.strftime("%d-%m-%Y")}' if from_date and to_date else '')
            row += 2
            # Bagian Header 1
            sheet.merge_range(row, 0, row + 1, 2, kemandoran.name or '', wbf['kemandoran'])

            if from_date and to_date:
                delta = to_date - from_date
                date_columns = []
                for i in range(delta.days + 1):
                    current_date = from_date + timedelta(days=i)
                    date_columns.append(current_date.strftime('%d'))

                start_col = 10
                end_col = start_col + len(date_columns) - 1
                
                sheet.merge_range(row, start_col, row + 1, end_col, 'TANGGAL', wbf['header'])
                for i, date in enumerate(date_columns):
                    sheet.write(row + 2, start_col + i, date, wbf['header'])
                    sheet.set_column(start_col + i, start_col + i, 5)

            hko_start = 3
            sheet.merge_range(row, hko_start, row + 1, hko_start + 5, 'JUMLAH HKO', wbf['header'])

            total_hk_start = hko_start + 6
            sheet.merge_range(row, total_hk_start, row + 2, total_hk_start, 'TOTAL HK', wbf['header'])

            # Header 2
            sheet.write(row + 2, 0, 'NO.', wbf['header'])
            sheet.write(row + 2, 1, 'NIK', wbf['header'])
            sheet.set_column(5, 1, 13)
            sheet.write(row + 2, 2, 'NAMA', wbf['header'])
            sheet.set_column(5, 2, 22)
            for total_hko in range(3, 9):
                sheet.set_column(5, total_hko, 7)

            hko_headers = ['HKO', 'L', 'S', 'P', 'CT', 'M']
            hko_formats = [self.wbf['biru_muda'], self.wbf['hijau_tua'], self.wbf['kuning'], self.wbf['biru_tua'], self.wbf['biru_muda'], self.wbf['merah']]

            for i, header in enumerate(hko_headers):
                sheet.write(row + 2, hko_start + i, header, hko_formats[i])

            # Bagian Isi Data
            query = """
                WITH employee_data AS (
                    SELECT 
                        emp.id AS emp_id,
                        emp.name AS employee_name,
                        emp.no_induk as no_induk
                    FROM 
                        hr_employee emp
                    WHERE 
                        emp.kemandoran_id = %s
                        AND emp.active = TRUE
                ),
                nap_data AS (
                    SELECT 
                        nap_line.qty_nap, 
                        nap.date_nap, 
                        nap_line.employee_id
                    FROM 
                        lhm_nap_line nap_line
                    JOIN 
                        lhm_nap nap ON nap.id = nap_line.lhm_nap_id
                    WHERE 
                        nap.date_nap BETWEEN %s AND %s
                        AND nap.state = 'done'
                        AND nap_line.product_id IN (
                            SELECT id FROM product_product 
                            WHERE product_tmpl_id IN (
                                SELECT id FROM product_template WHERE name = '{"en_US": "Lateks"}'
                            )
                        )
                ),
                trans_data AS (
                    SELECT 
                        trans_nap_line.hasil_convert_latex, 
                        trans_nap_line.hasil_convert_lump, 
                        trans.date, 
                        trans_line.employee_id
                    FROM 
                        lhm_transaction_nap_line trans_nap_line
                    JOIN 
                        lhm_transaction_line trans_line ON trans_line.id = trans_nap_line.lhm_transaction_line_id
                    JOIN 
                        lhm_transaction trans ON trans.id = trans_line.lhm_id
                    WHERE 
                        trans.date BETWEEN %s AND %s
                        AND trans.state = 'done'
                )
                SELECT 
                    employee_data.emp_id,
                    employee_data.employee_name,
                    employee_data.no_induk,
                    SUM(COALESCE(trans_data.hasil_convert_latex, 0)) AS total_hasil_convert_latex_bagi_2,
                    SUM(COALESCE(trans_data.hasil_convert_lump, 0)) AS total_hasil_convert_lump_bagi_2
                FROM 
                    employee_data
                LEFT JOIN 
                    nap_data ON employee_data.emp_id = nap_data.employee_id
                LEFT JOIN 
                    trans_data ON employee_data.emp_id = trans_data.employee_id
                GROUP BY 
                    employee_data.emp_id, 
                    employee_data.no_induk,
                    employee_data.employee_name
                ORDER BY
                    employee_data.employee_name ASC;
            """
            
            self.env.cr.execute(query, (kemandoran.id, from_date, to_date, from_date, to_date))
            karyawan_data = self.env.cr.fetchall()

            row += 4
            nomor = 1

            mandor_name = kemandoran.kepala_mandor_id.name if kemandoran.kepala_mandor_id else ''
            mandor_nik = kemandoran.kepala_mandor_id.no_induk if kemandoran.kepala_mandor_id else ''
            asisten_mandor_name = kemandoran.mandor_id.name if kemandoran.mandor_id else ''
            asisten_mandor_nik = kemandoran.mandor_id.no_induk if kemandoran.mandor_id else ''
            kerani_name = kemandoran.assisten_id.name if kemandoran.assisten_id else ''
            kerani_nik = kemandoran.assisten_id.no_induk if kemandoran.assisten_id else ''

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data:
                sheet.write(row, 0, nomor, wbf['data_center'])
                sheet.write(row, 1, no_induk, wbf['data'])
                sheet.write(row, 2, employee_name, wbf['data'])

                current_col = 10
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
                    ], limit=1)

                    type_code = attendance.attendance_id.code if attendance else '-'
                    sheet.write(row, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet.write(row, current_col, type_code, wbf['hijau_muda'])
                        hko_count += 1
                    elif type_code == 'L':
                        sheet.write(row, current_col, type_code, wbf['hijau_tua'])
                        l_count += 1
                    elif type_code == 'S1':
                        sheet.write(row, current_col, type_code, wbf['kuning'])
                        s_count += 1
                    elif type_code == 'P':
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

                row += 1
                nomor += 1

            # Logika untuk Mandor
            row += 1
            sheet.write(row, 0, 'M-1', wbf['data_center'])
            sheet.write(row, 1, mandor_nik, wbf['data'])
            sheet.write(row, 2, mandor_name, wbf['data'])

            mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', mandor_employee.id),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                ], limit=1)

                sheet.write(row, 10 + i, "-", wbf['data_center'])

            sheet.write(row, hko_start, "-", wbf['biru_muda'])
            sheet.write(row, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row, total_hk_start, '-', wbf['data_center'])

            # Logika untuk Asisten Mandor
            row += 1
            sheet.write(row, 0, 'M-2', wbf['data_center'])
            sheet.write(row, 1, asisten_mandor_nik, wbf['data'])
            sheet.write(row, 2, asisten_mandor_name, wbf['data'])

            asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', asisten_employee.id),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                ], limit=1)

                sheet.write(row, 10 + i, "-", wbf['data_center'])

            sheet.write(row, hko_start, "-", wbf['biru_muda'])
            sheet.write(row, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row, total_hk_start, "-", wbf['data_center'])

            # Logika untuk Kerani
            row += 1
            sheet.write(row, 0, 'M-3', wbf['data_center'])
            sheet.write(row, 1, kerani_nik, wbf['data'])
            sheet.write(row, 2, kerani_name, wbf['data'])

            kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', kerani_employee.id),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('state', '=', 'done'),
                ], limit=1)

                sheet.write(row, 10 + i, "-", wbf['data_center'])

            sheet.write(row, hko_start, "-", wbf['biru_muda'])
            sheet.write(row, hko_start + 1, "-", wbf['data_center'])
            sheet.write(row, hko_start + 2, "-", wbf['data_center'])
            sheet.write(row, hko_start + 3, "-", wbf['data_center'])
            sheet.write(row, hko_start + 4, "-", wbf['data_center'])
            sheet.write(row, hko_start + 5, "-", wbf['data_center'])
            sheet.write(row, total_hk_start, "-", wbf['data_center'])

            row += 1
            nomor += 1

            # 1 yang -
            row += 1
            total_hko_per_tanggal = [0] * len(date_columns)

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data:
                current_col = 10
                for i in range(len(date_columns)):
                    attendance = self.env['lhm.transaction.line'].search([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                    ], limit=1)

                    type_code = attendance.attendance_id.code if attendance else '-'
                    if type_code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

            sheet.write(row, 0, '-', wbf['data_center'])
            sheet.write(row, 1, '-', wbf['data_center'])
            sheet.write(row, 2, '-', wbf['data_center'])
            sheet.write(row, 3, '-', wbf['data_center'])
            sheet.write(row, 4, '-', wbf['data_center'])
            sheet.write(row, 5, '-', wbf['data_center'])
            sheet.write(row, 6, '-', wbf['data_center'])
            sheet.write(row, 7, '-', wbf['data_center'])
            sheet.write(row, 8, '-', wbf['data_center'])

            for i in range(len(date_columns)):
                sheet.write(row, 10 + i, total_hko_per_tanggal[i], wbf['data_center'])
            
            # start_col = 2 + len(date_columns)
            # for i in range(6):
            #     sheet.write(row, start_col + i, '-', wbf['data_center'])

            sheet.write(row, total_hk_start, '-', wbf['data_center'])

            #2
            row += 1
            total_bsh = 0
            total_krg = 0
            total_hko_per_tanggal = [0] * len(date_columns)
            total_l_per_tanggal = [0] * len(date_columns)
            total_s_per_tanggal = [0] * len(date_columns)
            total_p_per_tanggal = [0] * len(date_columns)
            total_ct_per_tanggal = [0] * len(date_columns)
            total_m_per_tanggal = [0] * len(date_columns)

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data:
                current_col = 10
                for i in range(len(date_columns)):
                    attendance = self.env['lhm.transaction.line'].search([
                        ('employee_id', '=', emp_id),
                        ('date', '=', from_date + timedelta(days=i)),
                        ('state', '=', 'done'),
                    ], limit=1)

                    type_code = attendance.attendance_id.code if attendance else '-'
                    if type_code == 'KJ':
                        total_hko_per_tanggal[i] += 1
                    elif type_code == 'L':
                        total_l_per_tanggal[i] += 1
                    elif type_code == 'S1':
                        total_s_per_tanggal[i] += 1
                    elif type_code == 'P':
                        total_p_per_tanggal[i] += 1
                    elif type_code == 'CT':
                        total_ct_per_tanggal[i] += 1
                    elif type_code == 'M':
                        total_m_per_tanggal[i] += 1

            row += 1
            sheet.merge_range(row, 0, row, 2, "JUMLAH TOTAL", wbf['jumlah_total'])

            for i in range(len(date_columns)):
                sheet.write(row, 10 + i, '', wbf['kuning'])

            sheet.write(row, hko_start, sum(total_hko_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 1, sum(total_l_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 2, sum(total_s_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 3, sum(total_p_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 4, sum(total_ct_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 5, sum(total_m_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, total_hk_start, '', wbf['hijau_tua'])

            row += 1


            # TTD 1
            row += 1

            for i in range(len(date_columns)):
                sheet.write(row, 5 + i, '', wbf['content_center'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 6 + len(date_columns)
            sheet.merge_range(row, start_col, row, start_col + 3, f'Nyalindung, {current_date}', wbf['content_center'])
            
            # TTD 2 ganteng
            row += 1
            sheet.merge_range(row, 0, row, 3, 'Mengetahui,', wbf['content_center'])
            sheet.merge_range(row, 5, row, 5 + len(date_columns), 'Menyetujui,', wbf['content_center'])


            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 6 + len(date_columns)
            sheet.merge_range(row, start_col, row, start_col + 3, 'Dibuat Oleh', wbf['content_center'])
            
            # TTD 3
            row += 6
            sheet.merge_range(row, 0, row, 1, 'Hendra', wbf['center_bold'])
            sheet.merge_range(row, 3, row, 4, 'Ilmiano Swara', wbf['center_bold'])
            sheet.merge_range(row, 5, row, 5 + len(date_columns), 'Wahyu Widiyanto', wbf['center_bold'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 6 + len(date_columns)
            sheet.merge_range(row, start_col, row, start_col + 3, 'Hani Andriani', wbf['center_bold'])
            
            # TTD 4
            row += 1
            sheet.merge_range(row, 0, row, 1, 'Mandor Besar Karet', wbf['content_center'])
            sheet.merge_range(row, 3, row, 4, 'Asisten Kebun', wbf['content_center'])
            sheet.merge_range(row, 5, row, 5 + len(date_columns), 'Manager Kebun', wbf['content_center'])

            row += 4
