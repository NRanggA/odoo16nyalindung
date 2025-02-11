from odoo import models
from pytz import timezone, UTC
class ReportStockMutation(models.AbstractModel):
    _name = 'report.c10i_stock.stock_card_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Stock Card Excel"

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
        
        self.wbf['positive'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_color':'green',
            # 'num_format': '#,##0'
            'num_format': '#,##0.00'
        })
        self.wbf['positive'].set_border()
        
        self.wbf['negative'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_color':'red',
            # 'num_format': '#,##0'
            'num_format': '#,##0.00'
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
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            # 'num_format': '#,##0'
            'num_format': '#,##0.00'
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

    def get_query(self):
        query = """
                SELECT
                    pp.id, 
                    coalesce(opening.qty, 0.0) as opening_qty,
                    coalesce(opening.value, 0.0) as opening_value,
                    coalesce(opening_2.qty, 0.0) as opening_2_qty
                FROM
                    product_product pp
                    LEFT JOIN (
                        SELECT
                            product_id, 
                            sum(qty) as qty,
                            sum(value) as value
                        FROM (
                            (SELECT 
                                sml.product_id, 
                                sml.qty_done as qty,
                                svl.value
                            FROM 
                                stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sml.location_id = lsrc.id 
                            AND svl.stock_move_id = sml.move_id 
                            AND sml.location_dest_id = ldest.id 
                            AND sml.location_dest_id = %(location_id)s
                            AND lsrc.usage != 'internal' 
                            AND ldest.usage = 'internal'
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s
                            AND sml.date < %(date_from)s)
                            UNION ALL
                            (SELECT 
                                sml.product_id, 
                                -sml.qty_done as qty,
                                svl.value
                            FROM 
                                stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sml.location_id = lsrc.id
                            AND sml.location_id = %(location_id)s 
                            AND svl.stock_move_id = sml.move_id 
                            AND sml.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage != 'internal'
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s 
                            AND sml.date < %(date_from)s)
                        ) sub
                        GROUP BY product_id
                    ) opening ON opening.product_id = pp.id
                    LEFT JOIN (
                        SELECT
                            product_id, 
                            sum(qty) as qty
                        FROM (
                            (SELECT 
                                sml.product_id, 
                                sml.qty_done as qty
                            FROM 
                                stock_move_line sml, stock_location lsrc, stock_location ldest
                            WHERE sml.location_id = lsrc.id 
                            AND lsrc.id != %(location_id)s
                            AND ldest.id = %(location_id)s
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage = 'internal'
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s
                            AND sml.date < %(date_from)s)
                            UNION ALL
                            (SELECT 
                                sml.product_id, 
                                -sml.qty_done as qty
                            FROM 
                                stock_move_line sml, stock_location lsrc, stock_location ldest
                            WHERE sml.location_id = lsrc.id
                            AND lsrc.usage = 'internal'
                            AND ldest.usage = 'internal'
                            AND lsrc.id = %(location_id)s
                            AND ldest.id != %(location_id)s
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s 
                            AND sml.date < %(date_from)s)
                        ) sub
                        GROUP BY product_id
                    ) opening_2 ON opening_2.product_id = pp.id
                WHERE pp.id = %(product_id)s
            """
        return query

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        from_date = obj.from_date if obj.from_date else ''
        to_date = obj.to_date if obj.to_date else ''
        location = obj.location_id.name

        products = obj.product_ids if obj.product_ids else self.env['product.product'].search([])
        sheet = workbook.add_worksheet("Stock Card Report")
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 10)
        sheet.set_column('D:D', 10)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 20)

        row = 1
        for product in products:
            query = self.get_query()
            params = {
                'product_id' : product.id,
                'location_id': obj.location_id.id,
                'date_from'  : obj.from_date.strftime('%Y-%m-%d 00:00:00'),
                'date_to'    : obj.to_date.strftime('%Y-%m-%d 23:59:59')
            }
            self.env.cr.execute(query, params)
            mutasi_stock = self.env.cr.dictfetchone()
            
            # Header Produk
            sheet.write(row, 0, 'Product:', wbf['title_doc'])
            sheet.write(row, 1, product.name, wbf['title_sec'])
            row += 1
            sheet.write(row, 0, 'Lokasi:', wbf['title_doc'])
            sheet.write(row, 1, location, wbf['title_sec'])
            row += 1
            sheet.write(row, 0, 'Periode:', wbf['title_doc'])
            sheet.write(row, 1, f'{from_date} s.d {to_date}', wbf['title_sec'])
            row += 2

            # Header Kolom
            sheet.write(row, 0, 'Date', wbf['header'])
            sheet.write(row, 1, 'Transaction', wbf['header'])
            sheet.write(row, 2, 'Penerimaan', wbf['header'])
            sheet.write(row, 3, 'Pengeluaran', wbf['header'])
            sheet.write(row, 4, 'Satuan', wbf['header'])
            sheet.write(row, 5, 'Balance', wbf['header'])
            row += 1

            # Menghitung Saldo Awal
            opening_qty         = mutasi_stock.get('opening_qty') if mutasi_stock else 0.0
            opening_2_qty       = mutasi_stock.get('opening_2_qty') if mutasi_stock else 0.0
            opening = opening_qty + opening_2_qty

            # Tulis Saldo Awal
            sheet.write(row, 1, 'Saldo Awal', wbf['header'])
            sheet.write(row, 5, opening, wbf['total_float'])

            row += 1

            domain = [
                '|',
                ('location_id', '=', obj.location_id.id),
                ('location_dest_id', '=', obj.location_id.id),
                ('product_id', '=', product.id),
                ('date', '>=', obj.from_date),
                ('date', '<=', obj.to_date),
                ('state', '=', 'done')
            ]
            moves = self.env['stock.move.line'].search(domain, order='date asc')

            balance = opening_qty + opening_2_qty
            for move in moves:
                # Konversi waktu dari UTC ke Asia/Jakarta
                utc_time = move.date
                jakarta_tz = timezone('Asia/Jakarta')
                local_time = utc_time.replace(tzinfo=UTC).astimezone(jakarta_tz)
                
                sheet.write(row, 0, local_time.strftime('%d-%m-%Y %H:%M:%S'), wbf['content'])
                transaction_name = move.reference or move.picking_id.name
                sheet.write(row, 1, transaction_name, wbf['content'])
                qty = move.qty_done
                # if move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal':
                #     qty = -qty
                #     sheet.write(row, 2, '', wbf['negative'])
                #     sheet.write(row, 3, qty, wbf['negative'])
                # else:
                #     sheet.write(row, 2, qty, wbf['positive'])
                #     sheet.write(row, 3, '', wbf['positive'])
                if move.location_id.id == obj.location_id.id and move.location_dest_id.id != obj.location_id.id:
                    qty = -qty
                    sheet.write(row, 2, '', wbf['negative'])
                    sheet.write(row, 3, qty, wbf['negative'])
                elif move.location_id.id != obj.location_id.id and move.location_dest_id.id == obj.location_id.id:
                    sheet.write(row, 2, qty, wbf['positive'])
                    sheet.write(row, 3, '', wbf['positive'])
                
                sheet.write(row, 4, move.product_id.uom_id.name, wbf['content'])

                # Update Balance
                balance += qty
                sheet.write(row, 5, balance, wbf['total_float'])

                row += 1

            # Tulis Saldo Akhir
            sheet.merge_range(row, 0, row, 4, 'Saldo Akhir', wbf['header'])
            sheet.write(row, 5, balance, wbf['total_float'])
            row += 3

        # Pengaturan Cetak
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.repeat_rows(0)
        sheet.set_print_scale(78)

