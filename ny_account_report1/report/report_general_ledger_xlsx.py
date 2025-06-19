from odoo import models
from pytz import timezone, UTC
class ReportStockMutation(models.AbstractModel):
    _name = 'report.ny_account_report1.general_ledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report General ledger Excell"

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
            SELECT 
                l.account_id AS account_id,
                COALESCE(SUM(l.debit), 0) AS total_debit,
                COALESCE(SUM(l.credit), 0) AS total_credit
            FROM 
                account_move_line l
            WHERE 
                l.parent_state = 'posted'
                AND l.date < %(date_from)s
                AND l.account_id = %(account_id)s
            GROUP BY l.account_id;
        """
        return query

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        from_date = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
        to_date = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''

        sheet = workbook.add_worksheet("General Ledger")
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 35)
        sheet.set_column('C:C', 10)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 25)
        sheet.set_column('K:K', 25)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 20)
        sheet.set_column('P:P', 20)

        row = 0

        # Periode Header
        sheet.write(row, 0, 'Periode:', wbf['title_doc'])
        sheet.write(row, 1, f'{from_date} s/d {to_date}', wbf['title_sec'])
        row += 2

        # Header Kolom
        headers = [
            "Date", "Account", "JRNL", "Partner", "Ref", "Move", "Tipe Lokasi","ORG",
            "Lokasi", "Activity", "Analytic Account", "Entry Label",
            "Debit", "Credit", "Cumm. Balance", "Currency", "Matching"
        ]
        for col, header in enumerate(headers):
            sheet.write(row, col, header, wbf['header'])
        row += 1

        # Iterasi Setiap Akun
        accounts = obj.account_ids if obj.account_ids else self.env['account.account'].search([])
        for account in accounts:
            domain = [
                ('account_id', '=', account.id),
                ('date', '>=', obj.from_date),
                ('date', '<=', obj.to_date),
                # ('parent_state', '=', obj.type_state)
            ]
            if obj.type_state == 'posted':
                domain.append(('parent_state', '=', 'posted'))
            elif obj.type_state == 'all_entries':
                domain.append(('parent_state', '!=', 'cancel'))

            # kalau is_transaction aktif, cari ambil akun yang memiliki transaksi
            if obj.is_transaction:
                if not self.env['account.move.line'].search_count(domain):
                    continue

            query = self.get_query()
            params = {
                'account_id': account.id,
                'date_from': obj.from_date.strftime('%Y-%m-%d 00:00:00'),
            }

            self.env.cr.execute(query, params)
            account_move = self.env.cr.dictfetchone()

            account_type = account.account_type
            # if account_type in ['bank', 'cash']:
            if account_type == 'asset_cash' :
                order = 'date asc, debit desc, credit desc'
            else:
                order = 'date asc, name asc'

            # Hitung Saldo Awal
            if account_move:
                total_debit = account_move['total_debit']
                total_credit = account_move['total_credit']
            else:
                total_debit = 0.0
                total_credit = 0.0

            opening_balance = total_debit - total_credit

            # Opening
            sheet.write(row, 0, '', wbf['account'])
            sheet.write(row, 1, f'{account.code} {account.name}', wbf['account'])
            sheet.write(row, 2, '', wbf['account'])
            sheet.write(row, 3, '', wbf['account'])
            sheet.write(row, 4, '', wbf['account'])
            sheet.write(row, 5, '', wbf['account'])
            sheet.write(row, 6, '', wbf['account'])
            sheet.write(row, 7, '', wbf['account'])
            sheet.write(row, 8, '', wbf['account'])
            sheet.write(row, 9, '', wbf['account'])
            sheet.write(row, 10, '', wbf['account'])
            sheet.write(row, 11, 'Opening', wbf['account'])
            sheet.write(row, 12, total_debit, wbf['opening_balance'])
            sheet.write(row, 13, total_credit, wbf['opening_balance'])
            sheet.write(row, 14, opening_balance, wbf['opening_balance'])
            sheet.write(row, 15, '', wbf['opening_balance'])
            sheet.write(row, 16, '', wbf['opening_balance'])
            row += 1

            account_move_lines = self.env['account.move.line'].search(domain, order=order)
            # balance = 0
            for move_line in account_move_lines:
                sheet.write(row, 0, move_line.date, wbf['content_date'])
                sheet.write(row, 1, f'{move_line.account_id.code} {move_line.account_id.name}', wbf['content'])
                sheet.write(row, 2, move_line.journal_id.code, wbf['content'])
                sheet.write(row, 3, move_line.partner_id.name if move_line.partner_id else '', wbf['content'])
                sheet.write(row, 4, move_line.ref if move_line.ref else '', wbf['content'])
                sheet.write(row, 5, move_line.move_id.name if move_line.move_id else '', wbf['content'])
                sheet.write(row, 6, move_line.plantation_location_type_id.name if move_line.plantation_location_type_id else '', wbf['content'])
                sheet.write(row, 7, move_line.plantation_varieties_id.name if move_line.plantation_varieties_id else '', wbf['content'])
                sheet.write(row, 8, move_line.plantation_location_id.name if move_line.plantation_location_id else '', wbf['content'])
                sheet.write(row, 9, move_line.plantation_activity_id.name if move_line.plantation_activity_id else '', wbf['content'])
                sheet.write(row, 10, '', wbf['content'])
                sheet.write(row, 11, move_line.name if move_line.name else '', wbf['content'])

                sheet.write(row, 12, move_line.debit, wbf['content_float'])
                sheet.write(row, 13, move_line.credit, wbf['content_float'])

                # balance += move_line.debit - move_line.credit
                # sheet.write(row, 13, balance, wbf['content_float'])
                sheet.write_formula(row, 14, f'=O{row}+M{row+1}-N{row+1}', wbf['content_float'])

                sheet.write(row, 15, move_line.amount_currency if move_line.currency_id != move_line.company_id.currency_id else 0, wbf['content_float'])
                sheet.write(row, 16, move_line.matching_number or '', wbf['content'])

                row += 1
            # Menutup looping account_move_lines dengan baris saldo akhir
            last_balance_row = row 
            sheet.write(row, 0, '', wbf['account'])
            sheet.write(row, 1, f'{account.code} {account.name}', wbf['account'])
            sheet.write(row, 2, '', wbf['account'])
            sheet.write(row, 3, '', wbf['account'])
            sheet.write(row, 4, '', wbf['account'])
            sheet.write(row, 5, '', wbf['account'])
            sheet.write(row, 6, '', wbf['account'])
            sheet.write(row, 7, '', wbf['account'])
            sheet.write(row, 8, '', wbf['account'])
            sheet.write(row, 9, '', wbf['account'])
            sheet.write(row, 10, '', wbf['account'])
            sheet.write(row, 11, 'Saldo Akhir', wbf['account'])
            sheet.write(row, 12, '', wbf['account'])
            sheet.write(row, 13, '', wbf['account'])

            # sheet.write_formula(row, 14, f'=SUM(O{row - len(account_move_lines)}:O{last_balance_row})', wbf['opening_balance'])
            sheet.write_formula(row, 14, f'=O{row}+M{row+1}-N{row+1}', wbf['opening_balance'])
            sheet.write(row, 15, '', wbf['account'])
            sheet.write(row, 16, '', wbf['account'])
            row += 1
        
        # Pengaturan Cetak
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.repeat_rows(0)
        sheet.set_print_scale(78)
    

    # def generate_xlsx_report(self, workbook, datas, obj):
    #     workbook = self.add_workbook_format(workbook)
    #     wbf = self.wbf

    #     from_date = obj.from_date.strftime('%d-%m-%Y') if obj.from_date else ''
    #     to_date = obj.to_date.strftime('%d-%m-%Y') if obj.to_date else ''

    #     sheet = workbook.add_worksheet("General Ledger")
    #     sheet.set_column('A:A', 15)
    #     sheet.set_column('B:B', 35)
    #     sheet.set_column('C:C', 10)
    #     sheet.set_column('D:D', 40)
    #     sheet.set_column('E:E', 20)
    #     sheet.set_column('F:F', 25)
    #     sheet.set_column('G:G', 20)
    #     sheet.set_column('H:H', 20)
    #     sheet.set_column('I:I', 20)
    #     sheet.set_column('J:J', 25)
    #     sheet.set_column('K:K', 25)
    #     sheet.set_column('L:L', 20)
    #     sheet.set_column('M:M', 20)
    #     sheet.set_column('N:N', 20)
    #     sheet.set_column('O:O', 20)

    #     row = 0

    #     # Periode Header
    #     sheet.write(row, 0, 'Periode:', wbf['title_doc'])
    #     sheet.write(row, 1, f'{from_date} s/d {to_date}', wbf['title_sec'])
    #     row += 2

    #     # Header Kolom
    #     headers = [
    #         "Date", "Account", "JRNL", "Partner", "Ref", "Move", "Tipe Lokasi","ORG",
    #         "Lokasi", "Activity", "Analytic Account", "Entry Label",
    #         "Debit", "Credit", "Cumm. Balance", "Currency"
    #     ]
    #     for col, header in enumerate(headers):
    #         sheet.write(row, col, header, wbf['header'])
    #     row += 1

    #     # Iterasi Setiap Akun
    #     accounts = obj.account_ids if obj.account_ids else self.env['account.account'].search([])
    #     for account in accounts:
    #         query = self.get_query()

    #         params = {
    #             'account_id': account.id,
    #             'date_from': obj.from_date.strftime('%Y-%m-%d 00:00:00'),
    #         }

    #         self.env.cr.execute(query, params)
    #         account_move = self.env.cr.dictfetchone()

    #         # Hitung Saldo Awal
    #         if account_move:
    #             total_debit = account_move['total_debit']
    #             total_credit = account_move['total_credit']
    #         else:
    #             total_debit = 0.0
    #             total_credit = 0.0

    #         opening_balance = total_debit - total_credit

    #         # Opening
    #         sheet.write(row, 0, '', wbf['account'])
    #         sheet.write(row, 1, f'{account.code} {account.name}', wbf['account'])
    #         sheet.write(row, 2, '', wbf['account'])
    #         sheet.write(row, 3, '', wbf['account'])
    #         sheet.write(row, 4, '', wbf['account'])
    #         sheet.write(row, 5, '', wbf['account'])
    #         sheet.write(row, 6, '', wbf['account'])
    #         sheet.write(row, 7, '', wbf['account'])
    #         sheet.write(row, 8, '', wbf['account'])
    #         sheet.write(row, 9, '', wbf['account'])
    #         sheet.write(row, 10, '', wbf['account'])
    #         sheet.write(row, 11, 'Opening', wbf['account'])
    #         sheet.write(row, 12, total_debit, wbf['opening_balance'])
    #         sheet.write(row, 13, total_credit, wbf['opening_balance'])
    #         sheet.write(row, 14, opening_balance, wbf['opening_balance'])
    #         sheet.write(row, 15, '', wbf['opening_balance'])
    #         row += 1

    #         domain = [
    #             ('account_id', '=', account.id),
    #             ('date', '>=', obj.from_date),
    #             ('date', '<=', obj.to_date),
    #             ('move_id.state', '=', 'posted')
    #         ]

    #         account_type = account.account_type
    #         if account_type in ['bank', 'cash']:
    #             order = 'date asc, debit desc, credit desc'
    #         else:
    #             order = 'date asc, name asc'

    #         account_move_lines = self.env['account.move.line'].search(domain, order=order)

    #         # balance = 0
    #         for move_line in account_move_lines:
    #             sheet.write(row, 0, move_line.date, wbf['content_date'])
    #             sheet.write(row, 1, f'{move_line.account_id.code} {move_line.account_id.name}', wbf['content'])
    #             sheet.write(row, 2, move_line.journal_id.code, wbf['content'])
    #             sheet.write(row, 3, move_line.partner_id.name if move_line.partner_id else '', wbf['content'])
    #             sheet.write(row, 4, move_line.ref if move_line.ref else '', wbf['content'])
    #             sheet.write(row, 5, move_line.move_id.name if move_line.move_id else '', wbf['content'])
    #             sheet.write(row, 6, move_line.plantation_location_type_id.name if move_line.plantation_location_type_id else '', wbf['content'])
    #             sheet.write(row, 7, move_line.plantation_varieties_id.name if move_line.plantation_varieties_id else '', wbf['content'])
    #             sheet.write(row, 8, move_line.plantation_location_id.name if move_line.plantation_location_id else '', wbf['content'])
    #             sheet.write(row, 9, move_line.plantation_activity_id.name if move_line.plantation_activity_id else '', wbf['content'])
    #             sheet.write(row, 10, '', wbf['content'])
    #             sheet.write(row, 11, move_line.name if move_line.name else '', wbf['content'])

    #             sheet.write(row, 12, move_line.debit, wbf['content_float'])
    #             sheet.write(row, 13, move_line.credit, wbf['content_float'])

    #             # balance += move_line.debit - move_line.credit
    #             # sheet.write(row, 13, balance, wbf['content_float'])
    #             sheet.write_formula(row, 14, f'=O{row}+M{row+1}-N{row+1}', wbf['content_float'])

    #             sheet.write(row, 15, move_line.amount_currency if move_line.currency_id != move_line.company_id.currency_id else 0, wbf['content_float'])

    #             row += 1
    #         # Menutup looping account_move_lines dengan baris saldo akhir
    #         last_balance_row = row 
    #         sheet.write(row, 0, '', wbf['account'])
    #         sheet.write(row, 1, f'{account.code} {account.name}', wbf['account'])
    #         sheet.write(row, 2, '', wbf['account'])
    #         sheet.write(row, 3, '', wbf['account'])
    #         sheet.write(row, 4, '', wbf['account'])
    #         sheet.write(row, 5, '', wbf['account'])
    #         sheet.write(row, 6, '', wbf['account'])
    #         sheet.write(row, 7, '', wbf['account'])
    #         sheet.write(row, 8, '', wbf['account'])
    #         sheet.write(row, 9, '', wbf['account'])
    #         sheet.write(row, 10, '', wbf['account'])
    #         sheet.write(row, 11, 'Saldo Akhir', wbf['account'])
    #         sheet.write(row, 12, '', wbf['account'])
    #         sheet.write(row, 13, '', wbf['account'])

    #         # sheet.write_formula(row, 14, f'=SUM(O{row - len(account_move_lines)}:O{last_balance_row})', wbf['opening_balance'])
    #         sheet.write_formula(row, 14, f'=O{row}+M{row+1}-N{row+1}', wbf['opening_balance'])
    #         sheet.write(row, 15, '', wbf['account'])
    #         sheet.write(row, 15, '', wbf['account'])
    #         row += 1
        
    #     # Pengaturan Cetak
    #     sheet.set_landscape()
    #     sheet.set_paper(9)
    #     sheet.repeat_rows(0)
    #     sheet.set_print_scale(78)
