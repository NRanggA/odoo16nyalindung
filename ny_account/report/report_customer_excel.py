from odoo import models, fields, api
from odoo.exceptions import UserError
import io
import base64
from datetime import datetime
import xlsxwriter

class ReportCustomerInvoiceXlsx(models.AbstractModel):
    _name = 'report.ny_account.report_customer_invoice_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Customer Invoice XLSX"

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
        # Format untuk header kolom tabel
        self.wbf['account'] = workbook.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10,
            # 'font_color': '#E17564',
            'bg_color': '#F4FFC3',
            'border': 1
        })
        self.wbf['account'].set_text_wrap() 
        self.wbf['account'].set_border()
        
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
            'valign': 'vcenter',
            'num_format': '#,##0.00',
        })
        self.wbf['content_number'].set_border()

        self.wbf['content_number_center'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0.00',
        })
        self.wbf['content_number_center'].set_border()

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
            # 'num_format': '#,##0.00',
            'num_format': '#,##0'
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
            WITH down_payments AS (
                SELECT 
                    ai.id AS invoice_id, 
                    COALESCE(SUM(ABS(ail.price_subtotal)), 0) AS total_down_payment
                FROM account_move ai
                JOIN account_move_line ail ON ai.id = ail.move_id
                JOIN product_product pp ON ail.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE ai.move_type = 'out_invoice'
                AND ai.state = 'posted'
                AND CAST(pt.name AS TEXT) ILIKE '%%down payment%%'
                GROUP BY ai.id
            )
            SELECT 
                ai.invoice_date, 
                ai.name AS invoice_name, 
                ai.partner_id,
                ail.plantation_location_type_id,
                ail.plantation_varieties_id,
                ail.plantation_location_id,
                ail.plantation_activity_id,
                ail.product_id, 
                ail.name AS description, 
                ail.quantity, 
                ail.price_unit, 
                ail.price_subtotal,
                ai.invoice_payment_term_id AS term_of_payment,
                CASE 
                    WHEN CAST(pt.name AS TEXT) ILIKE '%%down payment%%' THEN 0 
                    ELSE COALESCE(dp.total_down_payment, 0) 
                END AS down_payment,
                (ail.price_subtotal - 
                    CASE 
                        WHEN CAST(pt.name AS TEXT) ILIKE '%%down payment%%' THEN 0 
                        ELSE COALESCE(dp.total_down_payment, 0) 
                    END
                ) AS outstanding_amount
            FROM account_move ai
            LEFT JOIN account_move_line ail ON ai.id = ail.move_id
            LEFT JOIN product_product pp ON ail.product_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN down_payments dp ON ai.id = dp.invoice_id
            WHERE ai.move_type = 'out_invoice'
            AND ai.state = 'posted'
            AND ai.invoice_date BETWEEN %s AND %s
            AND ail.display_type IN ('product')
            ORDER BY ai.invoice_date, ai.name;
        """
        return query

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        # Pastikan format tanggal dalam format yang benar
        row = 0
        from_date = obj.from_date.strftime('%Y-%m-%d') if obj.from_date else None
        to_date = obj.to_date.strftime('%Y-%m-%d') if obj.to_date else None

        # Define the worksheet before writing to it
        sheet = workbook.add_worksheet("Customer Invoice")
        sheet.write(row, 0, 'Sales Report', wbf['title_doc'])
        row += 1
        sheet.write(row, 0, 'Date:', wbf['title_doc'])
        sheet.write(row, 1, f'{from_date} s/d {to_date}', wbf['title_sec'])
        row += 3

        
        # # Set format kolom
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 18)
        sheet.set_column('C:C', 27)
        sheet.set_column('D:D', 9)
        sheet.set_column('E:E', 9)
        sheet.set_column('F:F', 9)
        sheet.set_column('G:G', 9)
        sheet.set_column('H:H', 14)
        sheet.set_column('I:I', 16)
        sheet.set_column('J:J', 9)
        sheet.set_column('K:K', 14)
        sheet.set_column('L:L', 14)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 9)
        sheet.set_column('O:O', 15)


        # Header Kolom
        headers = ['Tanggal Invoice', 'No. Invoice', 'Konsumen', 'Tipe Lokasi', 'ORG', 'Lokasi', 'Aktivitas','Product', 'Deskripsi', 'Quantity',
                'Harga', 'Total Harga', 'Term of Payment', 'Down Payment', 'Net AR']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, wbf['header'])
        row += 1

        # Eksekusi query
        query = self.get_query()
        self.env.cr.execute(query, (from_date, to_date))
        results = self.env.cr.fetchall()

        # Tulis data ke sheet
        for invoice_date, invoice_name, partner_id, plantation_location_type_id, plantation_varieties_id, plantation_location_id, plantation_activity_id, product_id, description, quantity, price_unit, price_subtotal, term_of_payment, down_payment, outstanding_amount in results:

            
            sheet.write(row, 0, invoice_date.strftime('%d-%m-%Y') if invoice_date else '', wbf['content'])
            sheet.write(row, 1, invoice_name, wbf['content'])
            partner_name = self.env['res.partner'].browse(partner_id).name if partner_id else '-'
            sheet.write(row, 2, partner_name, wbf['content'])
            location_type_name = self.env['lhm.location.type'].browse(plantation_location_type_id).name if plantation_location_type_id else '-'
            sheet.write(row, 3, location_type_name, wbf['content'])
            varieties_name = self.env['plant.varieties'].browse(plantation_varieties_id).name if plantation_varieties_id else '-'
            sheet.write(row, 4, varieties_name, wbf['content'])
            location_name = self.env['lhm.location'].browse(plantation_location_id).name if plantation_location_id else '-'
            sheet.write(row, 5, location_name, wbf['content'])
            activity_name = self.env['lhm.activity'].browse(plantation_activity_id).name if plantation_activity_id else '-'
            sheet.write(row, 6, activity_name, wbf['content'])
            product_name = self.env['product.product'].browse(product_id).name if product_id else '-'
            sheet.write(row, 7, product_name, wbf['content'])
            sheet.write(row, 8, description, wbf['content'])
            sheet.write(row, 9, quantity, wbf['content_number_center'])
            sheet.write(row, 10, price_unit, wbf['total_float'])
            sheet.write(row, 11, price_subtotal, wbf['total_float'])
            payment_term_name = self.env['account.payment.term'].browse(term_of_payment).name if term_of_payment else '-'
            sheet.write(row, 12, payment_term_name, wbf['content'])
            sheet.write(row, 13, down_payment, wbf['total_float'])
            sheet.write(row, 14, outstanding_amount, wbf['total_float'])
            row += 1
