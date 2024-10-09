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
        sheet.merge_range('D2:H2', 'Mutasi bibitan', wbf['title_doc'])
        sheet.merge_range('D3:H3', f'{from_date} s/d {to_date}', wbf['title_doc'])
        sheet.merge_range('D4:H4', obj.location_id.name, wbf['title_doc'])

        # Header Produk
        sheet.merge_range('A5:A6', 'Kode Transaksi', wbf['header'])
        sheet.merge_range('B5:B6', 'Nama Product', wbf['header'])
        sheet.merge_range('C5:C6', 'Satuan', wbf['header'])
        sheet.merge_range('D5:E5', 'Saldo Awal', wbf['header'])
        sheet.merge_range('F5:G5', 'Penerimaan', wbf['header'])
        sheet.merge_range('H5:I5', 'Pengeluaran', wbf['header'])
        sheet.merge_range('J5:K5', 'Adjustment', wbf['header'])
        sheet.merge_range('L5:M5', 'Saldo Akhir', wbf['header'])

        sheet.merge_range('D6:E6', 'Qty', wbf['header'])
        sheet.merge_range('F6:G6', 'Qty', wbf['header'])
        sheet.merge_range('H6:I6', 'Qty', wbf['header'])
        sheet.merge_range('J6:K6', 'Qty', wbf['header'])
        sheet.merge_range('L6:M6', 'Qty', wbf['header'])

        SeedMoveLine = self.env['seed.move.line']
        
        # Opening
        all_in_moves 	= SeedMoveLine.search([
                            ('nursery_id', '=', obj.location_id.id),
                            ('location_dest_id', '=', obj.location_id.location_id.id),
                            ('mutation_type_id.type', 'in', ['incoming', 'adj_in', 'transfer']),
                            ('date', '<', obj.date_start)
                        ])
        all_out_moves   = SeedMoveLine.search([('nursery_id','=',obj.location_id.id),
                            ('location_src_id','=',obj.location_id.location_id.id),
                            ('mutation_type_id.type','in',['outgoing','adj_out','transfer']),
                            ('date', '<', obj.date_start)
                        ])
        
        # Incoming
        in_moves = SeedMoveLine.search([
            ('nursery_id', '=', obj.location_id.id),
            ('location_dest_id', '=', obj.location_id.location_id.id),
            ('mutation_type_id.type', 'in', ['incoming', 'transfer']),
            ('date', '>=', obj.date_start),
            ('date', '<=', obj.date_end),
        ])

        # Outgoing
        out_moves = SeedMoveLine.search([
            ('nursery_id', '=', obj.location_id.id),
            ('location_src_id', '=', obj.location_id.location_id.id),
            ('mutation_type_id.type', 'in', ['outgoing', 'transfer']),
            ('date', '>=', obj.date_start),
            ('date', '<=', obj.date_end),
        ])

        # Adjustment
        adj_in_moves = SeedMoveLine.search([
            ('nursery_id', '=', obj.location_id.id),
            ('location_dest_id', '=', obj.location_id.location_id.id),
            ('mutation_type_id.type', '=', 'adj_in'),
            ('date', '>=', obj.date_start),
            ('date', '<=', obj.date_end),
        ])
        
        adj_out_moves = SeedMoveLine.search([
            ('nursery_id', '=', obj.location_id.id),
            ('location_src_id', '=', obj.location_id.location_id.id),
            ('mutation_type_id.type', '=', 'adj_out'),
            ('date', '>=', obj.date_start),
            ('date', '<=', obj.date_end),
        ])
        
        # Gabung semua produk
        product_ids = set(in_moves.mapped('product_id.id')).union(
            set(out_moves.mapped('product_id.id')),
            set(adj_in_moves.mapped('product_id.id')),
            set(adj_out_moves.mapped('product_id.id')),
            set(all_in_moves.mapped('product_id.id')),
            set(all_out_moves.mapped('product_id.id'))
        )
        
        row = 6

        for product_id in product_ids:
            product = self.env['product.product'].browse(product_id)

            # Hitung penerimaan
            incoming_qty        = sum(in_moves.filtered(lambda m: m.product_id.id == product_id).mapped('qty')) or 0.0

            # Hitung pengeluaran 
            outgoing_qty        = sum(out_moves.filtered(lambda m: m.product_id.id == product_id).mapped('qty')) or 0.0

            # Hitung penyesuaian
            adjustment_in_qty   = sum(adj_in_moves.filtered(lambda m: m.product_id.id == product_id).mapped('qty')) or 0.0
            adjustment_out_qty  = sum(adj_out_moves.filtered(lambda m: m.product_id.id == product_id).mapped('qty')) or 0.0
            adjustment_qty      = adjustment_in_qty - adjustment_out_qty

            # Hitung saldo awal 
            opening_qty         = sum(all_in_moves.filtered(lambda m: m.product_id.id == product_id).mapped('qty')) - \
                                sum(all_out_moves.filtered(lambda m: m.product_id.id == product_id).mapped('qty')) or 0.0

            # Hitung saldo akhir 
            closing_qty         = opening_qty + incoming_qty - outgoing_qty + adjustment_qty

            
            sheet.write(row, 0, '-', wbf['content'])  
            sheet.write(row, 1, product.name, wbf['content']) 
            sheet.write(row, 2, product.uom_id.name, wbf['content']) 
            sheet.merge_range(row, 3, row, 4, opening_qty, wbf['content_float'])
            sheet.merge_range(row, 5, row, 6, incoming_qty, wbf['content_float'])
            sheet.merge_range(row, 7, row, 8, outgoing_qty, wbf['content_float'])
            sheet.merge_range(row, 9, row, 10, adjustment_qty, wbf['content_float'])
            sheet.merge_range(row, 11, row, 12, closing_qty, wbf['content_float'])


            row += 1  # Pindah ke baris berikutnya

        # Page Layout
        sheet.set_landscape()
        sheet.set_paper(9)  # A4
        sheet.repeat_rows(1, 4)

