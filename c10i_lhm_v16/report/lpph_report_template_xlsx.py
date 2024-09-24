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
            

            locations = []
            for lhm_data in lhm_transaction:
                if lhm_data.location not in locations:
                    locations.append(lhm_data.location)

            location_name = ', '.join([location for location in locations])


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
            worksheet.merge_range(next_row, 6, next_row + 2, 6, "PRODUCT 1", wbf['header'])
            worksheet.set_column(6, 6, 18)
            worksheet.merge_range(next_row, 7, next_row + 2, 7, "SATUAN 1", wbf['header'])
            worksheet.set_column(7, 7, 18)
            worksheet.merge_range(next_row, 8, next_row + 1, 9, "HASIL KERJA", wbf['header'])
            worksheet.write(next_row + 2, 8, "HI", wbf['header'])
            worksheet.set_column(8, 8, 14)
            worksheet.write(next_row + 2, 9, "SHI", wbf['header'])
            worksheet.set_column(9, 9, 14)
            worksheet.merge_range(next_row, 10, next_row + 2, 10, "VARIANCE\n(+/-)", wbf['header'])
            worksheet.set_column(10, 10, 18)
            worksheet.merge_range(next_row, 11, next_row + 2, 11, "PRODUCT 2", wbf['header'])
            worksheet.set_column(11, 11, 18)
            worksheet.merge_range(next_row, 12, next_row + 2, 12, "SATUAN 2", wbf['header'])
            worksheet.set_column(12, 12, 18)
            worksheet.merge_range(next_row, 13, next_row + 1, 14, "HASIL KERJA", wbf['header'])
            worksheet.write(next_row + 2, 13, "HI", wbf['header'])
            worksheet.set_column(13, 13, 14)
            worksheet.write(next_row + 2, 14, "SHI", wbf['header'])
            worksheet.set_column(14, 14, 14)
            worksheet.merge_range(next_row, 15, next_row + 2, 15, "VARIANCE\n(+/-)", wbf['header'])
            worksheet.set_column(15, 15, 18)
            worksheet.merge_range(next_row, 16, next_row, 21, "BIAYA", wbf['header'])
            worksheet.merge_range(next_row + 1, 16, next_row + 1, 18, "HI", wbf['header'])
            worksheet.write(next_row + 2, 16, "HK", wbf['header'])
            worksheet.set_column(16, 16, 16)
            worksheet.write(next_row + 2, 17, "PREMI/LEMBUR", wbf['header'])
            worksheet.set_column(17, 17, 18)
            worksheet.write(next_row + 2, 18, "TOTAL", wbf['header'])
            worksheet.set_column(18, 18, 18)
            worksheet.merge_range(next_row + 1, 19, next_row + 1, 21, "SHI", wbf['header'])
            worksheet.write(next_row + 2, 19, "HK", wbf['header'])
            worksheet.set_column(19, 19, 10)
            worksheet.write(next_row + 2, 20, "PREMI/LEMBUR", wbf['header'])
            worksheet.set_column(20, 20, 18)
            worksheet.write(next_row + 2, 21, "TOTAL", wbf['header'])
            worksheet.set_column(21, 21, 18)
            worksheet.merge_range(next_row, 22, next_row, 29, "PEMAKAIAN MATERIAL", wbf['header'])
            worksheet.merge_range(next_row + 1, 22, next_row + 1, 24, "SKB", wbf['header'])
            worksheet.write(next_row + 2, 22, "NO. PBB", wbf['header'])
            worksheet.set_column(22, 22, 18)
            worksheet.write(next_row + 2, 23, "TANGGAL", wbf['header'])
            worksheet.set_column(23, 23, 18)
            worksheet.write(next_row + 2, 24, "QTY", wbf['header'])
            worksheet.set_column(24, 24, 18)
            worksheet.merge_range(next_row + 1, 25, next_row + 2, 25, "NAMA MATERIAL", wbf['header'])
            worksheet.set_column(25, 25, 40)
            worksheet.merge_range(next_row + 1, 26, next_row + 2, 26, "SATUAN", wbf['header'])
            worksheet.set_column(26, 26, 18)
            worksheet.merge_range(next_row + 1, 27, next_row + 1, 28, "TOTAL", wbf['header'])
            worksheet.write(next_row + 2, 27, "HI", wbf['header'])
            worksheet.set_column(27, 27, 18)
            worksheet.write(next_row + 2, 28, "SHI", wbf['header'])
            worksheet.set_column(28, 28, 18)
            worksheet.merge_range(next_row + 1, 29, next_row + 2, 29, "VARIANCE\n(+/-)", wbf['header'])
            worksheet.set_column(29, 29, 18)


            grouped_lhm = {}

            for line in lhm_transaction.process_line_ids:
                key = line.location_id.type_id
                if key.id not in grouped_lhm:
                    grouped_lhm[key.id] = {
                        'key': key,
                        'progress': [],
                        'subtotal_qty': 0,
                        'total_qty': 0,
                        'nilai': 0,
                        'nilai_1': 0,
                        'subtotal_nilai': 0,
                        'total_nilai': 0,
                        'subtotal_nilai_1': 0,
                        'total_nilai_1': 0,
                    }

                existing_progress = next((progress for progress in grouped_lhm[key.id]['progress'] 
                    if progress['activity_id'] == line.activity_id and progress['location_id'] == line.location_id),None)
    
                if existing_progress:
                    total_material = self.env['lhm.transaction.material.line'].search([
                        ('progress_id', '=', line.id),
                        ('realization', '>', 0)
                    ])
                    grouped_lhm[key.id]['subtotal_qty'] += sum(m.realization for m in total_material)
                    grouped_lhm[key.id]['subtotal_nilai'] += line.nilai
                    grouped_lhm[key.id]['subtotal_nilai_1'] += line.nilai2

                    existing_progress['total_qty'] += material_realization_sum
                    existing_progress['nilai'] += line.nilai
                    existing_progress['nilai2'] += line.nilai2
                else:
                    total_material = self.env['lhm.transaction.material.line'].search([
                        ('progress_id', '=', line.id),
                        ('realization', '>', 0)
                    ])
                    material_realization_sum = sum(m.realization for m in total_material)
                    # grouped_lhm[key.id]['progress'].append(line)
                    grouped_lhm[key.id]['progress'].append({
                        'progress_id': line.id,
                        'name': line.name,
                        'product_id': line.product_id,
                        'uom_id': line.uom_id,
                        'product_id_2': line.product_id_2,
                        'uom2_id': line.uom2_id,
                        'activity_id': line.activity_id,
                        'location_id': line.location_id,
                        'total_qty': material_realization_sum,
                        'nilai': line.nilai,
                        'nilai2': line.nilai2
                    })
                    grouped_lhm[key.id]['subtotal_qty'] += sum(m.realization for m in total_material)
                    grouped_lhm[key.id]['subtotal_nilai'] += line.nilai
                    grouped_lhm[key.id]['subtotal_nilai_1'] += line.nilai2

            grand_total_qty = 0
            grand_total_nilai = 0
            grand_total_qty_nilai_1 = 0
            for key_id, data in grouped_lhm.items():
                total_material = self.env['lhm.transaction.material.line'].search([
                    ('progress_id', 'in', [progress_line['progress_id'] for progress_line in data['progress']]),
                    ('realization', '>', 0)
                ])
                
                material = sum(m.realization for m in total_material)
                grouped_lhm[key_id]['subtotal_qty'] += material
                grand_total_qty += grouped_lhm[key_id]['subtotal_qty']
                grouped_lhm[key_id]['total_qty'] += grand_total_qty
                grand_total_nilai += grouped_lhm[key_id]['subtotal_nilai']
                grouped_lhm[key_id]['total_nilai'] += grand_total_nilai
                grand_total_qty_nilai_1 += grouped_lhm[key_id]['subtotal_nilai_1']
                grouped_lhm[key_id]['total_nilai_1'] += grand_total_qty_nilai_1

            row_data = next_row + 3
            for lhm_data in grouped_lhm.values():
                for line in lhm_data['progress']:

                    get_material = self.env['lhm.transaction.material.line'].search([
                        ('progress_id', '=', line['progress_id']),
                        ('realization', '>', 0)
                    ])

                    worksheet.write(row_data, 0, lhm_data['key'].code, wbf['content'])
                    worksheet.set_column(0, 0, 18)

                    worksheet.write(row_data, 1, line['location_id'].code, wbf['content'])
                    worksheet.set_column(1, 1, 14)

                    worksheet.write(row_data, 2, '-', wbf['content'])
                    worksheet.set_column(2, 2, 14)

                    worksheet.write(row_data, 3, '-', wbf['content'])
                    worksheet.set_column(3, 3, 14)

                    worksheet.write(row_data, 4, line['activity_id'].code if line['activity_id'] else '-', wbf['content'])
                    worksheet.set_column(4, 4, 14)

                    worksheet.write(row_data, 5, line['name'] if line['name'] else '-', wbf['content'])
                    worksheet.set_column(5, 5, 40)

                    worksheet.write(row_data, 6, line['product_id'].name if line['product_id'] else '-', wbf['content'])
                    worksheet.set_column(6, 6, 18)

                    worksheet.write(row_data, 7, line['uom_id'].name if line['uom_id'] else '-', wbf['content'])
                    worksheet.set_column(7, 7, 18)
                    
                    worksheet.write(row_data, 8, line['nilai'] if line['nilai'] else 0.0, wbf['content'])
                    worksheet.set_column(8, 8, 14)

                    worksheet.write(row_data, 9, '-', wbf['content'])
                    worksheet.set_column(9, 9, 14)

                    worksheet.write(row_data, 10, '-', wbf['content'])
                    worksheet.set_column(10, 10, 18)
                    
                    worksheet.write(row_data, 11, line['product_id_2'].name if line['product_id_2'] else '-', wbf['content'])
                    worksheet.set_column(11, 11, 18)

                    worksheet.write(row_data, 12, line['uom2_id'].name if line['uom2_id'].name else '-', wbf['content'])
                    worksheet.set_column(12, 12, 18)
                    
                    worksheet.write(row_data, 13, line['nilai2'] if line['nilai2'] else 0.0, wbf['content'])
                    worksheet.set_column(13, 13, 14)

                    worksheet.write(row_data, 14, '-', wbf['content'])
                    worksheet.set_column(14, 14, 14)

                    worksheet.write(row_data, 15, '-', wbf['content'])
                    worksheet.set_column(15, 15, 18)
                    
                    worksheet.write(row_data, 16, '-', wbf['content'])
                    worksheet.set_column(16, 16, 10)

                    worksheet.write(row_data, 17, '-', wbf['content'])
                    worksheet.set_column(17, 17, 18)

                    worksheet.write(row_data, 18, '-', wbf['content'])
                    worksheet.set_column(18, 18, 18)
                    
                    worksheet.write(row_data, 19, '-', wbf['content'])
                    worksheet.set_column(19, 19, 10)

                    worksheet.write(row_data, 20, '-', wbf['content'])
                    worksheet.set_column(20, 20, 18)

                    worksheet.write(row_data, 21, '-', wbf['content'])
                    worksheet.set_column(21, 21, 18)

                    worksheet.write(row_data, 22, get_material.name if get_material else '-', wbf['content'])
                    worksheet.set_column(22, 22, 18)

                    worksheet.write(row_data, 23, get_material.date.strftime('%d-%m-%Y') if get_material else '-', wbf['content'])
                    worksheet.set_column(23, 23, 18)

                    worksheet.write(row_data, 24, get_material.realization if get_material else '-', wbf['content'])
                    worksheet.set_column(24, 24, 18)

                    worksheet.write(row_data, 25, get_material.product_id.name if get_material else '-', wbf['content'])
                    worksheet.set_column(25, 25, 40)

                    worksheet.write(row_data, 26, get_material.product_uom_id.name if get_material else '-', wbf['content'])
                    worksheet.set_column(26, 26, 18)

                    worksheet.write(row_data, 27, '-', wbf['content'])
                    worksheet.set_column(27, 27, 18)

                    worksheet.write(row_data, 28, '-', wbf['content'])
                    worksheet.set_column(28, 28, 18)

                    worksheet.write(row_data, 29, '-', wbf['content'])
                    worksheet.set_column(29, 29, 18)

                    row_data += 1

                worksheet.write(row_data, 0, "Subtotal", wbf['total'])
                worksheet.write(row_data, 1, "", wbf['total'])
                worksheet.write(row_data, 2, "", wbf['total'])
                worksheet.write(row_data, 3, "", wbf['total'])
                worksheet.write(row_data, 4, "", wbf['total'])
                worksheet.write(row_data, 5, "", wbf['total'])
                worksheet.write(row_data, 6, "", wbf['total'])
                worksheet.write(row_data, 7, "", wbf['total'])
                worksheet.write(row_data, 8, lhm_data['subtotal_nilai'], wbf['total'])
                worksheet.write(row_data, 9, "", wbf['total'])
                worksheet.write(row_data, 10, "", wbf['total'])
                worksheet.write(row_data, 11, "", wbf['total'])
                worksheet.write(row_data, 12, "", wbf['total'])
                worksheet.write(row_data, 13, lhm_data['subtotal_nilai_1'], wbf['total'])
                worksheet.write(row_data, 14, "", wbf['total'])
                worksheet.write(row_data, 15, "", wbf['total'])
                worksheet.write(row_data, 16, "", wbf['total'])
                worksheet.write(row_data, 17, "", wbf['total'])
                worksheet.write(row_data, 18, "", wbf['total'])
                worksheet.write(row_data, 19, "", wbf['total'])
                worksheet.write(row_data, 20, "", wbf['total'])
                worksheet.write(row_data, 21, "", wbf['total'])
                worksheet.write(row_data, 22, "", wbf['total'])
                worksheet.write(row_data, 23, "", wbf['total'])
                worksheet.write(row_data, 24, lhm_data['subtotal_qty'], wbf['total'])
                worksheet.write(row_data, 25, "", wbf['total'])
                worksheet.write(row_data, 26, "", wbf['total'])
                worksheet.write(row_data, 27, "", wbf['total'])
                worksheet.write(row_data, 28, "", wbf['total'])
                worksheet.write(row_data, 29, "", wbf['total'])

                row_data += 1

                worksheet.write(row_data, 0, "Grand Total", wbf['total'])
                worksheet.write(row_data, 1, "", wbf['total'])
                worksheet.write(row_data, 2, "", wbf['total'])
                worksheet.write(row_data, 3, "", wbf['total'])
                worksheet.write(row_data, 4, "", wbf['total'])
                worksheet.write(row_data, 5, "", wbf['total'])
                worksheet.write(row_data, 6, "", wbf['total'])
                worksheet.write(row_data, 7, "", wbf['total'])
                worksheet.write(row_data, 8, lhm_data['total_nilai'], wbf['total'])
                worksheet.write(row_data, 9, "", wbf['total'])
                worksheet.write(row_data, 10, "", wbf['total'])
                worksheet.write(row_data, 11, "", wbf['total'])
                worksheet.write(row_data, 12, "", wbf['total'])
                worksheet.write(row_data, 13, lhm_data['total_nilai_1'], wbf['total'])
                worksheet.write(row_data, 14, "", wbf['total'])
                worksheet.write(row_data, 15, "", wbf['total'])
                worksheet.write(row_data, 16, "", wbf['total'])
                worksheet.write(row_data, 17, "", wbf['total'])
                worksheet.write(row_data, 18, "", wbf['total'])
                worksheet.write(row_data, 19, "", wbf['total'])
                worksheet.write(row_data, 20, "", wbf['total'])
                worksheet.write(row_data, 21, "", wbf['total'])
                worksheet.write(row_data, 22, "", wbf['total'])
                worksheet.write(row_data, 23, "", wbf['total'])
                worksheet.write(row_data, 24, lhm_data['total_qty'], wbf['total'])
                worksheet.write(row_data, 25, "", wbf['total'])
                worksheet.write(row_data, 26, "", wbf['total'])
                worksheet.write(row_data, 27, "", wbf['total'])
                worksheet.write(row_data, 28, "", wbf['total'])
                worksheet.write(row_data, 29, "", wbf['total'])