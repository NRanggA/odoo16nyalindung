from odoo import models

class ReportSeedkMutation(models.AbstractModel):
    _name = 'report.c10i_plantation_seed.seed_mutation_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Seed Mutasi Excel"

    wbf = {}

    def add_workbook_format(self, workbook):
        # Header format untuk judul utama (misalnya, judul laporan)
        self.wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
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

        return workbook


    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf
   

        from_date   = obj.date_start.strftime('%d-%m-%Y') if obj.date_start else ''
        to_date     = obj.date_end.strftime('%d-%m-%Y') if obj.date_end else ''
        
        # Nama worksheet
        sheet = workbook.add_worksheet('Seed Mutation')

        # lebar kolom
        sheet.set_column('A:A', 10)  
        sheet.set_column('B:B', 30)  
        sheet.set_column('C:C', 10)  
        sheet.set_column('D:H', 15) 

        # Judul Laporan
        sheet.merge_range('D2:H2', 'SEED MUTATION', wbf['title_doc'])
        sheet.merge_range('D3:H3', f'{from_date} s/d {to_date}', wbf['title_doc'])

        # Header Produk
        sheet.merge_range('A4:A5', 'Kode Transaksi', wbf['header'])
        sheet.merge_range('B4:B5', 'Nama Product', wbf['header'])
        sheet.merge_range('C4:C5', 'Satuan', wbf['header'])
        sheet.merge_range('D4:E4', 'Saldo Awal', wbf['header'])
        sheet.merge_range('F4:G4', 'Penerimaan', wbf['header'])
        sheet.merge_range('H4:I4', 'Pengeluaran', wbf['header'])
        sheet.merge_range('J4:K4', 'Adjustment', wbf['header'])
        sheet.merge_range('L4:M4', 'Saldo Akhir', wbf['header'])

        sheet.merge_range('D5:E5', 'Qty', wbf['header'])
        sheet.merge_range('F5:G5', 'Qty', wbf['header'])
        sheet.merge_range('H5:I5', 'Qty', wbf['header'])
        sheet.merge_range('J5:K5', 'Qty', wbf['header'])
        sheet.merge_range('L5:M5', 'Qty', wbf['header'])


        transactions = self.env['seed.move.line'].search([('product_id', '=', obj.product_id.id)])


        row = 5  
        for transaction in transactions:
            sheet.write(row, 0, transaction.seed_move_id.name, wbf['content']) 
            sheet.write(row, 1, transaction.product_id.name, wbf['content']) 
            sheet.write(row, 2, transaction.product_id.uom_id.name, wbf['content']) 

            query = """
                    SELECT sml.id, 
                        sml.product_id, 
                        sml.qty, 
                        sml.nursery_id, 
                        sml.location_src_id, 
                        sml.location_dest_id, 
                        sml.date
                    FROM seed_move_line AS sml
                    JOIN seed_move AS sm 
                    ON sml.seed_move_id = sm.id
                    WHERE sml.nursery_id = %(location_id)s
                    AND sml.product_id = %(product_id)s
                    AND sm.date BETWEEN %(date_start)s AND %(date_end)s;
                """
            params = {
                'product_id'    : transaction.product_id.id,
                'location_id'   : obj.location_id.id,
                'date_start'    : obj.date_start.strftime('%Y-%m-%d 00:00:00'),
                'date_end'      : obj.date_end.strftime('%Y-%m-%d 23:59:59')
            }
            self.env.cr.execute(query, params)
            mutasi_stock = self.env.cr.dictfetchone()

            print(f"====== {mutasi_stock}")
            # print(f"====== {t}")
        
            
            
            # opening_qty = mutasi_stock.get('opening_qty') if mutasi_stock else 0.0
            # sheet.merge_range(row, 3, row, 4, opening_qty, wbf['content_float'])

            # incoming_qty = mutasi_stock.get('incoming_qty') if mutasi_stock else 0.0
            # sheet.merge_range(row, 5, row, 6, incoming_qty, wbf['content_float'])

            # outgoing_qty = mutasi_stock.get('outgoing_qty') if mutasi_stock else 0.0
            # sheet.merge_range(row, 7, row, 8, outgoing_qty, wbf['content_float'])

            # adjustment_qty = mutasi_stock.get('adjustment_qty') if mutasi_stock else 0.0
            # sheet.merge_range(row, 9, row, 10, adjustment_qty, wbf['content_float'])

            # closing_qty = opening_qty + incoming_qty - outgoing_qty + adjustment_qty
            # sheet.merge_range(row, 11, row, 12, closing_qty, wbf['content_float'])

            row += 1
        
        
        # Page Layout
        sheet.set_landscape()
        sheet.set_paper(9) # A4
        # sheet.set_header()
        sheet.repeat_rows(1, 4)
        # sheet.print_area(0, 0, row, 13)
        sheet.set_print_scale(78)

