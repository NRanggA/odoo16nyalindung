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
        sheet.set_column('D:D', 24)
        sheet.set_column('E:E', 22)
        sheet.set_column('F:F', 8)
        sheet.set_column('G:G', 12)
        sheet.set_column('H:H', 14)
        sheet.set_column('I:I', 16)
        sheet.set_column('J:J', 14)
        sheet.set_column('K:K', 19)


        # Header Kolom
        headers = ['Tanggal Invoice', 'No. Invoice', 'Konsumen', 'Product', 'Deskripsi', 'Quantity',
                'Harga', 'Total Harga', 'Term of Payment', 'Down Payment', 'Net AR']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, wbf['header'])
        row += 1

        # Eksekusi query
        query = self.get_query()
        self.env.cr.execute(query, (from_date, to_date))
        results = self.env.cr.fetchall()

        # Tulis data ke sheet
        for invoice_date, invoice_name, partner_id, product_id, description, quantity, price_unit, price_subtotal, term_of_payment, down_payment, outstanding_amount in results:

            
            sheet.write(row, 0, invoice_date.strftime('%d-%m-%Y') if invoice_date else '', wbf['content'])
            sheet.write(row, 1, invoice_name, wbf['content'])
            partner_name = self.env['res.partner'].browse(partner_id).name if partner_id else '-'
            sheet.write(row, 2, partner_name, wbf['content'])
            product_name = self.env['product.product'].browse(product_id).name if product_id else '-'
            sheet.write(row, 3, product_name, wbf['content'])
            sheet.write(row, 4, description, wbf['content'])
            sheet.write(row, 5, quantity, wbf['content'])
            sheet.write(row, 6, price_unit, wbf['total_float'])
            sheet.write(row, 7, price_subtotal, wbf['total_float'])
            payment_term_name = self.env['account.payment.term'].browse(term_of_payment).name if term_of_payment else '-'
            sheet.write(row, 8, payment_term_name, wbf['content'])
            sheet.write(row, 9, down_payment, wbf['total_float'])
            sheet.write(row, 10, outstanding_amount, wbf['total_float'])
            row += 1


        # # Iterasi Setiap Akun
        # accounts = obj.account_ids if obj.account_ids else self.env['account.account'].search([])
        # for account in accounts:
        #     query = self.get_query()

        #     params = {
        #         'account_id': account.id,
        #         'date_from': obj.from_date.strftime('%Y-%m-%d 00:00:00'),
        #     }

        #     self.env.cr.execute(query, params)
        #     account_move = self.env.cr.dictfetchone()

        #     # Hitung Saldo Awal
        #     if account_move:
        #         total_debit = account_move['total_debit']
        #         total_credit = account_move['total_credit']
        #     else:
        #         total_debit = 0.0
        #         total_credit = 0.0

        #     opening_balance = total_debit - total_credit

        #     # Opening
        #     sheet.write(row, 0, '', wbf['account'])
        #     sheet.write(row, 1, f'{account.code} {account.name}', wbf['account'])
        #     sheet.write(row, 2, '', wbf['account'])
        #     sheet.write(row, 3, '', wbf['account'])
        #     sheet.write(row, 4, '', wbf['account'])
        #     sheet.write(row, 5, '', wbf['account'])
        #     sheet.write(row, 6, '', wbf['account'])
        #     sheet.write(row, 7, '', wbf['account'])
        #     sheet.write(row, 8, '', wbf['account'])
        #     sheet.write(row, 9, '', wbf['account'])
        #     sheet.write(row, 10, '', wbf['account'])
        #     sheet.write(row, 11, 'Opening', wbf['account'])
        #     sheet.write(row, 12, total_debit, wbf['opening_balance'])
        #     sheet.write(row, 13, total_credit, wbf['opening_balance'])
        #     sheet.write(row, 14, opening_balance, wbf['opening_balance'])
        #     sheet.write(row, 15, '', wbf['opening_balance'])
        #     row += 1

        #     domain = [
        #         ('account_id', '=', account.id),
        #         ('date', '>=', obj.from_date),
        #         ('date', '<=', obj.to_date),
        #         ('move_id.state', '=', 'posted')
        #     ]
        #     account_move_lines = self.env['account.move.line'].search(domain, order='date asc')

        #     # balance = 0
        #     for move_line in account_move_lines:
        #         sheet.write(row, 0, move_line.date, wbf['content_date'])
        #         sheet.write(row, 1, f'{move_line.account_id.code} {move_line.account_id.name}', wbf['content'])
        #         sheet.write(row, 2, move_line.journal_id.code, wbf['content'])
        #         sheet.write(row, 3, move_line.partner_id.name if move_line.partner_id else '', wbf['content'])
        #         sheet.write(row, 4, move_line.ref if move_line.ref else '', wbf['content'])
        #         sheet.write(row, 5, move_line.move_id.name if move_line.move_id else '', wbf['content'])
        #         sheet.write(row, 6, move_line.plantation_location_type_id.name if move_line.plantation_location_type_id else '', wbf['content'])
        #         sheet.write(row, 7, move_line.plantation_varieties_id.name if move_line.plantation_varieties_id else '', wbf['content'])
        #         sheet.write(row, 8, move_line.plantation_location_id.name if move_line.plantation_location_id else '', wbf['content'])
        #         sheet.write(row, 9, move_line.plantation_activity_id.name if move_line.plantation_activity_id else '', wbf['content'])
        #         sheet.write(row, 10, '', wbf['content'])
        #         sheet.write(row, 11, move_line.name if move_line.name else '', wbf['content'])

        #         sheet.write(row, 12, move_line.debit, wbf['content_float'])
        #         sheet.write(row, 13, move_line.credit, wbf['content_float'])

        #         # balance += move_line.debit - move_line.credit
        #         # sheet.write(row, 13, balance, wbf['content_float'])
        #         sheet.write_formula(row, 14, f'=O{row}+M{row+1}-N{row+1}', wbf['content_float'])

        #         sheet.write(row, 15, move_line.amount_currency if move_line.currency_id != move_line.company_id.currency_id else 0, wbf['content_float'])

        #         row += 1
        #     # Menutup looping account_move_lines dengan baris saldo akhir
        #     last_balance_row = row 
        #     sheet.write(row, 0, '', wbf['account'])
        #     sheet.write(row, 1, f'{account.code} {account.name}', wbf['account'])
        #     sheet.write(row, 2, '', wbf['account'])
        #     sheet.write(row, 3, '', wbf['account'])
        #     sheet.write(row, 4, '', wbf['account'])
        #     sheet.write(row, 5, '', wbf['account'])
        #     sheet.write(row, 6, '', wbf['account'])
        #     sheet.write(row, 7, '', wbf['account'])
        #     sheet.write(row, 8, '', wbf['account'])
        #     sheet.write(row, 9, '', wbf['account'])
        #     sheet.write(row, 10, '', wbf['account'])
        #     sheet.write(row, 11, 'Saldo Akhir', wbf['account'])
        #     sheet.write(row, 12, '', wbf['account'])
        #     sheet.write(row, 13, '', wbf['account'])

        #     sheet.write_formula(row, 14, f'=SUM(O{row - len(account_move_lines)}:O{last_balance_row})', wbf['opening_balance'])
        #     sheet.write(row, 15, '', wbf['account'])
        #     row += 1
        
        # # Pengaturan Cetak
        # sheet.set_landscape()
        # sheet.set_paper(9)
        # sheet.repeat_rows(0)
        # sheet.set_print_scale(78)
