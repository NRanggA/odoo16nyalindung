from odoo import models

class ReportStockMutation(models.AbstractModel):
    _name = 'report.c10i_stock.stock_mutation_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Stock Mutasi Excel"

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
            # 'bg_color': '#FFFFDB',
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['header'].set_text_wrap()  # Membuat teks menjadi wrap agar bisa masuk dalam sel
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

        from_date   = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
        to_date     = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''

        if obj.product_ids:
            products = obj.product_ids
        else:
            products = self.env['product.product'].search([])
        

        # print(f"===== {products}")


        # Nama worksheet
        sheet = workbook.add_worksheet('Stock Mutation')

        # lebar kolom
        sheet.set_column('A:A', 10)  # Kode
        sheet.set_column('B:B', 30)  # Nama Product
        sheet.set_column('C:C', 10)  # Satuan
        sheet.set_column('D:H', 15)  # Saldo Awal, Penerimaan, Pengeluaran, Adjustment, Saldo Akhir

        # Judul Laporan
        sheet.merge_range('D2:H2', 'INVENTORY MUTATION', wbf['title_doc'])
        sheet.merge_range('D3:H3', f'{from_date} s/d {to_date}', wbf['title_doc'])

        # Header Produk
        sheet.merge_range('A4:A5', 'Kode', wbf['header'])
        sheet.merge_range('B4:B5', 'Nama Product', wbf['header'])
        sheet.merge_range('C4:C5', 'Satuan', wbf['header'])
        sheet.merge_range('D4:E4', 'Saldo Awal', wbf['header'])
        sheet.merge_range('F4:G4', 'Penerimaan', wbf['header'])
        sheet.merge_range('H4:I4', 'Pengeluaran', wbf['header'])
        sheet.merge_range('J4:K4', 'Adjustment', wbf['header'])
        sheet.merge_range('L4:M4', 'Saldo Akhir', wbf['header'])

        sheet.merge_range('D5:E5', 'Qty', wbf['header'])
        # sheet.write('E5', '', wbf['header'])
        sheet.merge_range('F5:G5', 'Qty', wbf['header'])
        # sheet.write('G5', '', wbf['header'])
        sheet.merge_range('H5:I5', 'Qty', wbf['header'])
        # sheet.write('I5', '', wbf['header'])
        sheet.merge_range('J5:K5', 'Qty', wbf['header'])
        # sheet.write('K5', '', wbf['header'])
        sheet.merge_range('L5:M5', 'Qty', wbf['header'])
        # sheet.write('M5', '', wbf['header'])




        row = 5  
        for product in products:
            sheet.write(row, 0, product['default_code'], wbf['content'])  # Kode
            sheet.write(row, 1, product['name'], wbf['content'])  # Nama Produk
            # sheet.write(row, 2, product['uom'], wbf['content'])  # Satuan
            sheet.write(row, 2, product['uom_id'].name, wbf['content'])  # Satuan
            
            # print(f"==== {product['default_code']}")
            # print(f"==== {product['name']}")
            # print(f"==== {product['uom_id'].id}")

            query = """
                SELECT
                    pp.id, 
                    coalesce(opening.qty, 0.0) as opening_qty,
                    coalesce(incoming.qty, 0.0) as incoming_qty,
                    coalesce(outgoing.qty, 0.0) as outgoing_qty,
                    coalesce(adjustment.qty, 0.0) as adjustment_qty
                FROM
                    product_product pp
                    LEFT JOIN (
                        SELECT
                            product_id, sum(qty) as qty 
                        FROM (
                            (SELECT 
                                sm.product_id, sm.product_uom_qty as qty 
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id 
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage != 'internal' 
                            AND ldest.usage = 'internal'
                            AND sm.state = 'done' 
                            AND sm.date < %(date_from)s)
                            UNION ALL
                            (SELECT 
                                sm.product_id, -sm.product_uom_qty as qty 
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id 
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage != 'internal'
                            AND sm.state = 'done' 
                            AND sm.date < %(date_from)s)
                        ) sub
                        GROUP BY product_id
                    ) opening ON opening.product_id = pp.id
                    LEFT JOIN (
                        SELECT product_id, sum(qty) as qty 
                        FROM (
                            SELECT 
                                sm.product_id, sm.product_uom_qty as qty 
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id 
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage IN ('supplier', 'customer') 
                            AND ldest.usage = 'internal' 
                            AND sm.state = 'done' 
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s
                        ) sub
                        GROUP BY product_id
                    ) incoming ON incoming.product_id = pp.id
                    LEFT JOIN (
                        SELECT product_id, sum(qty) as qty 
                        FROM (
                            SELECT 
                                sm.product_id, sm.product_uom_qty as qty 
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id 
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage IN ('supplier', 'customer') 
                            AND sm.state = 'done' 
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s
                        ) sub
                        GROUP BY product_id
                    ) outgoing ON outgoing.product_id = pp.id
                    LEFT JOIN (
                        SELECT product_id, sum(qty) as qty 
                        FROM (
                            (SELECT 
                                sm.product_id, sm.product_uom_qty as qty 
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id 
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage = 'inventory' 
                            AND ldest.usage = 'internal' 
                            AND sm.state = 'done' 
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s)
                            UNION ALL
                            (SELECT 
                                sm.product_id, -sm.product_uom_qty as qty 
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id 
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage = 'inventory' 
                            AND sm.state = 'done' 
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s)
                        ) sub
                        GROUP BY product_id
                    ) adjustment ON adjustment.product_id = pp.id
                WHERE pp.id = %(product_id)s
            """
            params = {
                'product_id': product.id,
                'date_from' : obj.from_date.strftime('%Y-%m-%d 00:00:00'),
                'date_to'   : obj.to_date.strftime('%Y-%m-%d 23:59:59')
            }
            self.env.cr.execute(query, params)
            mutasi_stock = self.env.cr.dictfetchone()

            print(f">>>>>>> {mutasi_stock}")
            
            # sheet.write(row, 3, product['opening_qty'], wbf['content_float'])  # Saldo Awal
            # sheet.write(row, 4, '', wbf['content_float'])  # Saldo Awal Kosong (Bisa dihilangkan jika tidak dipakai)
            # sheet.write(row, 5, product['received_qty'], wbf['content_float'])  # Penerimaan
            # sheet.write(row, 6, '', wbf['content_float'])  # Penerimaan Kosong
            # sheet.write(row, 7, product['used_qty'], wbf['content_float'])  # Pengeluaran
            # sheet.write(row, 8, '', wbf['content_float'])  # Pengeluaran Kosong
            # sheet.write(row, 9, product['adjust_qty'], wbf['content_float'])  # Adjustment
            # sheet.write(row, 10, '', wbf['content_float'])  # Adjustment Kosong
            # sheet.write(row, 11, product['closing_qty'], wbf['content_float'])  # Saldo Akhir
            # sheet.write(row, 12, '', wbf['content_float'])  # Saldo Akhir Kosong

            # Menggabungkan kolom 3 dan 4 untuk Saldo Awal
            opening_qty = mutasi_stock.get('opening_qty') if mutasi_stock else 0.0
            sheet.merge_range(row, 3, row, 4, opening_qty, wbf['content_float'])

            # Menggabungkan kolom 5 dan 6 untuk Penerimaan
            incoming_qty = mutasi_stock.get('incoming_qty') if mutasi_stock else 0.0
            sheet.merge_range(row, 5, row, 6, incoming_qty, wbf['content_float'])

            # Menggabungkan kolom 7 dan 8 untuk Pengeluaran
            outgoing_qty = mutasi_stock.get('outgoing_qty') if mutasi_stock else 0.0
            sheet.merge_range(row, 7, row, 8, outgoing_qty, wbf['content_float'])

            # Menggabungkan kolom 9 dan 10 untuk Adjustment
            adjustment_qty = mutasi_stock.get('adjustment_qty') if mutasi_stock else 0.0
            sheet.merge_range(row, 9, row, 10, adjustment_qty, wbf['content_float'])

            # Menggabungkan kolom 11 dan 12 untuk Saldo Akhir
            closing_qty = opening_qty + incoming_qty - outgoing_qty + adjustment_qty
            sheet.merge_range(row, 11, row, 12, closing_qty, wbf['content_float'])



            row += 1

