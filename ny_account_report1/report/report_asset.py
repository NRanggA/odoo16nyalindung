from odoo import models
from pytz import timezone, UTC
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

    # def get_query(self):
    #     query = """
    #         SELECT 
    #             l.account_id AS account_id,
    #             COALESCE(SUM(l.debit), 0) AS total_debit,
    #             COALESCE(SUM(l.credit), 0) AS total_credit
    #         FROM 
    #             account_move_line l
    #         WHERE 
    #             l.parent_state = 'posted'
    #             AND l.date < %(date_from)s
    #             AND l.account_id = %(account_id)s
    #         GROUP BY l.account_id;
    #     """
    #     return query

    # def generate_xlsx_report(self, workbook, datas, obj):
    #     workbook = self.add_workbook_format(workbook)
    #     wbf = self.wbf

    #     from_date = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
    #     to_date = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''

    #     sheet = workbook.add_worksheet("Asset Report")
    #     sheet.set_column('A:A', 30)
    #     sheet.set_column('B:B', 25)
    #     sheet.set_column('C:C', 15)
    #     sheet.set_column('D:D', 20)
    #     sheet.set_column('E:E', 25)
    #     sheet.set_column('F:F', 20)
    #     sheet.set_column('G:G', 20)
    #     sheet.set_column('H:H', 20)
    #     sheet.set_column('I:I', 20)

    #     row = 0

    #     # Periode Header
    #     sheet.write(row, 0, 'Periode:', wbf['title_doc'])
    #     sheet.write(row, 1, f'{from_date} s/d {to_date}', wbf['title_sec'])
    #     row += 2

    #     # Header Kolom
    #     headers = [
    #         "Nama", "Asset Category", "Tanggal", "Register Code", "Equipment Code", "Gross Value", 
    #         "Akumulasi Penyusutan", "Residual Value", "Umur Asset"
    #     ]
    #     for col, header in enumerate(headers):
    #         sheet.write(row, col, header, wbf['header'])
    #     row += 1

    #     assets = self.env['account.asset.asset'].search([])
    #     asset_groups = {}
        
    #     for asset in assets:
    #         category = asset.category_id
    #         if category not in asset_groups:
    #             asset_groups[category] = []
    #         asset_groups[category].append(asset)
        
    #     for category, asset_list in asset_groups.items():
    #         for col in range(0, 9):  
    #             value = f"{category.name}" if col == 0 else "" 
    #             sheet.write(row, col, value, wbf['header_category'])
    #         # sheet.write(row, 0, f"Kategori: {category.name}", wbf['header'])
    #         row += 1
            
    #         subtotal_value = 0.0
    #         subtotal_accum_depreciation = 0.0
    #         subtotal_residual = 0.0

    #         for asset in asset_list:
    #             sheet.write(row, 0, asset.name, wbf['content'])
    #             sheet.write(row, 1, asset.category_id.name, wbf['content'])
    #             sheet.write(row, 2, asset.date, wbf['content_date'])
    #             sheet.write(row, 3, asset.register_id.name if asset.register_id else '', wbf['content'])
    #             sheet.write(row, 4, asset.equipment_code if asset.equipment_code else '', wbf['content'])
    #             sheet.write(row, 5, asset.value, wbf['content_float'])
                
    #             accum_depreciation = asset.value - asset.value_residual
    #             sheet.write(row, 6, accum_depreciation, wbf['content_float'])
    #             sheet.write(row, 7, asset.value_residual, wbf['content_float'])
    #             sheet.write(row, 8, '', wbf['content'])
                
    #             subtotal_value += asset.value
    #             subtotal_accum_depreciation += accum_depreciation
    #             subtotal_residual += asset.value_residual

    #             row += 1
            
    #         sheet.write(row, 0, f"{category.name}", wbf['header_category'])
    #         sheet.write(row, 1, '', wbf['header_category'])
    #         sheet.write(row, 2, '', wbf['header_category'])
    #         sheet.write(row, 3, '', wbf['header_category'])
    #         sheet.write(row, 4, '', wbf['header_category'])
    #         sheet.write(row, 5, subtotal_value, wbf['total_float'])
    #         sheet.write(row, 6, subtotal_accum_depreciation, wbf['total_float'])
    #         sheet.write(row, 7, subtotal_residual, wbf['total_float'])
    #         sheet.write(row, 8, '', wbf['header_category'])
    #         row += 1 
        
    #     # Pengaturan Cetak
    #     sheet.set_landscape()
    #     sheet.set_paper(9)
    #     sheet.repeat_rows(0)
    #     sheet.set_print_scale(78)
    
    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        # from_date = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
        # to_date = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''
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
            "Akumulasi Penyusutan", "Residual Value", "Sisa Masa (Bulan)"
        ]
        for col, header in enumerate(headers):
            sheet.write(row, col, header, wbf['header'])
        row += 1

        # assets_categories = obj.asset_category_ids if obj.asset_category_ids else self.env['account.asset.category'].search([('account_asset_id.account_type','=','asset_fixed')])
        assets_categories = obj.asset_category_ids if obj.asset_category_ids else self.env['account.asset.category'].search([])
        for asset_category in assets_categories:
            for col in range(0, 10):  
                value = f"{asset_category.name}" if col == 0 else "" 
                sheet.write(row, col, value, wbf['header_category'])
            row += 1
            
            subtotal_value = 0.0
            subtotal_accum_depreciation = 0.0
            subtotal_residual = 0.0
            
            domain = [('category_id', '=', asset_category.id),('date','<=',obj.date)]
            if obj.asset_state=='running_only':
                domain.append(('state','=','open'))
            elif obj.asset_state=='include_closed':
                domain.append(('state','in',['open','close']))
            assets = self.env['account.asset.asset'].search(domain)

            for asset in assets:
                sheet.write(row, 0, asset.name, wbf['content'])
                sheet.write(row, 1, asset.code or asset.equipment_code or '', wbf['content'])
                sheet.write(row, 2, asset.category_id.name, wbf['content'])
                sheet.write(row, 3, asset.date, wbf['content_date'])
                sheet.write(row, 4, asset.register_id.name if asset.register_id else '', wbf['content'])
                sheet.write(row, 5, asset.equipment_code if asset.equipment_code else '', wbf['content'])
                # Gross Value
                sheet.write(row, 6, asset.value, wbf['content_float'])
                
                sisa_umur = sum(1 for line in asset.depreciation_line_ids if not line.move_check)

                accumulated_depreciation = residual_value = 0.0
                if not asset.depreciation_line_ids:
                    accumulated_depreciation = asset.accumulated_depreciation if asset.beginning_balance else 0.0
                    residual_value = asset.value_residual
                else:
                    for line in asset.depreciation_line_ids:
                        if line.depreciation_date.month == obj.date.month and line.depreciation_date.year == obj.date.year:
                            accumulated_depreciation += line.depreciated_value
                            residual_value += line.remaining_value
                
                # Accumulated Depreciation
                sheet.write(row, 7, accumulated_depreciation, wbf['content_float'])
                # Residual Value
                sheet.write(row, 8, residual_value, wbf['content_float'])
                
                # Sisa Umur (Bulan)
                sheet.write(row, 9, sisa_umur, wbf['content_number'])
                
                subtotal_value += asset.value
                subtotal_accum_depreciation += accumulated_depreciation
                subtotal_residual += residual_value

                row += 1
            
            sheet.write(row, 0, f"{asset_category.name}", wbf['header_category'])
            sheet.write(row, 1, '', wbf['header_category'])
            sheet.write(row, 2, '', wbf['header_category'])
            sheet.write(row, 3, '', wbf['header_category'])
            sheet.write(row, 4, '', wbf['header_category'])
            sheet.write(row, 5, '', wbf['header_category'])
            sheet.write(row, 6, subtotal_value, wbf['total_float'])
            sheet.write(row, 7, subtotal_accum_depreciation, wbf['total_float'])
            sheet.write(row, 8, subtotal_residual, wbf['total_float'])
            sheet.write(row, 9, '', wbf['header_category'])
            row += 1 
            
        # Pengaturan Cetak
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.repeat_rows(0)
        sheet.set_print_scale(78)

