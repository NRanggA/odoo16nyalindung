from odoo import fields, models, api

class ReportLpphExcel(models.AbstractModel):
    _name = 'report.c10i_lhm_v16.report_lpph_excel'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'LPPH Excel'

    wbf = {}

    def add_workbook_format(self, workbook):
        self.wbf['title'] = workbook.add_format({'bold': 1, 'align': 'left'})
        self.wbf['title'].set_align('vcenter')
        self.wbf['header'] = workbook.add_format({'bold': 1, 'align': 'center', 'font_color': '#000000'})
        self.wbf['header'].set_border()
        self.wbf['header'].set_text_wrap()
        self.wbf['header'].set_align('vcenter')
        self.wbf['header'].set_font_size(10)

        self.wbf['date'] = workbook.add_format({'align': 'center', 'num_format': 'mm/dd/yyyy'})
        self.wbf['date'].set_border()
        self.wbf['date'].set_text_wrap()
        self.wbf['date'].set_align('vcenter')
        self.wbf['date'].set_font_size(8)

        self.wbf['content'] = workbook.add_format({'align': 'center'})
        self.wbf['content'].set_border()
        self.wbf['content'].set_text_wrap()
        self.wbf['content'].set_align('vcenter')
        self.wbf['content'].set_font_size(8)
        
        self.wbf['total'] = workbook.add_format({'bold': 1, 'align': 'center', 'bg_color': '#F5F4F4'})
        self.wbf['total'].set_border()
        self.wbf['total'].set_text_wrap()
        self.wbf['total'].set_align('vcenter')
        self.wbf['total'].set_font_size(8)

        return workbook

    def generate_xlsx_report(self, workbook, data, objects):
        workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet("LPPH Report")
        wbf = self.wbf

        worksheet.set_column(0, 12, 15)

        for o in objects:
            # Header
            date_from = o.date_start.strftime('%d-%m-%Y')
            date_to = o.date_end.strftime('%d-%m-%Y')
            date = date_from if date_from == date_to else f"{(date_from) + ' s/d ' + (date_to)}"

            lhm_transaction = self.env['lhm.transaction'].search([
                                ('date','>=',o.date_start),
                                ('date','<=',o.date_end),
                                ('state','=','done')
                            ])
            

            location = []
            # for lhm_data in lhm_transaction:                
            #     lhm_key = lhm_data.process_line_ids.mapped('location_id')
            #     for loc in lhm_key:
            #         if loc.id not in [l.id for l in location]:
            #             location.append(loc)
            
            for lhm_data in lhm_transaction:
                location.append(lhm_data.location)

            location_name = ', '.join([loc for loc in location])


            row = 0
            worksheet.write(row, 0, (o.company_id.name), wbf['title'])
            worksheet.write(row + 1, 0, "LAPORAN PROGRES PEKERJAAN HARIAN - DETAIL MATERIAL", wbf['title'])
            worksheet.write(row + 2, 0, "AFDELING BAGIAN", wbf['title'])
            worksheet.write(row + 2, 1, ": %s" %(location_name), wbf['title'])
            worksheet.write(row + 3, 0, "TYPE PEKERJA", wbf['title'])
            worksheet.write(row + 3, 1, ": %s" %(o.type.upper()), wbf['title'])
            worksheet.write(row + 4, 0, "TANGGAL", wbf['title'])
            worksheet.write(row + 4, 1, ": %s" %(date), wbf['title'])
            worksheet.set_row(row, 18)
            worksheet.set_row(row + 1, 18)
            worksheet.set_row(row + 2, 18)
            worksheet.set_column(row + 2, 0, 20)
            worksheet.set_row(row + 3, 18)
            worksheet.set_row(row + 4, 18)

            next_row = row + 5
            worksheet.merge_range(next_row, 0, next_row + 2, 0, "TYPE", wbf['header'])
            worksheet.set_column(0, 0, 18)
            worksheet.merge_range(next_row, 1, next_row + 1, 3, "LOKASI", wbf['header'])
            worksheet.write(next_row + 2, 1, "KODE", wbf['header'])
            worksheet.set_column(1, 1, 14)
            worksheet.write(next_row + 2, 2, "SATUAN", wbf['header'])
            worksheet.set_column(2, 2, 14)
            worksheet.write(next_row + 2, 3, "QTY", wbf['header'])
            worksheet.set_column(3, 3, 14)
            worksheet.merge_range(next_row, 4, next_row + 1, 5, "KEGIATAN", wbf['header'])
            worksheet.write(next_row + 2, 4, "COA", wbf['header'])
            worksheet.set_column(4, 4, 14)
            worksheet.write(next_row + 2, 5, "DESKRIPSI", wbf['header'])
            worksheet.set_column(5, 5, 40)
            worksheet.merge_range(next_row, 6, next_row + 2, 6, "SATUAN", wbf['header'])
            worksheet.set_column(6, 6, 18)
            worksheet.merge_range(next_row, 7, next_row + 1, 8, "HASIL KERJA", wbf['header'])
            worksheet.write(next_row + 2, 7, "HI", wbf['header'])
            worksheet.set_column(7, 7, 14)
            worksheet.write(next_row + 2, 8, "SHI", wbf['header'])
            worksheet.set_column(8, 8, 14)
            worksheet.merge_range(next_row, 9, next_row + 2, 9, "VARIANCE\n(+/-)", wbf['header'])
            worksheet.set_column(9, 9, 18)
            worksheet.merge_range(next_row, 10, next_row, 15, "BIAYA", wbf['header'])
            worksheet.merge_range(next_row + 1, 10, next_row + 1, 12, "HI", wbf['header'])
            worksheet.write(next_row + 2, 10, "HK", wbf['header'])
            worksheet.set_column(10, 10, 10)
            worksheet.write(next_row + 2, 11, "PREMI/LEMBUR", wbf['header'])
            worksheet.set_column(11, 11, 18)
            worksheet.write(next_row + 2, 12, "TOTAL", wbf['header'])
            worksheet.set_column(12, 12, 18)
            worksheet.merge_range(next_row + 1, 13, next_row + 1, 15, "SHI", wbf['header'])
            worksheet.write(next_row + 2, 13, "HK", wbf['header'])
            worksheet.set_column(13, 13, 10)
            worksheet.write(next_row + 2, 14, "PREMI/LEMBUR", wbf['header'])
            worksheet.set_column(14, 14, 18)
            worksheet.write(next_row + 2, 15, "TOTAL", wbf['header'])
            worksheet.set_column(15, 15, 18)
            worksheet.merge_range(next_row, 16, next_row, 23, "PEMAKAIAN MATERIAL", wbf['header'])
            worksheet.merge_range(next_row + 1, 16, next_row + 1, 18, "SKB", wbf['header'])
            worksheet.write(next_row + 2, 16, "NO. PBB", wbf['header'])
            worksheet.set_column(16, 16, 18)
            worksheet.write(next_row + 2, 17, "TANGGAL", wbf['header'])
            worksheet.set_column(17, 17, 18)
            worksheet.write(next_row + 2, 18, "QTY", wbf['header'])
            worksheet.set_column(18, 18, 18)
            worksheet.merge_range(next_row + 1, 19, next_row + 2, 19, "NAMA MATERIAL", wbf['header'])
            worksheet.set_column(19, 19, 40)
            worksheet.merge_range(next_row + 1, 20, next_row + 2, 20, "SATUAN", wbf['header'])
            worksheet.set_column(20, 20, 18)
            worksheet.merge_range(next_row + 1, 21, next_row + 1, 22, "TOTAL", wbf['header'])
            worksheet.write(next_row + 2, 21, "HI", wbf['header'])
            worksheet.set_column(21, 21, 18)
            worksheet.write(next_row + 2, 22, "SHI", wbf['header'])
            worksheet.set_column(22, 22, 18)
            worksheet.merge_range(next_row + 1, 23, next_row + 2, 23, "VARIANCE\n(+/-)", wbf['header'])
            worksheet.set_column(23, 23, 18)


            grouped_lhm = {}

            for line in lhm_transaction.process_line_ids:
                key = line.location_id.type_id
                if key.id not in grouped_lhm:
                    grouped_lhm[key.id] = {
                        'key': key,
                        'progress': [],
                        'total_qty': 0,
                    }
                grouped_lhm[key.id]['progress'].append(line)
                # grouped_lhm[key.id]['total_qty'] += line.qty

            row_data = next_row + 3
            for lhm_data in grouped_lhm.values():
                for line in lhm_data['progress']:
                    worksheet.write(row_data, 0, lhm_data['key'].code, wbf['content'])
                    worksheet.set_column(0, 0, 18)

                    worksheet.write(row_data, 1, line.location_id.code, wbf['content'])
                    worksheet.set_column(1, 1, 14)

                    worksheet.write(row_data, 2, line.uom_id.name if line.uom_id else '-', wbf['content'])
                    worksheet.set_column(2, 2, 14)

                    worksheet.write(row_data, 3, line.nilai if line.nilai else '-', wbf['content'])
                    worksheet.set_column(3, 3, 14)

                    worksheet.write(row_data, 4, "COA", wbf['content'])
                    worksheet.set_column(4, 4, 14)

                    worksheet.write(row_data, 5, line.name if line.name else '-', wbf['content'])
                    worksheet.set_column(5, 5, 40)

                    worksheet.write(row_data, 6, "SATUAN", wbf['content'])
                    worksheet.set_column(6, 6, 18)
                    
                    worksheet.write(row_data, 7, "HI", wbf['content'])
                    worksheet.set_column(7, 7, 14)

                    worksheet.write(row_data, 8, "SHI", wbf['content'])
                    worksheet.set_column(8, 8, 14)

                    worksheet.write(row_data, 9, "VARIANCE\n(+/-)", wbf['content'])
                    worksheet.set_column(9, 9, 18)
                    
                    worksheet.write(row_data, 10, "HK", wbf['content'])
                    worksheet.set_column(10, 10, 10)

                    worksheet.write(row_data, 11, "PREMI/LEMBUR", wbf['content'])
                    worksheet.set_column(11, 11, 18)

                    worksheet.write(row_data, 12, "TOTAL", wbf['content'])
                    worksheet.set_column(12, 12, 18)
                    
                    worksheet.write(row_data, 13, "HK", wbf['content'])
                    worksheet.set_column(13, 13, 10)

                    worksheet.write(row_data, 14, "PREMI/LEMBUR", wbf['content'])
                    worksheet.set_column(14, 14, 18)

                    worksheet.write(row_data, 15, "TOTAL", wbf['content'])
                    worksheet.set_column(15, 15, 18)

                    worksheet.write(row_data, 16, "NO. PBB", wbf['content'])
                    worksheet.set_column(16, 16, 18)

                    worksheet.write(row_data, 17, "TANGGAL", wbf['content'])
                    worksheet.set_column(17, 17, 18)

                    worksheet.write(row_data, 18, "QTY", wbf['content'])
                    worksheet.set_column(18, 18, 18)

                    worksheet.write(row_data, 19, "NAMA MATERIAL", wbf['content'])
                    worksheet.set_column(19, 19, 40)

                    worksheet.write(row_data, 20, "SATUAN", wbf['content'])
                    worksheet.set_column(20, 20, 18)

                    worksheet.write(row_data, 21, "HI", wbf['content'])
                    worksheet.set_column(21, 21, 18)

                    worksheet.write(row_data, 22, "SHI", wbf['content'])
                    worksheet.set_column(22, 22, 18)

                    worksheet.write(row_data, 23, "VARIANCE\n(+/-)", wbf['content'])
                    worksheet.set_column(23, 23, 18)

                    row_data += 1

                worksheet.write(row_data, 0, "Subtotal ", wbf['total'])
                # worksheet.merge_range(row_data, 1, row_data, 4, "", wbf['subtotal'])  # Merge cells for subtotal
                # worksheet.write(row_data, 5, sum(line.qty for line in lhm_data['progress']), wbf['subtotal'])  # Total QTY

                row_data += 1