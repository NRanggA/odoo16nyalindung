from odoo import models
from datetime import datetime, timedelta

class ReportDetailReceipt(models.AbstractModel):
    _name = 'report.c10i_stock.detail_receipt_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Detail Receipt Excel"

    wbf = {}

    def add_workbook_format(self, workbook):
        # Header format untuk judul utama (misalnya, judul laporan)
        self.wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 14,
            'font_color': '#000000',
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

    # def generate_xlsx_report(self, workbook, datas, obj):
    #     workbook = self.add_workbook_format(workbook)
    #     wbf = self.wbf

    #     from_date = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
    #     to_date = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''
    #     picking_type_id = obj.picking_type_id

    #     if not picking_type_id:
    #         picking_type_id = self.env['stock.picking.type'].search([])
        
    #     sheet  = workbook.add_worksheet("Laporan Detail Receipt")

    #     row = 0

    #     for picking_type in picking_type_id:
    #         # Judul Laporan
    #         sheet.write(row, 0, 'Laporan Detail Receipt')
    #         row += 1
    #         sheet.write(row, 0,'BULAN')
    #         sheet.write(row, 1,':', wbf['content_center'])
    #         sheet.write(row, 2,f'{from_date.strftime("%d-%m-%Y")} s/d {to_date.strftime("%d-%m-%Y")}' if from_date and to_date else '')

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        from_date = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
        to_date = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''
        picking_type_id = obj.picking_type_id.name

        # Nama worksheet
        sheet = workbook.add_worksheet(f"{picking_type_id}")

        # Lebar kolom
        sheet.set_column('A:A', 6)  
        sheet.set_column('B:B', 20)  
        sheet.set_column('C:C', 20)  
        sheet.set_column('D:D', 20)  
        sheet.set_column('E:E', 20)  
        sheet.set_column('F:F', 30)  
        sheet.set_column('G:G', 20)  
        sheet.set_column('H:H', 20)  
        sheet.set_column('I:I', 20)  
        sheet.set_column('J:J', 20)  
        sheet.set_column('K:K', 40)  
        sheet.set_column('L:L', 20)  
        sheet.set_column('M:M', 20)  
        sheet.set_column('N:N', 20)  
        sheet.set_column('O:O', 40)  
        sheet.set_column('P:P', 40)  
        sheet.set_column('Q:Q', 40)  
        sheet.set_column('R:R', 20)  

        # Judul Laporan
        sheet.write('A2', 'Detail ' + picking_type_id, wbf['title_doc'])
        sheet.write('A3', f'{from_date} s/d {to_date}', wbf['title_doc'])

        # Header Produk
        sheet.write('A5', 'No.', wbf['header'])
        sheet.write('B5', 'Tanggal', wbf['header'])
        sheet.write('C5', 'No. Issue', wbf['header'])
        sheet.write('D5', 'No. MR', wbf['header'])
        sheet.write('E5', 'Product Code', wbf['header'])
        sheet.write('F5', 'Product Name', wbf['header'])
        sheet.write('G5', 'Qty', wbf['header'])
        sheet.write('H5', 'UOM', wbf['header'])
        
        if obj.with_accounting_journal:
            sheet.write('I5', 'Value', wbf['header'])
            sheet.write('J5', 'Journal Entry', wbf['header'])
            sheet.write('K5', 'Account', wbf['header'])
            sheet.write('L5', 'Value on Journal', wbf['header'])
            sheet.write('M5', 'Tipe Lokasi', wbf['header'])
            sheet.write('N5', 'ORG', wbf['header'])
            sheet.write('O5', 'Lokasi', wbf['header'])
            sheet.write('P5', 'Aktivitas', wbf['header'])
            sheet.write('Q5', 'Account', wbf['header'])
            sheet.write('R5', 'Value on Journal', wbf['header'])

        row = 5

        domain = [
            ('picking_type_id', '=', obj.picking_type_id.id),
            ('date', '>=', obj.from_date),
            ('date', '<=', obj.to_date),
            ('state', '=', 'done'),
        ]
        moves = self.env['stock.move'].search(domain, order='date asc')

        row_number = 1
        for stock in moves:
            first_journal_row = row  

            sheet.write(row, 0, row_number, wbf['content'])  
            sheet.write(row, 1, stock.date.strftime('%d-%m-%Y %H:%M:%S'), wbf['content'])  
            sheet.write(row, 2, stock.reference, wbf['content'])  
            sheet.write(row, 3, stock.mr_line_id.mr_id.name if stock.mr_line_id.mr_id else '-', wbf['content'])  
            sheet.write(row, 4, stock.product_id.default_code if stock.product_id.default_code else '-', wbf['content'])  
            sheet.write(row, 5, stock.product_id.name, wbf['content']) 
            sheet.write(row, 6, stock.product_uom_qty, wbf['content_float'])  
            sheet.write(row, 7, stock.product_id.uom_id.name, wbf['content']) 

            if obj.with_accounting_journal:
                for svl in stock.stock_valuation_layer_ids:
                    sheet.write(row, 8, svl.value, wbf['content_float'])

                if stock.account_move_ids:
                    for acc_move in stock.account_move_ids:  
                        sheet.write(row, 9, acc_move.name, wbf['content']) 
                        
                        for acc_move_line in acc_move.line_ids:
                            if stock.product_id.categ_id.property_stock_valuation_account_id.id != acc_move_line.account_id.id:
                                sheet.write(row, 10, f"{acc_move_line.account_id.code} - {acc_move_line.account_id.name}", wbf['content'])  
                                sheet.write(row, 11, acc_move_line.balance, wbf['content_float'])  
                                # row += 1 
                            else:
                                sheet.write(row, 12, acc_move_line.plantation_location_type_id.name if acc_move_line.plantation_location_type_id else '-', wbf['content'])
                                sheet.write(row, 13, acc_move_line.plantation_varieties_id.name if acc_move_line.plantation_varieties_id else '-', wbf['content'])
                                sheet.write(row, 14, acc_move_line.plantation_location_id.name if acc_move_line.plantation_location_id else '-', wbf['content'])
                                sheet.write(row, 15, f"{acc_move_line.plantation_activity_id.code} - {acc_move_line.plantation_activity_id.name}" if acc_move_line.plantation_activity_id else '-', wbf['content'])
                                sheet.write(row, 16, f"{acc_move_line.account_id.code} - {acc_move_line.account_id.name}", wbf['content'])
                                sheet.write(row, 17, acc_move_line.balance, wbf['content_float'])
                            
                                # row += 1 
                else:
                    sheet.write(row, 9, '-', wbf['content']) 
                    sheet.write(row, 10, '-', wbf['content'])  
                    sheet.write(row, 11, '-', wbf['content'])  
                    sheet.write(row, 12, '-', wbf['content'])  
                    sheet.write(row, 13, '-', wbf['content'])  
                    sheet.write(row, 14, '-', wbf['content'])  
                    sheet.write(row, 15, '-', wbf['content'])  
                    sheet.write(row, 16, '-', wbf['content'])  
                    sheet.write(row, 17, '-', wbf['content'])  

                
                if row == first_journal_row:  
                    row += 1  
            else:
                row += 1 

            row_number += 1 

        # Page Layout
        sheet.set_landscape()
        sheet.set_paper(9)  
        sheet.repeat_rows(1, 4)
        sheet.print_area(0, 0, row, 13)
        sheet.set_print_scale(78)
