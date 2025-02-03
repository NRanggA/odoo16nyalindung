from odoo import models
from datetime import datetime, timedelta

class ReportSummaryAttendance(models.AbstractModel):
    _name = 'report.nyalindung_report.summary_attendance_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Summary Attendance Excel"

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

        sheet = workbook.add_worksheet("Summary Attendance")
        sheet2 = workbook.add_worksheet("Holiday")
        sheet3 = workbook.add_worksheet("Koreksi")
        row = 0
        row2 = 0
        row3 = 0
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
            sheet.merge_range(row, 3, row + 1, 4, 'JUMLAH', wbf['header'])

            if from_date and to_date:
                delta = to_date - from_date
                date_columns = []
                for i in range(delta.days + 1):
                    current_date = from_date + timedelta(days=i)
                    date_columns.append(current_date.strftime('%d'))

                start_col = 12
                end_col = start_col + len(date_columns) - 1
                
                sheet.merge_range(row, start_col, row + 1, end_col, 'TANGGAL', wbf['header'])
                for i, date in enumerate(date_columns):
                    sheet.write(row + 2, start_col + i, date, wbf['header'])
                    sheet.set_column(start_col + i, start_col + i, 5)

            hko_start = 5
            sheet.merge_range(row, hko_start, row + 1, hko_start + 5, 'JUMLAH HKO', wbf['header'])

            total_hk_start = hko_start + 6
            sheet.merge_range(row, total_hk_start, row + 2, total_hk_start, 'TOTAL HK', wbf['header'])

            # Header 2
            sheet.write(row + 2, 0, 'NO.', wbf['header'])
            sheet.write(row + 2, 1, 'NIK', wbf['header'])
            sheet.set_column(5, 1, 13)
            sheet.write(row + 2, 2, 'NAMA', wbf['header'])
            sheet.set_column(5, 2, 22)
            sheet.write(row + 2, 3, 'BSH', wbf['biru_muda'])
            sheet.set_column(5, 3, 8)
            sheet.write(row + 2, 4, 'KRG', wbf['biru_muda'])
            sheet.set_column(5, 4, 8)

            hko_headers = ['HKO', 'L', 'S', 'P', 'CT', 'M']
            hko_formats = [self.wbf['biru_muda'], self.wbf['hijau_tua'], self.wbf['kuning'], self.wbf['biru_tua'], self.wbf['biru_muda'], self.wbf['merah']]
            # tunjangan_headers = ['MG', 'RY', 'S', 'CT']
            # tunjangan_formats = [self.wbf['merah'], self.wbf['kuning'], self.wbf['kuning'], self.wbf['kuning']]

            for i, header in enumerate(hko_headers):
                sheet.write(row + 2, hko_start + i, header, hko_formats[i])

            # for i, header in enumerate(tunjangan_headers):
            #     sheet.write(5, tunjangan_start + i, header, tunjangan_formats[i])

            # Bagian Isi Data
            query = """
                WITH employee_data AS (
                    SELECT 
                        emp.id AS emp_id,
                        emp.name AS employee_name,
                        emp.no_induk as no_induk
                    FROM 
                        hr_employee emp
                    WHERE emp.kemandoran_id = %s
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
                    trans_data ON employee_data.emp_id = trans_data.employee_id
                GROUP BY 
                    employee_data.emp_id, 
                    employee_data.no_induk,
                    employee_data.employee_name
                ORDER BY
                    employee_data.employee_name ASC;
            """

            self.env.cr.execute(query, (kemandoran.id, from_date, to_date))
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
                sheet.write(row, 3, total_hasil_convert_lump_bagi_2, wbf['data'])
                sheet.write(row, 4, total_hasil_convert_latex_bagi_2, wbf['data'])

                current_col = 12
                hko_count = 0
                l_count = 0
                s_count = 0
                p_count = 0
                ct_count = 0
                m_count = 0

                for i in range(delta.days + 1):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', from_date + timedelta(days=i))
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
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
                sheet.write(row, total_hk_start, sum([hko_count, l_count, s_count, p_count, ct_count, m_count]), wbf['data_center'])


                row += 1
                nomor += 1

            # Logika untuk Mandor
            row += 1
            sheet.write(row, 0, 'M-1', wbf['data_center'])
            sheet.write(row, 1, mandor_nik, wbf['data'])
            sheet.write(row, 2, mandor_name, wbf['data'])
            sheet.write(row, 3, 0, wbf['content_number'])
            sheet.write(row, 4, 0, wbf['content_number'])

            mandor_hko_count = 0
            mandor_l_count = 0
            mandor_s_count = 0
            mandor_p_count = 0
            mandor_ct_count = 0
            mandor_m_count = 0

            mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id', '=', "Mandor Besar"),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)

                type_code = attendance.type_id.code if attendance else '-'
                sheet.write(row, 12 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet.write(row, 12 + i, type_code, wbf['hijau_muda'])
                    mandor_hko_count += 1
                elif type_code == 'L':
                    sheet.write(row, 12 + i, type_code, wbf['hijau_tua'])
                    mandor_l_count += 1
                elif type_code == 'S1':
                    sheet.write(row, 12 + i, type_code, wbf['kuning'])
                    mandor_s_count += 1
                elif type_code == 'P':
                    sheet.write(row, 12 + i, type_code, wbf['biru_tua'])
                    mandor_p_count += 1
                elif type_code == 'CT':
                    sheet.write(row, 12 + i, type_code, wbf['biru_muda'])
                    mandor_ct_count += 1
                elif type_code == 'M':
                    sheet.write(row, 12 + i, type_code, wbf['merah'])
                    mandor_m_count += 1

            sheet.write(row, hko_start, mandor_hko_count, wbf['biru_muda'])
            sheet.write(row, hko_start + 1, mandor_l_count, wbf['data_center'])
            sheet.write(row, hko_start + 2, mandor_s_count, wbf['data_center'])
            sheet.write(row, hko_start + 3, mandor_p_count, wbf['data_center'])
            sheet.write(row, hko_start + 4, mandor_ct_count, wbf['data_center'])
            sheet.write(row, hko_start + 5, mandor_m_count, wbf['data_center'])

            # sheet.write(row, tunjangan_start, '-', wbf['data_center'])
            # sheet.write(row, tunjangan_start + 1, '-', wbf['data_center'])
            # sheet.write(row, tunjangan_start + 2, '-', wbf['data_center'])
            # sheet.write(row, tunjangan_start + 3, '-', wbf['data_center'])
            sheet.write(row, total_hk_start, sum([mandor_hko_count, mandor_l_count, mandor_s_count, mandor_p_count, mandor_ct_count, mandor_m_count]), wbf['data_center'])

            # Logika untuk Asisten Mandor
            row += 1
            sheet.write(row, 0, 'M-2', wbf['data_center'])
            sheet.write(row, 1, asisten_mandor_nik, wbf['data'])
            sheet.write(row, 2, asisten_mandor_name, wbf['data'])
            sheet.write(row, 3, 0, wbf['content_number'])
            sheet.write(row, 4, 0, wbf['content_number'])

            asisten_hko_count = 0
            asisten_l_count = 0
            asisten_s_count = 0
            asisten_p_count = 0
            asisten_ct_count = 0
            asisten_m_count = 0

            asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.job_id', '=', "Mandor"),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)

                type_code = attendance.type_id.code if attendance else '-'
                sheet.write(row, 12 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet.write(row, 12 + i, type_code, wbf['hijau_muda'])
                    asisten_hko_count += 1
                elif type_code == 'L':
                    sheet.write(row, 12 + i, type_code, wbf['hijau_tua'])
                    asisten_l_count += 1
                elif type_code == 'S1':
                    sheet.write(row, 12 + i, type_code, wbf['kuning'])
                    asisten_s_count += 1
                elif type_code == 'P':
                    sheet.write(row, 12 + i, type_code, wbf['biru_tua'])
                    asisten_p_count += 1
                elif type_code == 'CT':
                    sheet.write(row, 12 + i, type_code, wbf['biru_muda'])
                    asisten_ct_count += 1
                elif type_code == 'M':
                    sheet.write(row, 12 + i, type_code, wbf['merah'])
                    asisten_m_count += 1

            sheet.write(row, hko_start, asisten_hko_count, wbf['biru_muda'])
            sheet.write(row, hko_start + 1, asisten_l_count, wbf['data_center'])
            sheet.write(row, hko_start + 2, asisten_s_count, wbf['data_center'])
            sheet.write(row, hko_start + 3, asisten_p_count, wbf['data_center'])
            sheet.write(row, hko_start + 4, asisten_ct_count, wbf['data_center'])
            sheet.write(row, hko_start + 5, asisten_m_count, wbf['data_center'])
            sheet.write(row, total_hk_start, sum([asisten_hko_count, asisten_l_count, asisten_s_count, asisten_p_count, asisten_ct_count, asisten_m_count]), wbf['data_center'])

            # Logika untuk Kerani
            row += 1
            sheet.write(row, 0, 'M-3', wbf['data_center'])
            sheet.write(row, 1, kerani_nik, wbf['data'])
            sheet.write(row, 2, kerani_name, wbf['data'])
            sheet.write(row, 3, 0, wbf['content_number'])
            sheet.write(row, 4, 0, wbf['content_number'])

            kerani_hko_count = 0
            kerani_l_count = 0
            kerani_s_count = 0
            kerani_p_count = 0
            kerani_ct_count = 0
            kerani_m_count = 0

            kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)

                type_code = attendance.type_id.code if attendance else '-'
                sheet.write(row, 12 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet.write(row, 12 + i, type_code, wbf['hijau_muda'])
                    kerani_hko_count += 1
                elif type_code == 'L':
                    sheet.write(row, 12 + i, type_code, wbf['hijau_tua'])
                    kerani_l_count += 1
                elif type_code == 'S1':
                    sheet.write(row, 12 + i, type_code, wbf['kuning'])
                    kerani_s_count += 1
                elif type_code == 'P':
                    sheet.write(row, 12 + i, type_code, wbf['biru_tua'])
                    kerani_p_count += 1
                elif type_code == 'CT':
                    sheet.write(row, 12 + i, type_code, wbf['biru_muda'])
                    kerani_ct_count += 1
                elif type_code == 'M':
                    sheet.write(row, 12 + i, type_code, wbf['merah'])
                    kerani_m_count += 1

            sheet.write(row, hko_start, kerani_hko_count, wbf['biru_muda'])
            sheet.write(row, hko_start + 1, kerani_l_count, wbf['data_center'])
            sheet.write(row, hko_start + 2, kerani_s_count, wbf['data_center'])
            sheet.write(row, hko_start + 3, kerani_p_count, wbf['data_center'])
            sheet.write(row, hko_start + 4, kerani_ct_count, wbf['data_center'])
            sheet.write(row, hko_start + 5, kerani_m_count, wbf['data_center'])
            sheet.write(row, total_hk_start, sum([kerani_hko_count, kerani_l_count, kerani_s_count, kerani_p_count, kerani_ct_count, kerani_m_count]), wbf['data_center'])

            row += 1
            nomor += 1

            # 1
            row += 1
            total_hko_per_tanggal = [0] * len(date_columns)

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data:
                current_col = 12
                for i in range(len(date_columns)):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', from_date + timedelta(days=i))
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
                    if type_code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

            for i in range(len(date_columns)):
                mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id', '=', "Mandor Besar"),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)
                if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                    total_hko_per_tanggal[i] += 1

                asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.job_id', '=', "Mandor"),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)
                if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                    total_hko_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)
                if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
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
            sheet.write(row, 9, '-', wbf['data_center'])
            sheet.write(row, 10, '-', wbf['data_center'])

            for i in range(len(date_columns)):
                sheet.write(row, 12 + i, total_hko_per_tanggal[i], wbf['data_center'])

            # start_col = 12 + len(date_columns)
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
                total_bsh += total_hasil_convert_lump_bagi_2
                total_krg += total_hasil_convert_latex_bagi_2
                current_col = 12
                for i in range(len(date_columns)):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', from_date + timedelta(days=i))
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
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

            for i in range(len(date_columns)):
                mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id', '=', "Mandor Besar"),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

                asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.job_id', '=', "Mandor"),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i))
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

            row += 1
            sheet.merge_range(row, 0, row, 2, "JUMLAH TOTAL", wbf['jumlah_total'])
            sheet.write(row, 3, total_bsh, wbf['kuning'])
            sheet.write(row, 4, total_krg, wbf['kuning'])

            for i in range(len(date_columns)):
                sheet.write(row, 12 + i, '', wbf['kuning'])

            sheet.write(row, hko_start, sum(total_hko_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 1, sum(total_l_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 2, sum(total_s_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 3, sum(total_p_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 4, sum(total_ct_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, hko_start + 5, sum(total_m_per_tanggal), wbf['hijau_tua'])
            sheet.write(row, total_hk_start, sum([sum(total_hko_per_tanggal), sum(total_l_per_tanggal), sum(total_s_per_tanggal), sum(total_p_per_tanggal), sum(total_ct_per_tanggal), sum(total_m_per_tanggal)]), wbf['hijau_tua'])

            row += 1


            # TTD 1
            row += 1

            for i in range(len(date_columns)):
                sheet.write(row, 5 + i, '', wbf['content_center'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_columns)
            sheet.merge_range(row, start_col, row, start_col + 3, f'Nyalindung, {current_date}', wbf['content_center'])

            # TTD 2
            row += 1
            sheet.merge_range(row, 0, row, 4, 'Mengetahui,', wbf['content_center'])
            sheet.merge_range(row, 6, row, 6 + len(date_columns), 'Menyetujui,', wbf['content_center'])


            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_columns)
            sheet.merge_range(row, start_col, row, start_col + 3, 'Dibuat Oleh', wbf['content_center'])

            # TTD 3
            row += 6
            sheet.merge_range(row, 0, row, 1, 'Hendra', wbf['center_bold'])
            sheet.merge_range(row, 3, row, 4, 'Ilmiano Swara', wbf['center_bold'])
            sheet.merge_range(row, 6, row, 6 + len(date_columns), 'Wahyu Widiyanto', wbf['center_bold'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_columns)
            sheet.merge_range(row, start_col, row, start_col + 3, 'Hani Andriani', wbf['center_bold'])

            # TTD 4
            row += 1
            sheet.merge_range(row, 0, row, 1, 'Mandor Besar Karet', wbf['content_center'])
            sheet.merge_range(row, 3, row, 4, 'Asisten Kebun', wbf['content_center'])
            sheet.merge_range(row, 6, row, 6 + len(date_columns), 'Manager Kebun', wbf['content_center'])

            row += 4

##################################################### Holiday #####################################################

            sheet2.write(row2, 0, 'BLOK')
            sheet2.write(row2, 1,':', wbf['content_center'])
            sheet2.write(row2, 2, kemandoran.name)
            row2 += 1
            sheet2.write(row2, 0, 'BULAN')
            sheet2.write(row2, 1,':', wbf['content_center'])
            sheet2.write(row2, 2, f'{from_date.strftime("%d-%m-%Y")} s/d {to_date.strftime("%d-%m-%Y")}' if from_date and to_date else '')
            row2 += 2
            # Bagian Header 1
            sheet2.merge_range(row2, 0, row2 + 1, 2, kemandoran.name or '', wbf['kemandoran'])
            sheet2.merge_range(row2, 3, row2 + 1, 4, 'JUMLAH', wbf['header'])

            if from_date and to_date:
                delta = to_date - from_date
                date_columns = []
                holiday_dates = []
                for i in range(delta.days + 1):
                    current_date = from_date + timedelta(days=i)
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_holiday', '=', True)
                    ], limit=1)
                    if attendance:
                        date_columns.append(current_date.strftime('%d'))
                        holiday_dates.append(current_date)
            
            if date_columns:
                start_col = 12
                end_col = start_col + len(date_columns) - 1
                
                sheet2.merge_range(row2, start_col, row2 + 1, end_col, 'TANGGAL', wbf['header'])
                for i, date in enumerate(date_columns):
                    sheet2.write(row2 + 2, start_col + i, date, wbf['header'])
                    sheet2.set_column(start_col + i, start_col + i, 5)

            hko_start = 5
            sheet2.merge_range(row2, hko_start, row2 + 1, hko_start + 5, 'JUMLAH HKO', wbf['header'])

            total_hk_start = hko_start + 6
            sheet2.merge_range(row2, total_hk_start, row2 + 2, total_hk_start, 'TOTAL HK', wbf['header'])

            # Header 2
            sheet2.write(row2 + 2, 0, 'NO.', wbf['header'])
            sheet2.write(row2 + 2, 1, 'NIK', wbf['header'])
            sheet2.set_column(5, 1, 13)
            sheet2.write(row2 + 2, 2, 'NAMA', wbf['header'])
            sheet2.set_column(5, 2, 22)
            sheet2.write(row2 + 2, 3, 'BSH', wbf['biru_muda'])
            sheet2.set_column(5, 3, 8)
            sheet2.write(row2 + 2, 4, 'KRG', wbf['biru_muda'])
            sheet2.set_column(5, 4, 8)

            hko_headers = ['HKO', 'L', 'S', 'P', 'CT', 'M']
            hko_formats = [self.wbf['biru_muda'], self.wbf['hijau_tua'], self.wbf['kuning'], self.wbf['biru_tua'], self.wbf['biru_muda'], self.wbf['merah']]
            # tunjangan_headers = ['MG', 'RY', 'S', 'CT']
            # tunjangan_formats = [self.wbf['merah'], self.wbf['kuning'], self.wbf['kuning'], self.wbf['kuning']]

            for i, header in enumerate(hko_headers):
                sheet2.write(row2 + 2, hko_start + i, header, hko_formats[i])

            # for i, header in enumerate(tunjangan_headers):
            #     sheet2.write(5, tunjangan_start + i, header, tunjangan_formats[i])

            # Bagian Isi Data
            query = """
                WITH employee_data AS (
                    SELECT 
                        emp.id AS emp_id,
                        emp.name AS employee_name,
                        emp.no_induk as no_induk
                    FROM 
                        hr_employee emp
                    WHERE emp.kemandoran_id = %s
                ),
                holidays AS (
                    SELECT date FROM hr_attendance_sheet WHERE is_holiday = TRUE
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
                        AND trans.date IN (SELECT date FROM holidays)
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
                    trans_data ON employee_data.emp_id = trans_data.employee_id
                GROUP BY 
                    employee_data.emp_id, 
                    employee_data.no_induk,
                    employee_data.employee_name
                ORDER BY
                    employee_data.employee_name ASC;
            """

            self.env.cr.execute(query, (kemandoran.id, from_date, to_date))
            karyawan_data = self.env.cr.fetchall()

            row2 += 4
            nomor = 1

            mandor_name = kemandoran.kepala_mandor_id.name if kemandoran.kepala_mandor_id else ''
            mandor_nik = kemandoran.kepala_mandor_id.no_induk if kemandoran.kepala_mandor_id else ''
            asisten_mandor_name = kemandoran.mandor_id.name if kemandoran.mandor_id else ''
            asisten_mandor_nik = kemandoran.mandor_id.no_induk if kemandoran.mandor_id else ''
            kerani_name = kemandoran.assisten_id.name if kemandoran.assisten_id else ''
            kerani_nik = kemandoran.assisten_id.no_induk if kemandoran.assisten_id else ''

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data:
                sheet2.write(row2, 0, nomor, wbf['data_center'])
                sheet2.write(row2, 1, no_induk, wbf['data'])
                sheet2.write(row2, 2, employee_name, wbf['data'])
                sheet2.write(row2, 3, total_hasil_convert_lump_bagi_2, wbf['data'])
                sheet2.write(row2, 4, total_hasil_convert_latex_bagi_2, wbf['data'])

                hko_count = 0
                l_count = 0
                s_count = 0
                p_count = 0
                ct_count = 0
                m_count = 0

                current_col = start_col
                for current_date in holiday_dates:
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_holiday', '=', True)
                    ], limit=1)
                    
                    if not attendance:
                        continue

                    type_code = attendance.type_id.code if attendance else '-'
                    sheet2.write(row2, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet2.write(row2, current_col, type_code, wbf['hijau_muda'])
                        hko_count += 1
                    elif type_code == 'L':
                        sheet2.write(row2, current_col, type_code, wbf['hijau_tua'])
                        l_count += 1
                    elif type_code == 'S1':
                        sheet2.write(row2, current_col, type_code, wbf['kuning'])
                        s_count += 1
                    elif type_code == 'P':
                        sheet2.write(row2, current_col, type_code, wbf['biru_tua'])
                        p_count += 1
                    elif type_code == 'CT':
                        sheet2.write(row2, current_col, type_code, wbf['biru_muda'])
                        ct_count += 1
                    elif type_code == 'M':
                        sheet2.write(row2, current_col, type_code, wbf['merah'])
                        m_count += 1
                    elif type_code is None:
                        sheet2.write(row2, current_col, '-', wbf['content_center'])
                        m_count += 1

                    current_col += 1

                sheet2.write(row2, hko_start, hko_count, wbf['biru_muda'])
                sheet2.write(row2, hko_start + 1, l_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 2, s_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 3, p_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 4, ct_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 5, m_count, wbf['data_center'])
                sheet2.write(row2, total_hk_start, sum([hko_count, l_count, s_count, p_count, ct_count, m_count]), wbf['data_center'])


                row2 += 1
                nomor += 1

            # Logika untuk Mandor
            row2 += 1
            sheet2.write(row2, 0, 'M-1', wbf['data_center'])
            sheet2.write(row2, 1, mandor_nik, wbf['data'])
            sheet2.write(row2, 2, mandor_name, wbf['data'])
            sheet2.write(row2, 3, 0, wbf['content_number'])
            sheet2.write(row2, 4, 0, wbf['content_number'])

            current_col = start_col
            mandor_hko_count = 0
            mandor_l_count = 0
            mandor_s_count = 0
            mandor_p_count = 0
            mandor_ct_count = 0
            mandor_m_count = 0

            mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)
            if mandor_employee:
                for i, current_date in enumerate(holiday_dates):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', mandor_employee.name),
                        ('employee_id.active', '=', True),
                        ('employee_id.sub_department_id.name', '=', "Mandor Besar"),
                        ('date', '=', current_date),
                        ('is_holiday', '=', True)
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
                    sheet2.write(row2, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet2.write(row2, current_col, type_code, wbf['hijau_muda'])
                        mandor_hko_count += 1
                    elif type_code == 'L':
                        sheet2.write(row2, current_col, type_code, wbf['hijau_tua'])
                        mandor_l_count += 1
                    elif type_code == 'S1':
                        sheet2.write(row2, current_col, type_code, wbf['kuning'])
                        mandor_s_count += 1
                    elif type_code == 'P':
                        sheet2.write(row2, current_col, type_code, wbf['biru_tua'])
                        mandor_p_count += 1
                    elif type_code == 'CT':
                        sheet2.write(row2, current_col, type_code, wbf['biru_muda'])
                        mandor_ct_count += 1
                    elif type_code == 'M':
                        sheet2.write(row2, current_col, type_code, wbf['merah'])
                        mandor_m_count += 1

                    current_col += 1

            sheet2.write(row2, hko_start, mandor_hko_count, wbf['biru_muda'])
            sheet2.write(row2, hko_start + 1, mandor_l_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 2, mandor_s_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 3, mandor_p_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 4, mandor_ct_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 5, mandor_m_count, wbf['data_center'])
            sheet2.write(row2, total_hk_start, sum([mandor_hko_count, mandor_l_count, mandor_s_count, mandor_p_count, mandor_ct_count, mandor_m_count]), wbf['data_center'])


            # Logika untuk Asisten Mandor
            row2 += 1
            sheet2.write(row2, 0, 'M-2', wbf['data_center'])
            sheet2.write(row2, 1, asisten_mandor_nik, wbf['data'])
            sheet2.write(row2, 2, asisten_mandor_name, wbf['data'])
            sheet2.write(row2, 3, 0, wbf['content_number'])
            sheet2.write(row2, 4, 0, wbf['content_number'])

            current_col = start_col
            asisten_hko_count = 0
            asisten_l_count = 0
            asisten_s_count = 0
            asisten_p_count = 0
            asisten_ct_count = 0
            asisten_m_count = 0

            asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
            if asisten_employee:
                for i, current_date in enumerate(holiday_dates):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', asisten_employee.name),
                        ('employee_id.active', '=', True),
                        ('employee_id.job_id', '=', "Mandor"),
                        ('date', '=', current_date),
                        ('is_holiday', '=', True)
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
                    sheet2.write(row2, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet2.write(row2, current_col, type_code, wbf['hijau_muda'])
                        asisten_hko_count += 1
                    elif type_code == 'L':
                        sheet2.write(row2, current_col, type_code, wbf['hijau_tua'])
                        asisten_l_count += 1
                    elif type_code == 'S1':
                        sheet2.write(row2, current_col, type_code, wbf['kuning'])
                        asisten_s_count += 1
                    elif type_code == 'P':
                        sheet2.write(row2, current_col, type_code, wbf['biru_tua'])
                        asisten_p_count += 1
                    elif type_code == 'CT':
                        sheet2.write(row2, current_col, type_code, wbf['biru_muda'])
                        asisten_ct_count += 1
                    elif type_code == 'M':
                        sheet2.write(row2, current_col, type_code, wbf['merah'])
                        asisten_m_count += 1
                    
                    current_col += 1

                sheet2.write(row2, hko_start, asisten_hko_count, wbf['biru_muda'])
                sheet2.write(row2, hko_start + 1, asisten_l_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 2, asisten_s_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 3, asisten_p_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 4, asisten_ct_count, wbf['data_center'])
                sheet2.write(row2, hko_start + 5, asisten_m_count, wbf['data_center'])
                sheet2.write(row2, total_hk_start, sum([asisten_hko_count, asisten_l_count, asisten_s_count, asisten_p_count, asisten_ct_count, asisten_m_count]), wbf['data_center'])

            # Logika untuk Kerani
            row2 += 1
            sheet2.write(row2, 0, 'M-3', wbf['data_center'])
            sheet2.write(row2, 1, kerani_nik, wbf['data'])
            sheet2.write(row2, 2, kerani_name, wbf['data'])
            sheet2.write(row2, 3, 0, wbf['content_number'])
            sheet2.write(row2, 4, 0, wbf['content_number'])

            kerani_hko_count = 0
            kerani_l_count = 0
            kerani_s_count = 0
            kerani_p_count = 0
            kerani_ct_count = 0
            kerani_m_count = 0

            kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)

            for i in range(len(date_columns)):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('is_holiday', '=', True)
                ], limit=1)

                type_code = attendance.type_id.code if attendance else '-'
                sheet2.write(row2, 12 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet2.write(row2, 12 + i, type_code, wbf['hijau_muda'])
                    kerani_hko_count += 1
                elif type_code == 'L':
                    sheet2.write(row2, 12 + i, type_code, wbf['hijau_tua'])
                    kerani_l_count += 1
                elif type_code == 'S1':
                    sheet2.write(row2, 12 + i, type_code, wbf['kuning'])
                    kerani_s_count += 1
                elif type_code == 'P':
                    sheet2.write(row2, 12 + i, type_code, wbf['biru_tua'])
                    kerani_p_count += 1
                elif type_code == 'CT':
                    sheet2.write(row2, 12 + i, type_code, wbf['biru_muda'])
                    kerani_ct_count += 1
                elif type_code == 'M':
                    sheet2.write(row2, 12 + i, type_code, wbf['merah'])
                    kerani_m_count += 1

            sheet2.write(row2, hko_start, kerani_hko_count, wbf['biru_muda'])
            sheet2.write(row2, hko_start + 1, kerani_l_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 2, kerani_s_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 3, kerani_p_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 4, kerani_ct_count, wbf['data_center'])
            sheet2.write(row2, hko_start + 5, kerani_m_count, wbf['data_center'])
            sheet2.write(row2, total_hk_start, sum([kerani_hko_count, kerani_l_count, kerani_s_count, kerani_p_count, kerani_ct_count, kerani_m_count]), wbf['data_center'])

            row2 += 1
            nomor += 1

            # 1
            row2 += 1
            total_hko_per_tanggal = [0] * len(date_columns)

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data:
                for i, current_date in enumerate(holiday_dates):
                    attendances = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_holiday', '=', True)
                    ])
                    for attendance in attendances:
                        type_code = attendance.type_id.code if attendance.type_id else '-'
                        if type_code in ['KJ', 'KJI', 'KJO']:
                            total_hko_per_tanggal[i] += 1

            for i, current_date in enumerate(holiday_dates):
                attendances = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id.name', '=', "Mandor Besar"),
                    ('date', '=', current_date),
                    ('is_holiday', '=', True)
                ])
                for attendance in attendances:
                    if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

            for i, current_date in enumerate(holiday_dates):
                attendances = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id.name', '=', "Mandor"),
                    ('date', '=', current_date),
                    ('is_holiday', '=', True)
                ])
                for attendance in attendances:
                    if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

                # asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
                # attendance = self.env['hr.attendance.sheet'].search([
                #     ('employee_id', '=', asisten_employee.name),
                #     ('employee_id.job_id', '=', "Mandor"),
                #     ('date', '=', from_date + timedelta(days=i)),
                #     ('is_holiday', '=', True)
                # ], limit=1)
                # if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                #     total_hko_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('is_holiday', '=', True)
                ], limit=1)
                if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                    total_hko_per_tanggal[i] += 1

            sheet2.write(row2, 0, '-', wbf['data_center'])
            sheet2.write(row2, 1, '-', wbf['data_center'])
            sheet2.write(row2, 2, '-', wbf['data_center'])
            sheet2.write(row2, 3, '-', wbf['data_center'])
            sheet2.write(row2, 4, '-', wbf['data_center'])
            sheet2.write(row2, 5, '-', wbf['data_center'])
            sheet2.write(row2, 6, '-', wbf['data_center'])
            sheet2.write(row2, 7, '-', wbf['data_center'])
            sheet2.write(row2, 8, '-', wbf['data_center'])
            sheet2.write(row2, 9, '-', wbf['data_center'])
            sheet2.write(row2, 10, '-', wbf['data_center'])

            for i in range(len(date_columns)):
                sheet2.write(row2, 12 + i, total_hko_per_tanggal[i], wbf['data_center'])

            # start_col = 12 + len(date_columns)
            # for i in range(6):
            #     sheet2.write(row2, start_col + i, '-', wbf['data_center'])

            sheet2.write(row2, total_hk_start, '-', wbf['data_center'])

            #2
            row2 += 1
            total_bsh = 0
            total_krg = 0
            total_hko_per_tanggal = [0] * len(date_columns)
            total_l_per_tanggal = [0] * len(date_columns)
            total_s_per_tanggal = [0] * len(date_columns)
            total_p_per_tanggal = [0] * len(date_columns)
            total_ct_per_tanggal = [0] * len(date_columns)
            total_m_per_tanggal = [0] * len(date_columns)

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data:
                total_bsh += total_hasil_convert_lump_bagi_2
                total_krg += total_hasil_convert_latex_bagi_2
                current_col = 12
                for i, current_date in enumerate(holiday_dates):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_holiday', '=', True)
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
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

            for i, current_date in enumerate(holiday_dates):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id', '=', "Mandor Besar"),
                    ('date', '=', current_date),
                    ('is_holiday', '=', True)
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

            for i, current_date in enumerate(holiday_dates):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.job_id', '=', "Mandor"),
                    ('date', '=', current_date),
                    ('is_holiday', '=', True)
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('is_holiday', '=', True)
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

            row2 += 1
            sheet2.merge_range(row2, 0, row2, 2, "JUMLAH TOTAL", wbf['jumlah_total'])
            sheet2.write(row2, 3, total_bsh, wbf['kuning'])
            sheet2.write(row2, 4, total_krg, wbf['kuning'])

            for i in range(len(date_columns)):
                sheet2.write(row2, 12 + i, '', wbf['kuning'])

            sheet2.write(row2, hko_start, sum(total_hko_per_tanggal), wbf['hijau_tua'])
            sheet2.write(row2, hko_start + 1, sum(total_l_per_tanggal), wbf['hijau_tua'])
            sheet2.write(row2, hko_start + 2, sum(total_s_per_tanggal), wbf['hijau_tua'])
            sheet2.write(row2, hko_start + 3, sum(total_p_per_tanggal), wbf['hijau_tua'])
            sheet2.write(row2, hko_start + 4, sum(total_ct_per_tanggal), wbf['hijau_tua'])
            sheet2.write(row2, hko_start + 5, sum(total_m_per_tanggal), wbf['hijau_tua'])
            sheet2.write(row2, total_hk_start, sum([sum(total_hko_per_tanggal), sum(total_l_per_tanggal), sum(total_s_per_tanggal), sum(total_p_per_tanggal), sum(total_ct_per_tanggal), sum(total_m_per_tanggal)]), wbf['hijau_tua'])

            row2 += 1


            # TTD 1
            row2 += 1

            for i in range(len(date_columns)):
                sheet2.write(row2, 5 + i, '', wbf['content_center'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_columns)
            sheet2.merge_range(row2, start_col, row2, start_col + 3, f'Nyalindung, {current_date}', wbf['content_center'])

            # TTD 2
            row2 += 1
            sheet2.merge_range(row2, 0, row2, 4, 'Mengetahui,', wbf['content_center'])
            sheet2.merge_range(row2, 6, row2, 6 + len(date_columns), 'Menyetujui,', wbf['content_center'])


            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_columns)
            sheet2.merge_range(row2, start_col, row2, start_col + 3, 'Dibuat Oleh', wbf['content_center'])

            # TTD 3
            row2 += 6
            sheet2.merge_range(row2, 0, row2, 1, 'Hendra', wbf['center_bold'])
            sheet2.merge_range(row2, 3, row2, 4, 'Ilmiano Swara', wbf['center_bold'])
            sheet2.merge_range(row2, 6, row2, 6 + len(date_columns), 'Wahyu Widiyanto', wbf['center_bold'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_columns)
            sheet2.merge_range(row2, start_col, row2, start_col + 3, 'Hani Andriani', wbf['center_bold'])

            # TTD 4
            row2 += 1
            sheet2.merge_range(row2, 0, row2, 1, 'Mandor Besar Karet', wbf['content_center'])
            sheet2.merge_range(row2, 3, row2, 4, 'Asisten Kebun', wbf['content_center'])
            sheet2.merge_range(row2, 6, row2, 6 + len(date_columns), 'Manager Kebun', wbf['content_center'])

            row2 += 4


##################################################### KOREKSI #####################################################

            sheet3.write(row3, 0, 'BLOK')
            sheet3.write(row3, 1,':', wbf['content_center'])
            sheet3.write(row3, 2, kemandoran.name)
            row3 += 1
            sheet3.write(row3, 0, 'BULAN')
            sheet3.write(row3, 1,':', wbf['content_center'])
            sheet3.write(row3, 2, f'{from_date.strftime("%d-%m-%Y")} s/d {to_date.strftime("%d-%m-%Y")}' if from_date and to_date else '')
            row3 += 2
            # Bagian Header 1
            sheet3.merge_range(row3, 0, row3 + 1, 2, kemandoran.name or '', wbf['kemandoran'])
            sheet3.merge_range(row3, 3, row3 + 1, 4, 'JUMLAH', wbf['header'])


            if from_date and to_date:
                delta = to_date - from_date
                date_column_correction = []
                correction_dates = []
                for i in range(delta.days + 1):
                    current_date = from_date + timedelta(days=i)
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_correction', '=', True)
                    ], limit=1)
                    
                    # if attendance:
                    date_column_correction.append(current_date.strftime('%d'))
                    correction_dates.append(current_date)

                    
            if date_column_correction:
                start_col = 12
                end_col = start_col + len(date_column_correction) - 1
                
                sheet3.merge_range(row3, start_col, row3 + 1, end_col, 'TANGGAL', wbf['header'])
                for i, date in enumerate(date_column_correction):
                    sheet3.write(row3 + 2, start_col + i, date, wbf['header'])
                    sheet3.set_column(start_col + i, start_col + i, 5)

            hko_start = 5
            sheet3.merge_range(row3, hko_start, row3 + 1, hko_start + 5, 'JUMLAH HKO', wbf['header'])

            total_hk_start = hko_start + 6
            sheet3.merge_range(row3, total_hk_start, row3 + 2, total_hk_start, 'TOTAL HK', wbf['header'])

            # Header 2
            sheet3.write(row3 + 2, 0, 'NO.', wbf['header'])
            sheet3.write(row3 + 2, 1, 'NIK', wbf['header'])
            sheet3.set_column(5, 1, 13)
            sheet3.write(row3 + 2, 2, 'NAMA', wbf['header'])
            sheet3.set_column(5, 2, 22)
            sheet3.write(row3 + 2, 3, 'BSH', wbf['biru_muda'])
            sheet3.set_column(5, 3, 8)
            sheet3.write(row3 + 2, 4, 'KRG', wbf['biru_muda'])
            sheet3.set_column(5, 4, 8)

            hko_headers = ['HKO', 'L', 'S', 'P', 'CT', 'M']
            hko_formats = [self.wbf['biru_muda'], self.wbf['hijau_tua'], self.wbf['kuning'], self.wbf['biru_tua'], self.wbf['biru_muda'], self.wbf['merah']]
            # tunjangan_headers = ['MG', 'RY', 'S', 'CT']
            # tunjangan_formats = [self.wbf['merah'], self.wbf['kuning'], self.wbf['kuning'], self.wbf['kuning']]

            for i, header in enumerate(hko_headers):
                sheet3.write(row3 + 2, hko_start + i, header, hko_formats[i])

            # for i, header in enumerate(tunjangan_headers):
            #     sheet3.write(5, tunjangan_start + i, header, tunjangan_formats[i])

            # Bagian Isi Data
            # query = """
            #     WITH employee_data AS (
            #         SELECT 
            #             emp.id AS emp_id,
            #             emp.name AS employee_name,
            #             emp.no_induk as no_induk
            #         FROM 
            #             hr_employee emp
            #         WHERE emp.kemandoran_id = %s
            #     ),
            #     corrections AS (
            #         SELECT date FROM hr_attendance_sheet WHERE is_correction = TRUE
            #     ),
            #     trans_data AS (
            #         SELECT 
            #             trans_nap_line.hasil_convert_latex,
            #             trans_nap_line.hasil_convert_lump,  
            #             trans.date, 
            #             trans_line.employee_id
            #         FROM 
            #             lhm_transaction_nap_line trans_nap_line
            #         JOIN 
            #             lhm_transaction_line trans_line ON trans_line.id = trans_nap_line.lhm_transaction_line_id
            #         JOIN 
            #             lhm_transaction trans ON trans.id = trans_line.lhm_id
            #         WHERE 
            #             trans.date BETWEEN %s AND %s
            #             AND trans.date IN (SELECT date FROM corrections)
            #     )
            #     SELECT 
            #         employee_data.emp_id,
            #         employee_data.employee_name,
            #         employee_data.no_induk,
            #         SUM(COALESCE(trans_data.hasil_convert_latex, 0)) AS total_hasil_convert_latex_bagi_2,
            #         SUM(COALESCE(trans_data.hasil_convert_lump, 0)) AS total_hasil_convert_lump_bagi_2
            #     FROM 
            #         employee_data
            #     LEFT JOIN 
            #         trans_data ON employee_data.emp_id = trans_data.employee_id
            #     GROUP BY 
            #         employee_data.emp_id, 
            #         employee_data.no_induk,
            #         employee_data.employee_name
            #     ORDER BY
            #         employee_data.employee_name ASC;
            # """

            query = """
                WITH employee_data AS (
                    SELECT 
                        emp.id AS emp_id,
                        emp.name AS employee_name,
                        emp.no_induk AS no_induk
                    FROM 
                        hr_employee emp
                    WHERE emp.kemandoran_id = %s
                ),
                corrections AS (
                    SELECT DISTINCT date, employee_id 
                    FROM hr_attendance_sheet 
                    WHERE is_correction = TRUE
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
                        AND (trans.date, trans_line.employee_id) IN (SELECT date, employee_id FROM corrections)
                )
                SELECT 
                    employee_data.emp_id,
                    employee_data.employee_name,
                    employee_data.no_induk,
                    SUM(COALESCE(trans_data.hasil_convert_latex, 0)) AS total_hasil_convert_latex_bagi_2,
                    SUM(COALESCE(trans_data.hasil_convert_lump, 0)) AS total_hasil_convert_lump_bagi_2
                FROM 
                    employee_data
                JOIN 
                    corrections ON employee_data.emp_id = corrections.employee_id -- Hanya yang ada koreksi
                LEFT JOIN 
                    trans_data ON employee_data.emp_id = trans_data.employee_id
                GROUP BY 
                    employee_data.emp_id, 
                    employee_data.no_induk,
                    employee_data.employee_name
                ORDER BY
                    employee_data.employee_name ASC;
            """


            self.env.cr.execute(query, (kemandoran.id, from_date, to_date))
            karyawan_data_correction = self.env.cr.fetchall()

            row3 += 4
            nomor = 1

            mandor_name = kemandoran.kepala_mandor_id.name if kemandoran.kepala_mandor_id else ''
            mandor_nik = kemandoran.kepala_mandor_id.no_induk if kemandoran.kepala_mandor_id else ''
            asisten_mandor_name = kemandoran.mandor_id.name if kemandoran.mandor_id else ''
            asisten_mandor_nik = kemandoran.mandor_id.no_induk if kemandoran.mandor_id else ''
            kerani_name = kemandoran.assisten_id.name if kemandoran.assisten_id else ''
            kerani_nik = kemandoran.assisten_id.no_induk if kemandoran.assisten_id else ''

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data_correction:
                sheet3.write(row3, 0, nomor, wbf['data_center'])
                sheet3.write(row3, 1, no_induk, wbf['data'])
                sheet3.write(row3, 2, employee_name, wbf['data'])
                sheet3.write(row3, 3, total_hasil_convert_lump_bagi_2, wbf['data'])
                sheet3.write(row3, 4, total_hasil_convert_latex_bagi_2, wbf['data'])

                hko_count = 0
                l_count = 0
                s_count = 0
                p_count = 0
                ct_count = 0
                m_count = 0

                current_col = start_col
                for current_date in correction_dates:
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_correction', '=', True)
                    ], limit=1)
                    
                    if not attendance:
                        continue

                    type_code = attendance.type_id.code if attendance else '-'
                    sheet3.write(row3, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet3.write(row3, current_col, type_code, wbf['hijau_muda'])
                        hko_count += 1
                    elif type_code == 'L':
                        sheet3.write(row3, current_col, type_code, wbf['hijau_tua'])
                        l_count += 1
                    elif type_code == 'S1':
                        sheet3.write(row3, current_col, type_code, wbf['kuning'])
                        s_count += 1
                    elif type_code == 'P':
                        sheet3.write(row3, current_col, type_code, wbf['biru_tua'])
                        p_count += 1
                    elif type_code == 'CT':
                        sheet3.write(row3, current_col, type_code, wbf['biru_muda'])
                        ct_count += 1
                    elif type_code == 'M':
                        sheet3.write(row3, current_col, type_code, wbf['merah'])
                        m_count += 1
                    elif type_code is None:
                        sheet3.write(row3, current_col, '-', wbf['content_center'])
                        m_count += 1

                    current_col += 1

                sheet3.write(row3, hko_start, hko_count, wbf['biru_muda'])
                sheet3.write(row3, hko_start + 1, l_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 2, s_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 3, p_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 4, ct_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 5, m_count, wbf['data_center'])
                sheet3.write(row3, total_hk_start, sum([hko_count, l_count, s_count, p_count, ct_count, m_count]), wbf['data_center'])


                row3 += 1
                nomor += 1

            # Logika untuk Mandor
            row3 += 1
            sheet3.write(row3, 0, 'M-1', wbf['data_center'])
            sheet3.write(row3, 1, mandor_nik, wbf['data'])
            sheet3.write(row3, 2, mandor_name, wbf['data'])
            sheet3.write(row3, 3, 0, wbf['content_number'])
            sheet3.write(row3, 4, 0, wbf['content_number'])

            current_col = start_col
            mandor_hko_count = 0
            mandor_l_count = 0
            mandor_s_count = 0
            mandor_p_count = 0
            mandor_ct_count = 0
            mandor_m_count = 0

            mandor_employee = self.env['hr.employee'].search([('name', '=', mandor_name)], limit=1)
            if mandor_employee:
                for i, current_date in enumerate(correction_dates):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', mandor_employee.name),
                        ('employee_id.active', '=', True),
                        ('employee_id.sub_department_id.name', '=', "Mandor Besar"),
                        ('date', '=', current_date),
                        ('is_correction', '=', True)
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
                    sheet3.write(row3, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet3.write(row3, current_col, type_code, wbf['hijau_muda'])
                        mandor_hko_count += 1
                    elif type_code == 'L':
                        sheet3.write(row3, current_col, type_code, wbf['hijau_tua'])
                        mandor_l_count += 1
                    elif type_code == 'S1':
                        sheet3.write(row3, current_col, type_code, wbf['kuning'])
                        mandor_s_count += 1
                    elif type_code == 'P':
                        sheet3.write(row3, current_col, type_code, wbf['biru_tua'])
                        mandor_p_count += 1
                    elif type_code == 'CT':
                        sheet3.write(row3, current_col, type_code, wbf['biru_muda'])
                        mandor_ct_count += 1
                    elif type_code == 'M':
                        sheet3.write(row3, current_col, type_code, wbf['merah'])
                        mandor_m_count += 1

                    current_col += 1

            sheet3.write(row3, hko_start, mandor_hko_count, wbf['biru_muda'])
            sheet3.write(row3, hko_start + 1, mandor_l_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 2, mandor_s_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 3, mandor_p_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 4, mandor_ct_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 5, mandor_m_count, wbf['data_center'])
            sheet3.write(row3, total_hk_start, sum([mandor_hko_count, mandor_l_count, mandor_s_count, mandor_p_count, mandor_ct_count, mandor_m_count]), wbf['data_center'])


            # Logika untuk Asisten Mandor
            row3 += 1
            sheet3.write(row3, 0, 'M-2', wbf['data_center'])
            sheet3.write(row3, 1, asisten_mandor_nik, wbf['data'])
            sheet3.write(row3, 2, asisten_mandor_name, wbf['data'])
            sheet3.write(row3, 3, 0, wbf['content_number'])
            sheet3.write(row3, 4, 0, wbf['content_number'])

            current_col = start_col
            asisten_hko_count = 0
            asisten_l_count = 0
            asisten_s_count = 0
            asisten_p_count = 0
            asisten_ct_count = 0
            asisten_m_count = 0

            asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
            if asisten_employee:
                for i, current_date in enumerate(correction_dates):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', asisten_employee.name),
                        ('employee_id.active', '=', True),
                        ('employee_id.job_id', '=', "Mandor"),
                        ('date', '=', current_date),
                        ('is_correction', '=', True)
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
                    sheet3.write(row3, current_col, type_code, wbf['data_center'])

                    if type_code in ['KJ', 'KJI', 'KJO']:
                        sheet3.write(row3, current_col, type_code, wbf['hijau_muda'])
                        asisten_hko_count += 1
                    elif type_code == 'L':
                        sheet3.write(row3, current_col, type_code, wbf['hijau_tua'])
                        asisten_l_count += 1
                    elif type_code == 'S1':
                        sheet3.write(row3, current_col, type_code, wbf['kuning'])
                        asisten_s_count += 1
                    elif type_code == 'P':
                        sheet3.write(row3, current_col, type_code, wbf['biru_tua'])
                        asisten_p_count += 1
                    elif type_code == 'CT':
                        sheet3.write(row3, current_col, type_code, wbf['biru_muda'])
                        asisten_ct_count += 1
                    elif type_code == 'M':
                        sheet3.write(row3, current_col, type_code, wbf['merah'])
                        asisten_m_count += 1
                    
                    current_col += 1

                sheet3.write(row3, hko_start, asisten_hko_count, wbf['biru_muda'])
                sheet3.write(row3, hko_start + 1, asisten_l_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 2, asisten_s_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 3, asisten_p_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 4, asisten_ct_count, wbf['data_center'])
                sheet3.write(row3, hko_start + 5, asisten_m_count, wbf['data_center'])
                sheet3.write(row3, total_hk_start, sum([asisten_hko_count, asisten_l_count, asisten_s_count, asisten_p_count, asisten_ct_count, asisten_m_count]), wbf['data_center'])

            # Logika untuk Kerani
            row3 += 1
            sheet3.write(row3, 0, 'M-3', wbf['data_center'])
            sheet3.write(row3, 1, kerani_nik, wbf['data'])
            sheet3.write(row3, 2, kerani_name, wbf['data'])
            sheet3.write(row3, 3, 0, wbf['content_number'])
            sheet3.write(row3, 4, 0, wbf['content_number'])

            kerani_hko_count = 0
            kerani_l_count = 0
            kerani_s_count = 0
            kerani_p_count = 0
            kerani_ct_count = 0
            kerani_m_count = 0

            kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)

            for i in range(len(date_column_correction)):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('is_correction', '=', True)
                ], limit=1)

                type_code = attendance.type_id.code if attendance else '-'
                sheet3.write(row3, 12 + i, type_code, wbf['data_center'])

                if type_code in ['KJ', 'KJI', 'KJO']:
                    sheet3.write(row3, 12 + i, type_code, wbf['hijau_muda'])
                    kerani_hko_count += 1
                elif type_code == 'L':
                    sheet3.write(row3, 12 + i, type_code, wbf['hijau_tua'])
                    kerani_l_count += 1
                elif type_code == 'S1':
                    sheet3.write(row3, 12 + i, type_code, wbf['kuning'])
                    kerani_s_count += 1
                elif type_code == 'P':
                    sheet3.write(row3, 12 + i, type_code, wbf['biru_tua'])
                    kerani_p_count += 1
                elif type_code == 'CT':
                    sheet3.write(row3, 12 + i, type_code, wbf['biru_muda'])
                    kerani_ct_count += 1
                elif type_code == 'M':
                    sheet3.write(row3, 12 + i, type_code, wbf['merah'])
                    kerani_m_count += 1

            sheet3.write(row3, hko_start, kerani_hko_count, wbf['biru_muda'])
            sheet3.write(row3, hko_start + 1, kerani_l_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 2, kerani_s_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 3, kerani_p_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 4, kerani_ct_count, wbf['data_center'])
            sheet3.write(row3, hko_start + 5, kerani_m_count, wbf['data_center'])
            sheet3.write(row3, total_hk_start, sum([kerani_hko_count, kerani_l_count, kerani_s_count, kerani_p_count, kerani_ct_count, kerani_m_count]), wbf['data_center'])

            row3 += 1
            nomor += 1

            # 1
            row3 += 1
            total_hko_per_tanggal = [0] * len(date_column_correction)


            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data_correction:
                for i, current_date in enumerate(correction_dates):
                    attendances = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_correction', '=', True)
                    ])

                    for attendance in attendances:
                        type_code = attendance.type_id.code if attendance.type_id else '-'
                        if type_code in ['KJ', 'KJI', 'KJO']:
                            total_hko_per_tanggal[i] += 1

            for i, current_date in enumerate(correction_dates):
                attendances = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id.name', '=', "Mandor Besar"),
                    ('date', '=', current_date),
                    ('is_correction', '=', True)
                ])
                for attendance in attendances:
                    if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

            for i, current_date in enumerate(correction_dates):
                attendances = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id.name', '=', "Mandor"),
                    ('date', '=', current_date),
                    ('is_correction', '=', True)
                ])
                for attendance in attendances:
                    if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                        total_hko_per_tanggal[i] += 1

                # asisten_employee = self.env['hr.employee'].search([('name', '=', asisten_mandor_name)], limit=1)
                # attendance = self.env['hr.attendance.sheet'].search([
                #     ('employee_id', '=', asisten_employee.name),
                #     ('employee_id.job_id', '=', "Mandor"),
                #     ('date', '=', from_date + timedelta(days=i)),
                #     ('is_holiday', '=', True)
                # ], limit=1)
                # if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                #     total_hko_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('is_correction', '=', True)
                ], limit=1)
                if attendance.type_id.code in ['KJ', 'KJI', 'KJO']:
                    total_hko_per_tanggal[i] += 1

            sheet3.write(row3, 0, '-', wbf['data_center'])
            sheet3.write(row3, 1, '-', wbf['data_center'])
            sheet3.write(row3, 2, '-', wbf['data_center'])
            sheet3.write(row3, 3, '-', wbf['data_center'])
            sheet3.write(row3, 4, '-', wbf['data_center'])
            sheet3.write(row3, 5, '-', wbf['data_center'])
            sheet3.write(row3, 6, '-', wbf['data_center'])
            sheet3.write(row3, 7, '-', wbf['data_center'])
            sheet3.write(row3, 8, '-', wbf['data_center'])
            sheet3.write(row3, 9, '-', wbf['data_center'])
            sheet3.write(row3, 10, '-', wbf['data_center'])

            for i in range(len(date_column_correction)):
                sheet3.write(row3, 12 + i, total_hko_per_tanggal[i], wbf['data_center'])

            # start_col = 12 + len(date_column_correction)
            # for i in range(6):
            #     sheet3.write(row3, start_col + i, '-', wbf['data_center'])

            sheet3.write(row3, total_hk_start, '-', wbf['data_center'])

            #2
            row3 += 1
            total_bsh = 0
            total_krg = 0
            total_hko_per_tanggal = [0] * len(date_column_correction)
            total_l_per_tanggal = [0] * len(date_column_correction)
            total_s_per_tanggal = [0] * len(date_column_correction)
            total_p_per_tanggal = [0] * len(date_column_correction)
            total_ct_per_tanggal = [0] * len(date_column_correction)
            total_m_per_tanggal = [0] * len(date_column_correction)

            for emp_id, employee_name, no_induk, total_hasil_convert_lump_bagi_2, total_hasil_convert_latex_bagi_2 in karyawan_data_correction:
                total_bsh += total_hasil_convert_lump_bagi_2
                total_krg += total_hasil_convert_latex_bagi_2
                current_col = 12
                for i, current_date in enumerate(correction_dates):
                    attendance = self.env['hr.attendance.sheet'].search([
                        ('employee_id', '=', emp_id),
                        ('employee_id.active', '=', True),
                        ('date', '=', current_date),
                        ('is_correction', '=', True)
                    ], limit=1)

                    type_code = attendance.type_id.code if attendance else '-'
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

            for i, current_date in enumerate(correction_dates):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', mandor_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.sub_department_id', '=', "Mandor Besar"),
                    ('date', '=', current_date),
                    ('is_correction', '=', True)
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

            for i, current_date in enumerate(correction_dates):
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', asisten_employee.name),
                    ('employee_id.active', '=', True),
                    ('employee_id.job_id', '=', "Mandor"),
                    ('date', '=', current_date),
                    ('is_correction', '=', True)
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

                kerani_employee = self.env['hr.employee'].search([('name', '=', kerani_name)], limit=1)
                attendance = self.env['hr.attendance.sheet'].search([
                    ('employee_id', '=', kerani_employee.name),
                    ('employee_id.active', '=', True),
                    ('date', '=', from_date + timedelta(days=i)),
                    ('is_correction', '=', True)
                ], limit=1)
                if attendance.type_id.code == 'KJ':
                    total_hko_per_tanggal[i] += 1
                elif attendance.type_id.code == 'L':
                    total_l_per_tanggal[i] += 1
                elif attendance.type_id.code == 'S1':
                    total_s_per_tanggal[i] += 1
                elif attendance.type_id.code == 'P':
                    total_p_per_tanggal[i] += 1
                elif attendance.type_id.code == 'CT':
                    total_ct_per_tanggal[i] += 1
                elif attendance.type_id.code == 'M':
                    total_m_per_tanggal[i] += 1

            row3 += 1
            sheet3.merge_range(row3, 0, row3, 2, "JUMLAH TOTAL", wbf['jumlah_total'])
            sheet3.write(row3, 3, total_bsh, wbf['kuning'])
            sheet3.write(row3, 4, total_krg, wbf['kuning'])

            for i in range(len(date_column_correction)):
                sheet3.write(row3, 12 + i, '', wbf['kuning'])

            sheet3.write(row3, hko_start, sum(total_hko_per_tanggal), wbf['hijau_tua'])
            sheet3.write(row3, hko_start + 1, sum(total_l_per_tanggal), wbf['hijau_tua'])
            sheet3.write(row3, hko_start + 2, sum(total_s_per_tanggal), wbf['hijau_tua'])
            sheet3.write(row3, hko_start + 3, sum(total_p_per_tanggal), wbf['hijau_tua'])
            sheet3.write(row3, hko_start + 4, sum(total_ct_per_tanggal), wbf['hijau_tua'])
            sheet3.write(row3, hko_start + 5, sum(total_m_per_tanggal), wbf['hijau_tua'])
            sheet3.write(row3, total_hk_start, sum([sum(total_hko_per_tanggal), sum(total_l_per_tanggal), sum(total_s_per_tanggal), sum(total_p_per_tanggal), sum(total_ct_per_tanggal), sum(total_m_per_tanggal)]), wbf['hijau_tua'])

            row3 += 1


            # TTD 1
            row3 += 1

            for i in range(len(date_column_correction)):
                sheet3.write(row3, 5 + i, '', wbf['content_center'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_column_correction)
            sheet3.merge_range(row3, start_col, row3, start_col + 3, f'Nyalindung, {current_date}', wbf['content_center'])

            # TTD 2
            row3 += 1
            sheet3.merge_range(row3, 0, row3, 4, 'Mengetahui,', wbf['content_center'])
            sheet3.merge_range(row3, 6, row3, 6 + len(date_column_correction), 'Menyetujui,', wbf['content_center'])


            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_column_correction)
            sheet3.merge_range(row3, start_col, row3, start_col + 3, 'Dibuat Oleh', wbf['content_center'])

            # TTD 3
            row3 += 6
            sheet3.merge_range(row3, 0, row3, 1, 'Hendra', wbf['center_bold'])
            sheet3.merge_range(row3, 3, row3, 4, 'Ilmiano Swara', wbf['center_bold'])
            sheet3.merge_range(row3, 6, row3, 6 + len(date_column_correction), 'Wahyu Widiyanto', wbf['center_bold'])

            current_date = datetime.now().strftime("%d-%m-%Y")
            start_col = 8 + len(date_column_correction)
            sheet3.merge_range(row3, start_col, row3, start_col + 3, 'Hani Andriani', wbf['center_bold'])

            # TTD 4
            row3 += 1
            sheet3.merge_range(row3, 0, row3, 1, 'Mandor Besar Karet', wbf['content_center'])
            sheet3.merge_range(row3, 3, row3, 4, 'Asisten Kebun', wbf['content_center'])
            sheet3.merge_range(row3, 6, row3, 6 + len(date_column_correction), 'Manager Kebun', wbf['content_center'])

            row3 += 4
        