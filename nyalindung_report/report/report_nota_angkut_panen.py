from odoo import models
from datetime import datetime, timedelta
from pytz import timezone, UTC

class ReportProduction(models.AbstractModel):
    _name = 'report.nyalindung_report.nota_angkut_panen'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Nota Angkut Panen (NAP) Excel"

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
            'num_format': '#,##0.00'
        })
        self.wbf['content_float'].set_border()

        # Format untuk teks konten yang rata kiri
        self.wbf['content'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
        })
        self.wbf['content'].set_border()
        
        # Format untuk konten no border

        self.wbf['content_no_border'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
        })
        # Format untuk konten rata tengah
        self.wbf['content_center'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_center_border'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_center_border'].set_border()

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
            'num_format': '#,##0.00',
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
            'num_format': '#,##0.00',
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

    # REPORT NAP HANYA MENGGUNAKAN 1 PRODUCT
    # def generate_xlsx_report(self, workbook, datas, obj):
    #     workbook = self.add_workbook_format(workbook)
    #     wbf = self.wbf

    #     sheet  = workbook.add_worksheet("Laporan NAP")
    #     row = 0

    #     sheet.write(0, 0,obj.env.company.name,wbf['content_no_border'])
    #     sheet.merge_range('A2:D2','Report Produksi Nota Angkut Panen (NAP)',wbf['content_no_border'])
    #     sheet.write(2, 0,'Untuk Periode',wbf['content_no_border'])
    #     sheet.write(2, 1,str(obj.date_start),wbf['content_no_border'])
    #     sheet.write(2, 2,'s/d',wbf['content_no_border'])
    #     sheet.write(2, 3,str(obj.date_end),wbf['content_no_border'])
    #     sheet.write(3, 0,'Product',wbf['content_no_border'])
    #     sheet.write(3, 1,obj.product_id.name,wbf['content_no_border'])
    #     sheet.merge_range('A6:F6','NAP',wbf['content_center_border'])
    #     sheet.merge_range('G6:J6','Material Receipt',wbf['content_center_border'])
    #     sheet.merge_range('K6:N6','Material Receipt Return',wbf['content_center_border'])
    #     sheet.write(6, 0,'Tanggal',wbf['content_center_border'])
    #     sheet.write(6, 1,'Document',wbf['content_center_border'])
    #     sheet.write(6, 2,'Location',wbf['content_center_border'])
    #     sheet.write(6, 3,'Qty',wbf['content_center_border'])
    #     sheet.write(6, 4,'UoM',wbf['content_center_border'])
    #     sheet.write(6, 5,'Status',wbf['content_center_border'])
    #     sheet.write(6, 6,'Document#',wbf['content_center_border'])
    #     sheet.write(6, 7,'Qty',wbf['content_center_border'])
    #     sheet.write(6, 8,'UoM',wbf['content_center_border'])
    #     sheet.write(6, 9,'Status',wbf['content_center_border'])
    #     sheet.write(6, 10,'Document#',wbf['content_center_border'])
    #     sheet.write(6, 11,'Qty',wbf['content_center_border'])
    #     sheet.write(6, 12,'UoM',wbf['content_center_border'])
    #     sheet.write(6, 13,'Status',wbf['content_center_border'])
    #     row = 7

    #     sql = """
    #     select 
    #         tp.product_id as product,
    #         ln.date_nap as tanggal,
    #         ln.name as dokumen_nap,
    #         lpb.name as lokasi,
    #         tp.product_qty as qty_nap,
    #         uom.name->>'en_US' as uom_nap,
    #         ln.state as state_nap,
    #         sp.name as mr_name,
    #         sm.quantity_done as mr_qty,
    #         uom_sm.name->>'en_US' as mr_uom,
    #         sm.state as mr_state,
    #         sm_return.name as retur_name,
    #         sm_return.quantity_done as retur_qty,
    #         uom_return.name->>'en_US' as retur_uom,
    #         sm_return.state as retur_state
            
            
    #     from timbangan_pabrik as tp
    #     left join lhm_nap as ln on ln.id = tp.lhm_nap_id
    #     left join lhm_plant_block as lpb on lpb.id = tp.block_id
    #     left join stock_location as sl on sl.id = lpb.location_id
    #     left join uom_uom as uom on uom.id = tp.uom_id
    #     left join stock_picking as sp on sp.id = tp.stock_picking_id
    #     left join stock_move as sm on sm.picking_id = sp.id
    #     left join uom_uom as uom_sm on uom_sm.id = sm.product_uom
    #     left join stock_move as sm_return on sm.id = sm_return.origin_returned_move_id
    #     left join uom_uom as uom_return on uom_return.id = sm_return.product_uom
    #     where tp.product_id = {product_id} and tp.tgl_panen between '{date_start}' and '{date_end}'
    #     group by product,lokasi,tanggal,dokumen_nap,state_nap,uom_nap,mr_name,mr_uom,mr_state,retur_name,retur_uom,retur_state,qty_nap,mr_qty,retur_qty
    #      """.format(product_id=obj.product_id.id,date_start=str(obj.date_start),date_end=(obj.date_end))

    #     self._cr.execute(sql)
    #     datas = self._cr.dictfetchall()
    #     col = 0
    #     for data in datas:
    #         sheet.write(row,0,data['tanggal'],wbf['content_center_border'])
    #         sheet.write(row,1,data['dokumen_nap'],wbf['content_center_border'])
    #         sheet.write(row,2,data['lokasi'],wbf['content_center_border'])
    #         sheet.write(row,3,data['qty_nap'],wbf['content_center_border'])
    #         sheet.write(row,4,data['uom_nap'],wbf['content_center_border'])
    #         sheet.write(row,5,data['state_nap'],wbf['content_center_border'])
    #         sheet.write(row,6,data['mr_name'],wbf['content_center_border'])
    #         sheet.write(row,7,data['mr_qty'],wbf['content_center_border'])
    #         sheet.write(row,8,data['mr_uom'],wbf['content_center_border'])
    #         sheet.write(row,9,data['mr_state'],wbf['content_center_border'])
    #         sheet.write(row,10,data['retur_name'],wbf['content_center_border'])
    #         sheet.write(row,11,data['retur_qty'],wbf['content_center_border'])
    #         sheet.write(row,12,data['retur_uom'],wbf['content_center_border'])
    #         sheet.write(row,13,data['retur_state'],wbf['content_center_border'])
    #         row += 1
        
    #     # sheet.write(, 0,'Product',wbf['data'])
    

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        sheet = workbook.add_worksheet("Laporan NAP")
        row = 0

        products = obj.product_ids if obj.product_ids else self.env['product.product'].search([])

        sheet.write(0, 0, obj.env.company.name, wbf['content_no_border'])
        sheet.merge_range('A2:D2', 'Report Produksi Nota Angkut Panen (NAP)', wbf['content_no_border'])
        sheet.write(2, 0, 'Untuk Periode', wbf['content_no_border'])
        sheet.write(2, 1, str(obj.date_start), wbf['content_no_border'])
        sheet.write(2, 2, 's/d', wbf['content_no_border'])
        sheet.write(2, 3, str(obj.date_end), wbf['content_no_border'])

        row = 4 

        for product in products:
            sheet.write(row, 0, 'Product', wbf['content_no_border'])
            sheet.write(row, 1, product.name, wbf['content_no_border'])
            row += 1  

            sheet.merge_range(row, 0, row, 5, 'NAP', wbf['content_center_border'])
            sheet.merge_range(row, 6, row, 9, 'Material Receipt', wbf['content_center_border'])
            sheet.merge_range(row, 10, row, 13, 'Material Receipt Return', wbf['content_center_border'])
            row += 1

            sheet.write(row, 0, 'Tanggal', wbf['content_center_border'])
            sheet.write(row, 1, 'Document', wbf['content_center_border'])
            sheet.write(row, 2, 'Location', wbf['content_center_border'])
            sheet.write(row, 3, 'Qty', wbf['content_center_border'])
            sheet.write(row, 4, 'UoM', wbf['content_center_border'])
            sheet.write(row, 5, 'Status', wbf['content_center_border'])
            sheet.write(row, 6, 'Document#', wbf['content_center_border'])
            sheet.write(row, 7, 'Qty', wbf['content_center_border'])
            sheet.write(row, 8, 'UoM', wbf['content_center_border'])
            sheet.write(row, 9, 'Status', wbf['content_center_border'])
            sheet.write(row, 10, 'Document#', wbf['content_center_border'])
            sheet.write(row, 11, 'Qty', wbf['content_center_border'])
            sheet.write(row, 12, 'UoM', wbf['content_center_border'])
            sheet.write(row, 13, 'Status', wbf['content_center_border'])
            row += 1  

            sql = """
            SELECT 
                tp.product_id AS product,
                ln.date_nap AS tanggal,
                ln.name AS dokumen_nap,
                lpb.name AS lokasi,
                tp.product_qty AS qty_nap,
                uom.name->>'en_US' AS uom_nap,
                ln.state AS state_nap,
                sp.name AS mr_name,
                sm.quantity_done AS mr_qty,
                uom_sm.name->>'en_US' AS mr_uom,
                sm.state AS mr_state,
                sm_return.name AS retur_name,
                sm_return.quantity_done AS retur_qty,
                uom_return.name->>'en_US' AS retur_uom,
                sm_return.state AS retur_state
            FROM timbangan_pabrik AS tp
            LEFT JOIN lhm_nap AS ln ON ln.id = tp.lhm_nap_id
            LEFT JOIN lhm_plant_block AS lpb ON lpb.id = tp.block_id
            LEFT JOIN stock_location AS sl ON sl.id = lpb.location_id
            LEFT JOIN uom_uom AS uom ON uom.id = tp.uom_id
            LEFT JOIN stock_picking AS sp ON sp.id = tp.stock_picking_id
            LEFT JOIN stock_move AS sm ON sm.picking_id = sp.id
            LEFT JOIN uom_uom AS uom_sm ON uom_sm.id = sm.product_uom
            LEFT JOIN stock_move AS sm_return ON sm.id = sm_return.origin_returned_move_id
            LEFT JOIN uom_uom AS uom_return ON uom_return.id = sm_return.product_uom
            WHERE tp.product_id = {product_id} 
            AND tp.tgl_panen BETWEEN '{date_start}' AND '{date_end}'
            GROUP BY product, lokasi, tanggal, dokumen_nap, state_nap, uom_nap, 
                    mr_name, mr_uom, mr_state, retur_name, retur_uom, retur_state, 
                    qty_nap, mr_qty, retur_qty
            """.format(product_id=product.id, date_start=str(obj.date_start), date_end=str(obj.date_end))

            self._cr.execute(sql)
            datas = self._cr.dictfetchall()

            for data in datas:
                utc_time = data['tanggal']  
                jakarta_tz = timezone('Asia/Jakarta')
                utc_time = datetime.combine(utc_time, datetime.min.time())
                utc_time = utc_time.replace(tzinfo=UTC)
                local_time = utc_time.astimezone(jakarta_tz)

                sheet.write(row, 0, local_time.strftime('%d-%m-%Y'), wbf['content_center_border'])
                sheet.write(row, 1, data['dokumen_nap'], wbf['content_center_border'])
                sheet.write(row, 2, data['lokasi'], wbf['content_center_border'])
                sheet.write(row, 3, data['qty_nap'], wbf['content_center_border'])
                sheet.write(row, 4, data['uom_nap'], wbf['content_center_border'])
                sheet.write(row, 5, data['state_nap'], wbf['content_center_border'])
                sheet.write(row, 6, data['mr_name'], wbf['content_center_border'])
                sheet.write(row, 7, data['mr_qty'], wbf['content_center_border'])
                sheet.write(row, 8, data['mr_uom'], wbf['content_center_border'])
                sheet.write(row, 9, data['mr_state'], wbf['content_center_border'])
                sheet.write(row, 10, data['retur_name'], wbf['content_center_border'])
                sheet.write(row, 11, data['retur_qty'], wbf['content_center_border'])
                sheet.write(row, 12, data['retur_uom'], wbf['content_center_border'])
                sheet.write(row, 13, data['retur_state'], wbf['content_center_border'])
                row += 1 

            row += 2  



