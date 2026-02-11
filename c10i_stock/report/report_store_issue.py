from odoo import models

class ReportStockMutation(models.AbstractModel):
    _name = 'report.c10i_stock.store_issue_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Store True Excel"

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
            'align': 'center',
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

    # def get_query_old(self):
    #     query = """
    #             SELECT
    #                 pp.id, 
    #                 coalesce(opening.qty, 0.0) as opening_qty,
    #                 coalesce(opening.value, 0.0) as opening_value,
    #                 coalesce(incoming.qty, 0.0) as incoming_qty,
    #                 coalesce(incoming.value, 0.0) as incoming_value,
    #                 coalesce(outgoing.qty, 0.0) as outgoing_qty,
    #                 coalesce(outgoing.value, 0.0) as outgoing_value,
    #                 coalesce(adjustment.qty, 0.0) as adjustment_qty,
    #                 coalesce(adjustment.value, 0.0) as adjustment_value,
    #                 coalesce(incoming_2.qty, 0.0) as incoming_2_qty,
    #                 coalesce(outgoing_2.qty, 0.0) as outgoing_2_qty,
    #                 coalesce(opening_2.qty, 0.0) as opening_2_qty
    #             FROM
    #                 product_product pp
    #                 LEFT JOIN (
    #                     SELECT
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value) as value
    #                     FROM (
    #                         (SELECT 
    #                             sm.product_id, 
    #                             sm.product_uom_qty as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sm.location_id = lsrc.id 
    #                         AND svl.stock_move_id = sm.id 
    #                         AND sm.location_dest_id = ldest.id 
    #                         AND sm.location_dest_id = %(location_id)s
    #                         AND lsrc.usage != 'internal' 
    #                         AND ldest.usage = 'internal'
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s
    #                         AND sm.date < %(date_from)s)
    #                         UNION ALL
    #                         (SELECT 
    #                             sm.product_id, 
    #                             -sm.product_uom_qty as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sm.location_id = lsrc.id
    #                         AND sm.location_id = %(location_id)s 
    #                         AND svl.stock_move_id = sm.id 
    #                         AND sm.location_dest_id = ldest.id 
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage != 'internal'
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s 
    #                         AND sm.date < %(date_from)s)
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) opening ON opening.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT
    #                         product_id, 
    #                         sum(qty) as qty
    #                     FROM (
    #                         (SELECT 
    #                             sm.product_id, 
    #                             sm.product_uom_qty as qty
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest
    #                         WHERE sm.location_id = lsrc.id 
    #                         AND lsrc.id != %(location_id)s
    #                         AND ldest.id = %(location_id)s
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage = 'internal'
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s
    #                         AND sm.date < %(date_from)s)
    #                         UNION ALL
    #                         (SELECT 
    #                             sm.product_id, 
    #                             -sm.product_uom_qty as qty
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest
    #                         WHERE sm.location_id = lsrc.id
    #                         AND lsrc.usage = 'internal'
    #                         AND ldest.usage = 'internal'
    #                         AND lsrc.id = %(location_id)s
    #                         AND ldest.id != %(location_id)s
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s 
    #                         AND sm.date < %(date_from)s)
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) opening_2 ON opening_2.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT 
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value) as value
    #                     FROM (
    #                         SELECT 
    #                             sm.product_id, 
    #                             sm.product_uom_qty as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sm.location_id = lsrc.id 
    #                         AND svl.stock_move_id = sm.id 
    #                         AND sm.location_dest_id = ldest.id
    #                         AND sm.location_dest_id = %(location_id)s 
    #                         AND lsrc.usage IN ('supplier', 'customer','production') 
    #                         AND ldest.usage = 'internal' 
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s 
    #                         AND sm.date BETWEEN %(date_from)s AND %(date_to)s
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) incoming ON incoming.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT
    #                         sm.product_id,
    #                         sum(sm.product_uom_qty) as qty
    #                     FROM 
    #                         stock_move sm
    #                         JOIN stock_location lsrc ON sm.location_id = lsrc.id
    #                         JOIN stock_location ldest ON sm.location_dest_id = ldest.id
    #                     WHERE 
    #                         lsrc.usage = 'internal'
    #                         AND ldest.usage = 'internal'
    #                         AND lsrc.id != %(location_id)s
    #                         AND ldest.id = %(location_id)s
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s
    #                         AND sm.date BETWEEN %(date_from)s AND %(date_to)s
    #                     GROUP BY sm.product_id
    #                 ) incoming_2 ON incoming_2.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT 
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value * -1) as value
    #                     FROM (
    #                         SELECT 
    #                             sm.product_id, 
    #                             sm.product_uom_qty as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sm.location_id = lsrc.id
    #                         AND sm.location_id = %(location_id)s 
    #                         AND svl.stock_move_id = sm.id
    #                         AND sm.location_dest_id = ldest.id 
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage IN ('supplier', 'customer','production') 
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s  
    #                         AND sm.date BETWEEN %(date_from)s AND %(date_to)s
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) outgoing ON outgoing.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT
    #                         sm.product_id,
    #                         sum(sm.product_uom_qty) as qty
    #                     FROM 
    #                         stock_move sm
    #                         JOIN stock_location lsrc ON sm.location_id = lsrc.id
    #                         JOIN stock_location ldest ON sm.location_dest_id = ldest.id
    #                     WHERE 
    #                         lsrc.usage = 'internal'
    #                         AND ldest.usage = 'internal'
    #                         AND lsrc.id = %(location_id)s
    #                         AND ldest.id != %(location_id)s
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s
    #                         AND sm.date BETWEEN %(date_from)s AND %(date_to)s
    #                     GROUP BY sm.product_id
    #                 ) outgoing_2 ON outgoing_2.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT 
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value) as value 
    #                     FROM (
    #                         (SELECT 
    #                             sm.product_id, 
    #                             sm.product_uom_qty as qty,
    #                             svl.value 
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sm.location_id = lsrc.id
    #                         AND svl.stock_move_id = sm.id 
    #                         AND sm.location_dest_id = ldest.id
    #                         AND sm.location_dest_id = %(location_id)s  
    #                         AND lsrc.usage = 'inventory' 
    #                         AND ldest.usage = 'internal' 
    #                         AND sm.state = 'done'
    #                         AND sm.product_id = %(product_id)s  
    #                         AND sm.date BETWEEN %(date_from)s AND %(date_to)s)
    #                         UNION ALL
    #                         (SELECT 
    #                             sm.product_id, 
    #                             -sm.product_uom_qty as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move sm, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sm.location_id = lsrc.id
    #                         AND sm.location_id = %(location_id)s 
    #                         AND svl.stock_move_id = sm.id
    #                         AND sm.location_dest_id = ldest.id 
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage = 'inventory' 
    #                         AND sm.state = 'done' 
    #                         AND sm.product_id = %(product_id)s 
    #                         AND sm.date BETWEEN %(date_from)s AND %(date_to)s)
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) adjustment ON adjustment.product_id = pp.id
    #             WHERE pp.id = %(product_id)s
    #         """
    #     return query

    # def get_query(self):
    #     query = """
    #             SELECT
    #                 pp.id, 
    #                 coalesce(opening.qty, 0.0) as opening_qty,
    #                 coalesce(opening.value, 0.0) as opening_value,
    #                 coalesce(incoming.qty, 0.0) as incoming_qty,
    #                 coalesce(incoming.value, 0.0) as incoming_value,
    #                 coalesce(outgoing.qty, 0.0) as outgoing_qty,
    #                 coalesce(outgoing.value, 0.0) as outgoing_value,
    #                 coalesce(adjustment.qty, 0.0) as adjustment_qty,
    #                 coalesce(adjustment.value, 0.0) as adjustment_value,
    #                 coalesce(incoming_2.qty, 0.0) as incoming_2_qty,
    #                 coalesce(outgoing_2.qty, 0.0) as outgoing_2_qty,
    #                 coalesce(opening_2.qty, 0.0) as opening_2_qty
    #             FROM
    #                 product_product pp
    #                 LEFT JOIN (
    #                     SELECT
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value) as value
    #                     FROM (
    #                         (SELECT 
    #                             sml.product_id, 
    #                             sml.qty_done as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sml.location_id = lsrc.id 
    #                         AND svl.stock_move_id = sml.move_id 
    #                         AND sml.location_dest_id = ldest.id 
    #                         AND sml.location_dest_id = %(location_id)s
    #                         AND lsrc.usage != 'internal' 
    #                         AND ldest.usage = 'internal'
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s
    #                         AND sml.date < %(date_from)s)
    #                         UNION ALL
    #                         (SELECT 
    #                             sml.product_id, 
    #                             -sml.qty_done as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sml.location_id = lsrc.id
    #                         AND sml.location_id = %(location_id)s 
    #                         AND svl.stock_move_id = sml.move_id 
    #                         AND sml.location_dest_id = ldest.id 
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage != 'internal'
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s 
    #                         AND sml.date < %(date_from)s)
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) opening ON opening.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT
    #                         product_id, 
    #                         sum(qty) as qty
    #                     FROM (
    #                         (SELECT 
    #                             sml.product_id, 
    #                             sml.qty_done as qty
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest
    #                         WHERE sml.location_id = lsrc.id 
    #                         AND lsrc.id != %(location_id)s
    #                         AND ldest.id = %(location_id)s
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage = 'internal'
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s
    #                         AND sml.date < %(date_from)s)
    #                         UNION ALL
    #                         (SELECT 
    #                             sml.product_id, 
    #                             -sml.qty_done as qty
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest
    #                         WHERE sml.location_id = lsrc.id
    #                         AND lsrc.usage = 'internal'
    #                         AND ldest.usage = 'internal'
    #                         AND lsrc.id = %(location_id)s
    #                         AND ldest.id != %(location_id)s
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s 
    #                         AND sml.date < %(date_from)s)
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) opening_2 ON opening_2.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT 
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value) as value
    #                     FROM (
    #                         SELECT 
    #                             sml.product_id, 
    #                             sml.qty_done as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sml.location_id = lsrc.id 
    #                         AND svl.stock_move_id = sml.move_id 
    #                         AND sml.location_dest_id = ldest.id
    #                         AND sml.location_dest_id = %(location_id)s 
    #                         AND lsrc.usage IN ('supplier', 'customer','production') 
    #                         AND ldest.usage = 'internal' 
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s 
    #                         AND sml.date BETWEEN %(date_from)s AND %(date_to)s
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) incoming ON incoming.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT
    #                         sml.product_id,
    #                         sum(sml.qty_done) as qty
    #                     FROM 
    #                         stock_move_line sml
    #                         JOIN stock_location lsrc ON sml.location_id = lsrc.id
    #                         JOIN stock_location ldest ON sml.location_dest_id = ldest.id
    #                     WHERE 
    #                         lsrc.usage = 'internal'
    #                         AND ldest.usage = 'internal'
    #                         AND lsrc.id != %(location_id)s
    #                         AND ldest.id = %(location_id)s
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s
    #                         AND sml.date BETWEEN %(date_from)s AND %(date_to)s
    #                     GROUP BY sml.product_id
    #                 ) incoming_2 ON incoming_2.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT 
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value * -1) as value
    #                     FROM (
    #                         SELECT 
    #                             sml.product_id, 
    #                             sml.qty_done as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sml.location_id = lsrc.id
    #                         AND sml.location_id = %(location_id)s 
    #                         AND svl.stock_move_id = sml.move_id
    #                         AND sml.location_dest_id = ldest.id 
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage IN ('supplier', 'customer','production') 
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s  
    #                         AND sml.date BETWEEN %(date_from)s AND %(date_to)s
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) outgoing ON outgoing.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT
    #                         sml.product_id,
    #                         sum(sml.qty_done) as qty
    #                     FROM 
    #                         stock_move_line sml
    #                         JOIN stock_location lsrc ON sml.location_id = lsrc.id
    #                         JOIN stock_location ldest ON sml.location_dest_id = ldest.id
    #                     WHERE 
    #                         lsrc.usage = 'internal'
    #                         AND ldest.usage = 'internal'
    #                         AND lsrc.id = %(location_id)s
    #                         AND ldest.id != %(location_id)s
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s
    #                         AND sml.date BETWEEN %(date_from)s AND %(date_to)s
    #                     GROUP BY sml.product_id
    #                 ) outgoing_2 ON outgoing_2.product_id = pp.id
    #                 LEFT JOIN (
    #                     SELECT 
    #                         product_id, 
    #                         sum(qty) as qty,
    #                         sum(value) as value 
    #                     FROM (
    #                         (SELECT 
    #                             sml.product_id, 
    #                             sml.qty_done as qty,
    #                             svl.value 
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sml.location_id = lsrc.id
    #                         AND svl.stock_move_id = sml.move_id 
    #                         AND sml.location_dest_id = ldest.id
    #                         AND sml.location_dest_id = %(location_id)s  
    #                         AND lsrc.usage = 'inventory' 
    #                         AND ldest.usage = 'internal' 
    #                         AND sml.state = 'done'
    #                         AND sml.product_id = %(product_id)s  
    #                         AND sml.date BETWEEN %(date_from)s AND %(date_to)s)
    #                         UNION ALL
    #                         (SELECT 
    #                             sml.product_id, 
    #                             -sml.qty_done as qty,
    #                             svl.value
    #                         FROM 
    #                             stock_move_line sml, stock_location lsrc, stock_location ldest, stock_valuation_layer svl
    #                         WHERE sml.location_id = lsrc.id
    #                         AND sml.location_id = %(location_id)s 
    #                         AND svl.stock_move_id = sml.move_id
    #                         AND sml.location_dest_id = ldest.id 
    #                         AND lsrc.usage = 'internal' 
    #                         AND ldest.usage = 'inventory' 
    #                         AND sml.state = 'done' 
    #                         AND sml.product_id = %(product_id)s 
    #                         AND sml.date BETWEEN %(date_from)s AND %(date_to)s)
    #                     ) sub
    #                     GROUP BY product_id
    #                 ) adjustment ON adjustment.product_id = pp.id
    #             WHERE pp.id = %(product_id)s
    #         """
    #     return query

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        from_date = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
        to_date = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''
        operation_type = obj.operation_type_id.name

        # Nama worksheet
        sheet = workbook.add_worksheet(f"{operation_type}")

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
        sheet.write('A2', 'Detail Store Issue', wbf['title_doc'])
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
        sheet.write('I5', 'KETERANGAN', wbf['header'])
        
        if obj.with_journal:
            sheet.write('J5', 'Value', wbf['header'])
            sheet.write('K5', 'Journal Entry', wbf['header'])
            sheet.write('L5', 'Account', wbf['header'])
            sheet.write('M5', 'Value on Journal', wbf['header'])
            sheet.write('N5', 'Tipe Lokasi', wbf['header'])
            sheet.write('O5', 'ORG', wbf['header'])
            sheet.write('P5', 'Lokasi', wbf['header'])
            sheet.write('Q5', 'Aktivitas', wbf['header'])
            sheet.write('R5', 'Account', wbf['header'])
            sheet.write('S5', 'Value on Journal', wbf['header'])

        row = 5

        domain = [
            ('picking_type_id', '=', obj.operation_type_id.id),
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
            tags = ""
            if stock.product_id.product_tag_ids:
                tags = ', '.join(stock.product_id.product_tag_ids.mapped('name'))
            sheet.write(row, 8, tags, wbf['content']) 

            if obj.with_journal:
                for svl in stock.stock_valuation_layer_ids:
                    sheet.write(row, 9, svl.value, wbf['content_float'])

                if stock.account_move_ids:
                    for acc_move in stock.account_move_ids:  
                        sheet.write(row, 10, acc_move.name, wbf['content']) 
                        
                        for acc_move_line in acc_move.line_ids:
                            if stock.product_id.categ_id.property_stock_valuation_account_id.id == acc_move_line.account_id.id:
                                sheet.write(row, 11, f"{acc_move_line.account_id.code} - {acc_move_line.account_id.name}", wbf['content'])  
                                sheet.write(row, 12, acc_move_line.balance, wbf['content_float'])  
                                # row += 1 
                            else:
                                sheet.write(row, 13, acc_move_line.plantation_location_type_id.name if acc_move_line.plantation_location_type_id else '-', wbf['content'])
                                sheet.write(row, 14, acc_move_line.plantation_varieties_id.name if acc_move_line.plantation_varieties_id else '-', wbf['content'])
                                sheet.write(row, 15, acc_move_line.plantation_location_id.name if acc_move_line.plantation_location_id else '-', wbf['content'])
                                sheet.write(row, 16, f"{acc_move_line.plantation_activity_id.code} - {acc_move_line.plantation_activity_id.name}" if acc_move_line.plantation_activity_id else '-', wbf['content'])
                                sheet.write(row, 17, f"{acc_move_line.account_id.code} - {acc_move_line.account_id.name}", wbf['content'])
                                sheet.write(row, 18, acc_move_line.balance, wbf['content_float'])
                            
                                row += 1 
                else:
                    sheet.write(row, 10, '-', wbf['content']) 
                    sheet.write(row, 11, '-', wbf['content'])  
                    sheet.write(row, 11, '-', wbf['content'])  
                    sheet.write(row, 13, '-', wbf['content'])  
                    sheet.write(row, 14, '-', wbf['content'])  
                    sheet.write(row, 15, '-', wbf['content'])  
                    sheet.write(row, 16, '-', wbf['content'])  
                    sheet.write(row, 17, '-', wbf['content'])  
                    sheet.write(row, 18, '-', wbf['content'])  

                
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


