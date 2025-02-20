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


    def get_query_old(self):
        query = """
                SELECT
                    pp.id, 
                    coalesce(opening.qty, 0.0) as opening_qty,
                    coalesce(opening.value, 0.0) as opening_value,
                    coalesce(incoming.qty, 0.0) as incoming_qty,
                    coalesce(incoming.value, 0.0) as incoming_value,
                    coalesce(outgoing.qty, 0.0) as outgoing_qty,
                    coalesce(outgoing.value, 0.0) as outgoing_value,
                    coalesce(adjustment.qty, 0.0) as adjustment_qty,
                    coalesce(adjustment.value, 0.0) as adjustment_value,
                    coalesce(incoming_2.qty, 0.0) as incoming_2_qty,
                    coalesce(outgoing_2.qty, 0.0) as outgoing_2_qty,
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
                                sm.product_id, 
                                sm.product_uom_qty as qty,
                                svl.value
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sm.location_id = lsrc.id 
                            AND svl.stock_move_id = sm.id 
                            AND sm.location_dest_id = ldest.id 
                            AND sm.location_dest_id = %(location_id)s
                            AND lsrc.usage != 'internal' 
                            AND ldest.usage = 'internal'
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s
                            AND sm.date < %(date_from)s)
                            UNION ALL
                            (SELECT 
                                sm.product_id, 
                                -sm.product_uom_qty as qty,
                                svl.value
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sm.location_id = lsrc.id
                            AND sm.location_id = %(location_id)s 
                            AND svl.stock_move_id = sm.id 
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage != 'internal'
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s 
                            AND sm.date < %(date_from)s)
                        ) sub
                        GROUP BY product_id
                    ) opening ON opening.product_id = pp.id
                    LEFT JOIN (
                        SELECT
                            product_id, 
                            sum(qty) as qty
                        FROM (
                            (SELECT 
                                sm.product_id, 
                                sm.product_uom_qty as qty
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id 
                            AND lsrc.id != %(location_id)s
                            AND ldest.id = %(location_id)s
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage = 'internal'
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s
                            AND sm.date < %(date_from)s)
                            UNION ALL
                            (SELECT 
                                sm.product_id, 
                                -sm.product_uom_qty as qty
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest
                            WHERE sm.location_id = lsrc.id
                            AND lsrc.usage = 'internal'
                            AND ldest.usage = 'internal'
                            AND lsrc.id = %(location_id)s
                            AND ldest.id != %(location_id)s
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s 
                            AND sm.date < %(date_from)s)
                        ) sub
                        GROUP BY product_id
                    ) opening_2 ON opening_2.product_id = pp.id
                    LEFT JOIN (
                        SELECT 
                            product_id, 
                            sum(qty) as qty,
                            sum(value) as value
                        FROM (
                            SELECT 
                                sm.product_id, 
                                sm.product_uom_qty as qty,
                                svl.value
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sm.location_id = lsrc.id 
                            AND svl.stock_move_id = sm.id 
                            AND sm.location_dest_id = ldest.id
                            AND sm.location_dest_id = %(location_id)s 
                            AND lsrc.usage IN ('supplier', 'customer','production') 
                            AND ldest.usage = 'internal' 
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s 
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s
                        ) sub
                        GROUP BY product_id
                    ) incoming ON incoming.product_id = pp.id
                    LEFT JOIN (
                        SELECT
                            sm.product_id,
                            sum(sm.product_uom_qty) as qty
                        FROM 
                            stock_move sm
                            JOIN stock_location lsrc ON sm.location_id = lsrc.id
                            JOIN stock_location ldest ON sm.location_dest_id = ldest.id
                        WHERE 
                            lsrc.usage = 'internal'
                            AND ldest.usage = 'internal'
                            AND lsrc.id != %(location_id)s
                            AND ldest.id = %(location_id)s
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s
                        GROUP BY sm.product_id
                    ) incoming_2 ON incoming_2.product_id = pp.id
                    LEFT JOIN (
                        SELECT 
                            product_id, 
                            sum(qty) as qty,
                            sum(value * -1) as value
                        FROM (
                            SELECT 
                                sm.product_id, 
                                sm.product_uom_qty as qty,
                                svl.value
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sm.location_id = lsrc.id
                            AND sm.location_id = %(location_id)s 
                            AND svl.stock_move_id = sm.id
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage IN ('supplier', 'customer','production') 
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s  
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s
                        ) sub
                        GROUP BY product_id
                    ) outgoing ON outgoing.product_id = pp.id
                    LEFT JOIN (
                        SELECT
                            sm.product_id,
                            sum(sm.product_uom_qty) as qty
                        FROM 
                            stock_move sm
                            JOIN stock_location lsrc ON sm.location_id = lsrc.id
                            JOIN stock_location ldest ON sm.location_dest_id = ldest.id
                        WHERE 
                            lsrc.usage = 'internal'
                            AND ldest.usage = 'internal'
                            AND lsrc.id = %(location_id)s
                            AND ldest.id != %(location_id)s
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s
                        GROUP BY sm.product_id
                    ) outgoing_2 ON outgoing_2.product_id = pp.id
                    LEFT JOIN (
                        SELECT 
                            product_id, 
                            sum(qty) as qty,
                            sum(value) as value 
                        FROM (
                            (SELECT 
                                sm.product_id, 
                                sm.product_uom_qty as qty,
                                svl.value 
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sm.location_id = lsrc.id
                            AND svl.stock_move_id = sm.id 
                            AND sm.location_dest_id = ldest.id
                            AND sm.location_dest_id = %(location_id)s  
                            AND lsrc.usage = 'inventory' 
                            AND ldest.usage = 'internal' 
                            AND sm.state = 'done'
                            AND sm.product_id = %(product_id)s  
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s)
                            UNION ALL
                            (SELECT 
                                sm.product_id, 
                                -sm.product_uom_qty as qty,
                                svl.value
                            FROM 
                                stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sm.location_id = lsrc.id
                            AND sm.location_id = %(location_id)s 
                            AND svl.stock_move_id = sm.id
                            AND sm.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage = 'inventory' 
                            AND sm.state = 'done' 
                            AND sm.product_id = %(product_id)s 
                            AND sm.date BETWEEN %(date_from)s AND %(date_to)s)
                        ) sub
                        GROUP BY product_id
                    ) adjustment ON adjustment.product_id = pp.id
                WHERE pp.id = %(product_id)s
            """
        return query

    def get_query(self):
        query = """
                SELECT
                    pp.id, 
                    coalesce(opening.qty, 0.0) as opening_qty,
                    coalesce(opening.value, 0.0) as opening_value,
                    coalesce(incoming.qty, 0.0) as incoming_qty,
                    coalesce(incoming.value, 0.0) as incoming_value,
                    coalesce(outgoing.qty, 0.0) as outgoing_qty,
                    coalesce(outgoing.value, 0.0) as outgoing_value,
                    coalesce(adjustment.qty, 0.0) as adjustment_qty,
                    coalesce(adjustment.value, 0.0) as adjustment_value,
                    coalesce(incoming_2.qty, 0.0) as incoming_2_qty,
                    coalesce(outgoing_2.qty, 0.0) as outgoing_2_qty,
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
                    LEFT JOIN (
                        SELECT 
                            product_id, 
                            sum(qty) as qty,
                            sum(value) as value
                        FROM (
                            SELECT 
                                sml.product_id, 
                                sml.qty_done as qty,
                                svl.value
                            FROM 
                                stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sml.location_id = lsrc.id 
                            AND svl.stock_move_id = sml.move_id 
                            AND sml.location_dest_id = ldest.id
                            AND sml.location_dest_id = %(location_id)s 
                            AND lsrc.usage IN ('supplier', 'customer','production') 
                            AND ldest.usage = 'internal' 
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s 
                            AND sml.date BETWEEN %(date_from)s AND %(date_to)s
                        ) sub
                        GROUP BY product_id
                    ) incoming ON incoming.product_id = pp.id
                    LEFT JOIN (
                        SELECT
                            sml.product_id,
                            sum(sml.qty_done) as qty
                        FROM 
                            stock_move_line sml
                            JOIN stock_location lsrc ON sml.location_id = lsrc.id
                            JOIN stock_location ldest ON sml.location_dest_id = ldest.id
                        WHERE 
                            lsrc.usage = 'internal'
                            AND ldest.usage = 'internal'
                            AND lsrc.id != %(location_id)s
                            AND ldest.id = %(location_id)s
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s
                            AND sml.date BETWEEN %(date_from)s AND %(date_to)s
                        GROUP BY sml.product_id
                    ) incoming_2 ON incoming_2.product_id = pp.id
                    LEFT JOIN (
                        SELECT 
                            product_id, 
                            sum(qty) as qty,
                            sum(value * -1) as value
                        FROM (
                            SELECT 
                                sml.product_id, 
                                sml.qty_done as qty,
                                svl.value
                            FROM 
                                stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
                            WHERE sml.location_id = lsrc.id
                            AND sml.location_id = %(location_id)s 
                            AND svl.stock_move_id = sml.move_id
                            AND sml.location_dest_id = ldest.id 
                            AND lsrc.usage = 'internal' 
                            AND ldest.usage IN ('supplier', 'customer','production') 
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s  
                            AND sml.date BETWEEN %(date_from)s AND %(date_to)s
                        ) sub
                        GROUP BY product_id
                    ) outgoing ON outgoing.product_id = pp.id
                    LEFT JOIN (
                        SELECT
                            sml.product_id,
                            sum(sml.qty_done) as qty
                        FROM 
                            stock_move_line sml
                            JOIN stock_location lsrc ON sml.location_id = lsrc.id
                            JOIN stock_location ldest ON sml.location_dest_id = ldest.id
                        WHERE 
                            lsrc.usage = 'internal'
                            AND ldest.usage = 'internal'
                            AND lsrc.id = %(location_id)s
                            AND ldest.id != %(location_id)s
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s
                            AND sml.date BETWEEN %(date_from)s AND %(date_to)s
                        GROUP BY sml.product_id
                    ) outgoing_2 ON outgoing_2.product_id = pp.id
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
                            AND lsrc.usage = 'inventory' 
                            AND ldest.usage = 'internal' 
                            AND sml.state = 'done'
                            AND sml.product_id = %(product_id)s  
                            AND sml.date BETWEEN %(date_from)s AND %(date_to)s)
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
                            AND ldest.usage = 'inventory' 
                            AND sml.state = 'done' 
                            AND sml.product_id = %(product_id)s 
                            AND sml.date BETWEEN %(date_from)s AND %(date_to)s)
                        ) sub
                        GROUP BY product_id
                    ) adjustment ON adjustment.product_id = pp.id
                WHERE pp.id = %(product_id)s
            """
        return query

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        from_date   = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
        to_date     = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''
        location    = obj.location_id.name

        if obj.product_ids:
            products = obj.product_ids
        else:
            products = self.env['product.product'].search([(('categ_id.property_valuation', '=', obj.inventory_valuation))])
        
        # Nama worksheet
        sheet = workbook.add_worksheet(f"{location}")

        # lebar kolom
        sheet.set_column('A:A', 10)  # Kode
        sheet.set_column('B:B', 30)  # Nama Product
        sheet.set_column('C:C', 10)  # Satuan
        sheet.set_column('D:M', 15)  # Saldo Awal, Penerimaan, Pengeluaran, Adjustment, Saldo Akhir


        # Judul Laporan
        title_range = 'E2:J2' if obj.show_value == 'cost' else 'B2:G2'
        date_range = 'E3:J3' if obj.show_value == 'cost' else 'B3:G3'
        sheet.merge_range(title_range, f'INVENTORY MUTATION ({location})', wbf['title_doc'])
        sheet.merge_range(date_range, f'{from_date} s/d {to_date}', wbf['title_doc'])

        # Header Produk
        sheet.merge_range('A4:A5', 'Kode', wbf['header'])
        sheet.merge_range('B4:B5', 'Nama Product', wbf['header'])
        sheet.merge_range('C4:C5', 'Satuan', wbf['header'])
        
        if obj.show_value == 'cost':
            sheet.merge_range('D4:E4', 'Saldo Awal', wbf['header'])
            sheet.merge_range('F4:G4', 'Penerimaan', wbf['header'])
            sheet.merge_range('H4:I4', 'Pengeluaran', wbf['header'])
            sheet.merge_range('J4:K4', 'Adjustment', wbf['header'])
            sheet.merge_range('L4:M4', 'Saldo Akhir', wbf['header'])
            sheet.write('D5', 'Qty', wbf['header'])
            sheet.write('E5', 'Rupiah', wbf['header'])
            sheet.write('F5', 'Qty', wbf['header'])
            sheet.write('G5', 'Rupiah', wbf['header'])
            sheet.write('H5', 'Qty', wbf['header'])
            sheet.write('I5', 'Rupiah', wbf['header'])
            sheet.write('J5', 'Qty', wbf['header'])
            sheet.write('K5', 'Rupiah', wbf['header'])
            sheet.write('L5', 'Qty', wbf['header'])
            sheet.write('M5', 'Rupiah', wbf['header'])
        else:
            sheet.write('D4', 'Saldo Awal', wbf['header'])
            sheet.write('E4', 'Penerimaan', wbf['header'])
            sheet.write('F4', 'Pengeluaran', wbf['header'])
            sheet.write('G4', 'Adjustment', wbf['header'])
            sheet.write('H4', 'Saldo Akhir', wbf['header'])

            sheet.write('D5', 'Qty', wbf['header'])
            sheet.write('E5', 'Qty', wbf['header'])
            sheet.write('F5', 'Qty', wbf['header'])
            sheet.write('G5', 'Qty', wbf['header'])
            sheet.write('H5', 'Qty', wbf['header'])

        row = 5 
        
        for product in products: 
            query = self.get_query()
            if obj.exclude_exhaust:
                query += """
                    GROUP BY 
                        pp.id, 
                        opening.qty, 
                        opening_2.qty, 
                        opening.value,  
                        incoming.qty,  
                        incoming_2.qty,  
                        incoming.value,  
                        outgoing.qty,  
                        outgoing_2.qty,  
                        outgoing.value,  
                        adjustment.qty,  
                        adjustment.value
                    HAVING 
                        (SUM(coalesce(opening.qty, 0.0)) != 0 OR
                        SUM(coalesce(opening_2.qty, 0.0)) != 0 OR
                        SUM(coalesce(incoming.qty, 0.0)) != 0 OR
                        SUM(coalesce(incoming_2.qty, 0.0)) != 0 OR
                        SUM(coalesce(outgoing.qty, 0.0)) != 0 OR
                        SUM(coalesce(outgoing_2.qty, 0.0)) != 0 OR
                        SUM(coalesce(adjustment.qty, 0.0)) != 0)
                """


            params = {
                'product_id' : product.id,
                'location_id': obj.location_id.id,
                'date_from'  : obj.from_date.strftime('%Y-%m-%d 00:00:00'),
                'date_to'    : obj.to_date.strftime('%Y-%m-%d 23:59:59')
            }
            self.env.cr.execute(query, params)
            mutasi_stock = self.env.cr.dictfetchone()

            opening_qty         = mutasi_stock.get('opening_qty') if mutasi_stock else 0.0
            opening_2_qty       = mutasi_stock.get('opening_2_qty') if mutasi_stock else 0.0 # Internal Transfer Opening
            
            incoming_qty        = mutasi_stock.get('incoming_qty') if mutasi_stock else 0.0
            incoming_2_qty      = mutasi_stock.get('incoming_2_qty') if mutasi_stock else 0.0 ## Internal Transfer Incoming
            
            outgoing_qty        = mutasi_stock.get('outgoing_qty') if mutasi_stock else 0.0
            outgoing_2_qty      = mutasi_stock.get('outgoing_2_qty') if mutasi_stock else 0.0 # Internal Transfer Outgoing
            
            adjustment_qty      = mutasi_stock.get('adjustment_qty') if mutasi_stock else 0.0
            closing_qty         = (opening_qty + opening_2_qty) + (incoming_qty + incoming_2_qty) - (outgoing_qty + outgoing_2_qty) + adjustment_qty

            if mutasi_stock:

                # Menampilkan product nya 
                sheet.write(row, 0, product['default_code'] if product['default_code'] else '-', wbf['content']) 
                sheet.write(row, 1, product['name'], wbf['content']) 
                sheet.write(row, 2, product['uom_id'].name, wbf['content']) 

                if obj.show_value == 'cost':
                    opening_value       = mutasi_stock.get('opening_value') if mutasi_stock else 0.0
                    incoming_value      = mutasi_stock.get('incoming_value') if mutasi_stock else 0.0
                    outgoing_value      = mutasi_stock.get('outgoing_value') if mutasi_stock else 0.0
                    adjustment_value    = mutasi_stock.get('adjustment_value') if mutasi_stock else 0.0
                    closing_value       = opening_value + incoming_value - outgoing_value + adjustment_value
                    
                    # Opening
                    sheet.write(row, 3, opening_qty + opening_2_qty, wbf['content_float']) 
                    sheet.write(row, 4, opening_value, wbf['content_float'])  
                    
                    # Incoming
                    sheet.write(row, 5, incoming_qty + incoming_2_qty, wbf['content_float']) 
                    sheet.write(row, 6, incoming_value, wbf['content_float'])  
                    
                    # Outgoing
                    sheet.write(row, 7, outgoing_qty + outgoing_2_qty, wbf['content_float'])  
                    sheet.write(row, 8, outgoing_value, wbf['content_float'])  
                    
                    # Adjustment
                    sheet.write(row, 9, adjustment_qty, wbf['content_float'])  
                    sheet.write(row, 10, adjustment_value, wbf['content_float'])  
                    
                    # Closing
                    sheet.write(row, 11, closing_qty, wbf['content_float'])  
                    sheet.write(row, 12, closing_value, wbf['content_float'])  

                else:
                    # Opening
                    sheet.write(row, 3, opening_qty + opening_2_qty, wbf['content_float'])
                    # Incoming
                    sheet.write(row, 4, incoming_qty + incoming_2_qty, wbf['content_float'])
                    # Outgoing
                    sheet.write(row, 5, outgoing_qty + outgoing_2_qty, wbf['content_float'])
                    # Adjustment
                    sheet.write(row, 6, adjustment_qty, wbf['content_float'])
                    # Closing
                    sheet.write(row, 7, closing_qty, wbf['content_float'])

                row += 1
        
        # Page Layout
        sheet.set_landscape()
        sheet.set_paper(9) # A4
        # sheet.set_header()
        sheet.repeat_rows(1, 4)
        sheet.print_area(0, 0, row, 13)
        sheet.set_print_scale(78)

