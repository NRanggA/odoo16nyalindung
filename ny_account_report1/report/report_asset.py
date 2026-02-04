from odoo import models
from pytz import timezone, UTC
from datetime import datetime
from dateutil.relativedelta import relativedelta
class ReportAsset(models.AbstractModel):
    _name           = 'report.ny_account_report1.report_asset_xlsx'
    _inherit        = 'report.report_xlsx.abstract'
    _description    = "Report Account Asset Excell"

    wbf = {}

    
    def add_workbook_format(self, workbook):
        # Header format untuk judul utama (misalnya, judul laporan)
        self.wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 12,
            'font_color': '#000000',
        })
        self.wbf['title_sec'] = workbook.add_format({
            'bold': False,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 12,
            'font_color': '#000000',
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
        # Format untuk header-category kolom tabel
        self.wbf['header_category'] = workbook.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10,
            'bg_color': '#F4FFC3',
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['header_category'].set_text_wrap() 
        self.wbf['header_category'].set_border()
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
            # 'num_format': 'yyyy-mm-dd',
            'num_format': 'dd/mm/yyyy',
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_date'].set_border()

        # Format konten float (angka desimal)
        self.wbf['content_float'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            # 'num_format': '#,##0.00'
            # 'num_format': '#.##,######00; -#.##,######00;"-"'
            'num_format': '#,##0.00; -#,##0.00;"-"'
        })
        self.wbf['content_float'].set_border()
        
        # Format konten float TOTAL (angka desimal)
        self.wbf['content_subtotal'] = workbook.add_format({
            'bold': True,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '#,##0.00; -#,##0.00;"-"'
        })
        self.wbf['content_subtotal'].set_border()

        self.wbf['opening_balance'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#F4FFC3',
            # 'num_format': '#.##,######00; -#.##,######00;"-"'
            'num_format': '#,##0.00; -#,##0.00;"-"'
        })
        self.wbf['opening_balance'].set_border()

        # Format untuk teks konten yang rata kiri
        self.wbf['content'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
        })
        self.wbf['content'].set_border()
        
        self.wbf['positive'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_color':'green',
            'num_format': '#,##0'
        })
        self.wbf['positive'].set_border()
        
        self.wbf['negative'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_color':'red',
            'num_format': '#,##0'
        })
        self.wbf['negative'].set_border()

        # Format untuk konten rata tengah
        self.wbf['content_center'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_center'].set_border()

        # Format untuk konten rata kanan (angka tanpa desimal)
        self.wbf['content_number'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter'
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
            'bg_color': '#F4FFC3',
            'num_format': '#,##0.00',
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

        return workbook
    
    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        date = obj.date.strftime('%d-%m-%Y') if obj.date else ''

        sheet = workbook.add_worksheet("Asset Report")
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('L:L', 20)

        row = 0

        # Periode Header
        sheet.write(row, 0, 'Laporan:', wbf['title_doc'])
        sheet.write(row, 1, f'Account Asset', wbf['title_sec'])
        row += 1

        sheet.write(row, 0, 'Tanggal:', wbf['title_doc'])
        sheet.write(row, 1, date, wbf['title_sec'])
        row += 2

        # Header Kolom
        headers = [
            "Nama", "Reference", "Asset Category", "Tanggal", "Register Code", "Equipment Code", "Gross Value",
            "Akumulasi Penyusutan Tahun Lalu",
            "Akumulasi Tahun Ini", "Akumulasi Penyusutan Periode Ini","Akumulasi Penyusutan", "Residual Value", "Sisa Masa (Bulan)"
        ]
        for col, header in enumerate(headers):
            sheet.write(row, col, header, wbf['header'])
        row += 1

        # Tambahkan ini untuk freeze header
        sheet.freeze_panes(row, 0)

        assets_categories = obj.asset_category_ids if obj.asset_category_ids else self.env['account.asset.category'].search([])
        for asset_category in assets_categories:
            for col in range(0, 12):  
                value = f"{asset_category.name}" if col == 0 else "" 
                sheet.write(row, col, value, wbf['header_category'])
            row += 1
            
            subtotal_value = 0.0
            subtotal_accum_depreciation = 0.0
            subtotal_residual = 0.0
            subtotal_penyusutan_tahun_lalu = 0.0
            subtotal_penyusutan_sebelum_bulan_ini = 0.0
            subtotal_penyusutan_bulan_ini = 0.0
            
            domain = [('category_id', '=', asset_category.id),('date','<=',obj.date), ('parent_id', '=', False)]
            # domain = [('category_id', '=', asset_category.id), ('parent_id', '=', False)]
            if obj.asset_state=='running_only':
                domain.append(('state','=','open'))
            elif obj.asset_state=='include_closed':
                domain.append(('state','in',['open','close']))
            
            # tampabhakan pada domain untuk filter asset -> parent = 0/false
            assets = self.env['account.asset.asset'].search(domain, order="date asc")

            for asset in assets:
                sheet.write(row, 0, asset.name, wbf['content'])
                sheet.write(row, 1, asset.code or asset.equipment_code or '', wbf['content'])
                sheet.write(row, 2, asset.category_id.name, wbf['content'])
                sheet.write(row, 3, asset.date, wbf['content_date'])
                sheet.write(row, 4, asset.register_id.name if asset.register_id else '', wbf['content'])
                sheet.write(row, 5, asset.equipment_code if asset.equipment_code else '', wbf['content'])

                # Gross Value
                gross_value = asset.value if obj.date >= asset.date else 0.0
                sheet.write(row, 6, gross_value, wbf['content_float'])
                
                tanggal_as_of = obj.date
                awal_bulan_ini = tanggal_as_of.replace(day=1)

                # Ambil depreciation line dan urutkan
                depreciation_lines = asset.depreciation_line_ids.sorted(key=lambda l: l.depreciation_date)

                # # Akumulasi penyusutan s.d. sebelum bulan ini
                # penyusutan_sebelum_bulan_ini = sum(
                #     line.amount for line in depreciation_lines
                #     if line.depreciation_date < awal_bulan_ini
                # )
                # # Penyusutan bulan ini s.d. tanggal input
                # penyusutan_bulan_ini = sum(
                #     line.amount for line in depreciation_lines
                #     if awal_bulan_ini <= line.depreciation_date <= tanggal_as_of
                # )
                penyusutan_bulan_ini = penyusutan_sebelum_bulan_ini = penyusutan_tahun_lalu = 0.0
                for l in depreciation_lines:
                    if l.depreciation_date.month < tanggal_as_of.month:
                        penyusutan_bulan_ini += l.amount
                    elif l.depreciation_date < awal_bulan_ini and l.depreciation_date.year == tanggal_as_of.year:
                        penyusutan_sebelum_bulan_ini += l.amount
                    else:
                        penyusutan_tahun_lalu += l.amount
                # # Tambahkan saldo awal jika ada
                if asset.beginning_balance:
                    penyusutan_tahun_lalu += asset.accumulated_depreciation or 0.0

                            
                # Akumulasi Penyusutan (sebelum bulan ini)
                sheet.write(row, 7, penyusutan_tahun_lalu if obj.date >= asset.date else 0.0, wbf['content_float'])
                sheet.write(row, 8, penyusutan_sebelum_bulan_ini if obj.date >= asset.date else 0.0, wbf['content_float'])
                # Akumulasi Penyusutan (Bulan ini)
                sheet.write(row, 9, penyusutan_bulan_ini if obj.date >= asset.date else 0.0, wbf['content_float'])

                sisa_umur = sum(1 for line in asset.depreciation_line_ids if not line.move_check)
                accumulated_depreciation = 0.0
                residual_value = 0.0
                # Ambil semua line penyusutannya sesuai dengan tanggal dulu
                depreciation_lines = asset.depreciation_line_ids.sorted(key=lambda l: l.depreciation_date)

                if depreciation_lines:
                    first_depr_date = depreciation_lines[0].depreciation_date

                    if obj.date < first_depr_date:
                        # Bugs yang dibilang pak hndra
                        # accumulated_depreciation = asset.accumulated_depreciation if asset.beginning_balance else 0.0
                        accumulated_depreciation = 0.0

                    else:
                        # Ambil semua line penyusutan yang tanggalnya <= tanggal pada wizard
                        valid_lines = depreciation_lines.filtered(lambda l: l.depreciation_date <= obj.date)
                        penyusutan_lanjutan = sum(valid_lines.mapped('amount'))

                        # Kalau ada beginning balance, tambahkan penyusutannya dengan accumulated_depreciation
                        accumulated_depreciation = penyusutan_lanjutan
                        if asset.beginning_balance:
                            accumulated_depreciation += asset.accumulated_depreciation or 0.0
                else:
                    # kalau Tidak ada penyusutan line, hanya pakai saldo awal jika ada
                    accumulated_depreciation = asset.accumulated_depreciation if asset.beginning_balance else 0.0

                # Hitung residual value menggunakan rumus perhitugan gross value - accumulated depreciation
                residual_value = gross_value - accumulated_depreciation
                ################################################ UBAH ######################################################

                # Accumulated Depreciation
                sheet.write(row, 10, accumulated_depreciation if obj.date >= asset.date else 0.0, wbf['content_float'])
                # Residual Value
                sheet.write(row, 11, residual_value if obj.date >= asset.date else 0.0, wbf['content_float'])

                # Sisa Umur (Bulan)
                sheet.write(row, 12, sisa_umur if obj.date >= asset.date else 0.0, wbf['content_number'])

                if obj.date >= asset.date:
                    subtotal_value += asset.value
                    subtotal_accum_depreciation += accumulated_depreciation
                    subtotal_residual += residual_value
                    subtotal_penyusutan_tahun_lalu += penyusutan_tahun_lalu
                    subtotal_penyusutan_sebelum_bulan_ini += penyusutan_sebelum_bulan_ini
                    subtotal_penyusutan_bulan_ini += penyusutan_bulan_ini

                row += 1
            
            sheet.write(row, 0, f"{asset_category.name}", wbf['header_category'])
            sheet.write(row, 1, '', wbf['header_category'])
            sheet.write(row, 2, '', wbf['header_category'])
            sheet.write(row, 3, '', wbf['header_category'])
            sheet.write(row, 4, '', wbf['header_category'])
            sheet.write(row, 5, '', wbf['header_category'])
            sheet.write(row, 6, subtotal_value, wbf['total_float'])
            sheet.write(row, 7, subtotal_penyusutan_tahun_lalu, wbf['total_float'])
            sheet.write(row, 8, subtotal_penyusutan_sebelum_bulan_ini, wbf['total_float'])
            sheet.write(row, 9, subtotal_penyusutan_bulan_ini, wbf['total_float'])
            sheet.write(row, 10, subtotal_accum_depreciation, wbf['total_float'])
            sheet.write(row, 11, subtotal_residual, wbf['total_float'])
            sheet.write(row, 12, '', wbf['header_category'])
            row += 1 
            
        # Pengaturan Cetak
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.repeat_rows(0)
        sheet.set_print_scale(78)

