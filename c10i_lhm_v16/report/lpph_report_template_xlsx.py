from odoo import fields, models, api
from datetime import datetime

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
        
        self.wbf['number_content'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        self.wbf['number_content'].set_border()
        self.wbf['number_content'].set_text_wrap()
        self.wbf['number_content'].set_align('vcenter')
        self.wbf['number_content'].set_font_size(8)
        
        self.wbf['number_total'] = workbook.add_format({'bold': 1, 'align': 'right', 'bg_color': '#F5F4F4', 'num_format': '#,##0.00'})
        self.wbf['number_total'].set_border()
        self.wbf['number_total'].set_text_wrap()
        self.wbf['number_total'].set_align('vcenter')
        self.wbf['number_total'].set_font_size(8)

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
                                ('date','=',o.date_start),
                                # ('date','<=',o.date_end),
                                ('state','=','done')
                            ])
            
            shi_month = o.date_start.month
            shi_year = o.date_start.year
            shi_date_from = datetime(shi_year, shi_month, 1)

            shi_lhm_transaction = self.env['lhm.transaction'].search([
                                ('date','>=',shi_date_from),
                                ('date','<=',o.date_start),
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
                        'subtotal_realization': 0.0,
                        'subtotal_real_stock_qty': 0.0,
                        'subtotal_nilai': 0.0,
                        'subtotal_nilai_1': 0.0,
                        'subtotal_workday': 0.0,
                        'subtotal_premi': 0.0,
                        'shi_subtotal_realization': 0.0,
                        'shi_subtotal_nilai': 0.0,
                        'shi_subtotal_nilai_1': 0.0,
                        'shi_subtotal_workday': 0.0,
                        'shi_subtotal_premi': 0.0,
                        'realization': 0.0,
                        'real_stock_qty': 0.0,
                        'shi_realization': 0.0,
                    }

    
                materials = self.env['lhm.transaction.material.line'].search([
                    ('progress_id', '=', line.id),
                    ('realization', '>', 0)
                ])
                material_realization_sum = sum(m.realization for m in materials)
                real_stock_qty_sum = sum(m.real_stock_qty for m in materials)
                
                existing_progress = next((progress for progress in grouped_lhm[key.id]['progress'] 
                    if progress['activity_id'] == line.activity_id and progress['location_id'] == line.location_id),None)

                if existing_progress:
                    existing_progress['realization'] += material_realization_sum
                    existing_progress['real_stock_qty'] += real_stock_qty_sum
                    existing_progress['nilai'] += line.nilai
                    existing_progress['nilai2'] += line.nilai2
                    existing_progress['work_day'] += line.work_day
                    existing_progress['premi'] += line.premi
                else:
                    grouped_lhm[key.id]['progress'].append({
                        'progress_id': line.id,
                        'name': line.name,
                        'product_id': line.product_id,
                        'uom_id': line.uom_id,
                        'product_id_2': line.product_id_2,
                        'uom2_id': line.uom2_id,
                        'activity_id': line.activity_id,
                        'location_id': line.location_id,
                        'work_day': line.work_day,
                        'premi': line.premi,
                        'realization': material_realization_sum,                        
                        'real_stock_qty': real_stock_qty_sum,
                        'nilai': line.nilai,
                        'nilai2': line.nilai2,
                    })
                    grouped_lhm[key.id]['subtotal_realization'] += material_realization_sum
                    grouped_lhm[key.id]['subtotal_real_stock_qty'] += real_stock_qty_sum
                    grouped_lhm[key.id]['subtotal_nilai'] += line.nilai
                    grouped_lhm[key.id]['subtotal_nilai_1'] += line.nilai2
                    grouped_lhm[key.id]['subtotal_workday'] += line.work_day
                    grouped_lhm[key.id]['subtotal_premi'] += line.premi

            if lhm_transaction:
                for line in shi_lhm_transaction.process_line_ids:
                    key = line.location_id.type_id

                    if key.id not in grouped_lhm:
                        grouped_lhm[key.id] = {
                            'key': key,
                            'progress': [],
                            'subtotal_realization': 0.0,
                            'realization': 0.0,
                            'subtotal_real_stock_qty': 0.0,
                            'real_stock_qty': 0.0,
                            'nilai': 0.0,
                            'nilai_1': 0.0,
                            'subtotal_nilai': 0.0,
                            'subtotal_nilai_1': 0.0,
                            'subtotal_workday': 0.0,
                            'subtotal_premi': 0.0,
                            'shi_subtotal_realization': 0.0,
                            'shi_realization': 0.0,
                            'shi_nilai': 0.0,
                            'shi_nilai_1': 0.0,
                            'shi_subtotal_nilai': 0.0,
                            'shi_subtotal_nilai_1': 0.0,
                            'shi_subtotal_workday': 0.0,
                            'shi_subtotal_premi': 0.0,
                        }
                    
                    materials = self.env['lhm.transaction.material.line'].search([
                            ('progress_id', '=', line.id),
                            ('realization', '>', 0)
                        ])
                    material_realization_sum = sum(m.realization for m in materials)
                    real_stock_qty_sum = sum(m.real_stock_qty for m in materials)
                    
                    existing_progress = next((progress for progress in grouped_lhm[key.id]['progress'] 
                        if progress['activity_id'] == line.activity_id and progress['location_id'] == line.location_id),None)
        
                    if existing_progress:
                        existing_progress['shi_realization'] = existing_progress.get('shi_realization', 0.0) + material_realization_sum
                        existing_progress['shi_nilai'] = existing_progress.get('shi_nilai', 0.0) + line.nilai
                        existing_progress['shi_nilai_1'] = existing_progress.get('shi_nilai_1', 0.0) + line.nilai2
                        existing_progress['shi_work_day'] = existing_progress.get('shi_work_day', 0.0) + line.work_day
                        existing_progress['shi_premi'] = existing_progress.get('shi_premi', 0.0) + line.premi
                    else:
                        grouped_lhm[key.id]['progress'].append({
                            'progress_id': line.id,
                            'name': line.name,
                            'product_id': line.product_id,
                            'uom_id': line.uom_id,
                            'product_id_2': line.product_id_2,
                            'uom2_id': line.uom2_id,
                            'activity_id': line.activity_id,
                            'location_id': line.location_id,
                            'work_day': line.work_day,
                            'premi': line.premi,
                            'realization': material_realization_sum,
                            'real_stock_qty': real_stock_qty_sum,
                            'nilai': line.nilai,
                            'nilai2': line.nilai2,
                            'shi_work_day': line.work_day,
                            'shi_premi': line.premi,
                            'shi_realization': material_realization_sum,
                            'shi_nilai': line.nilai,
                            'shi_nilai_1': line.nilai2,
                        })
                        grouped_lhm[key.id]['subtotal_realization'] += sum(m.realization for m in materials)
                        grouped_lhm[key.id]['subtotal_real_stock_qty'] += sum(m.real_stock_qty for m in materials)
                        grouped_lhm[key.id]['subtotal_nilai'] += line.nilai
                        grouped_lhm[key.id]['subtotal_nilai_1'] += line.nilai2
                        grouped_lhm[key.id]['subtotal_workday'] += line.work_day
                        grouped_lhm[key.id]['subtotal_premi'] += line.premi
                        

                shi_subtotal_nilai = 0.0
                shi_subtotal_nilai_1 = 0.0
                shi_subtotal_workday = 0.0
                shi_subtotal_premi = 0.0
                shi_subtotal_realization = 0.0
                
                total_realization = 0.0
                total_real_stock_qty = 0.0
                total_nilai = 0.0
                total_nilai_1 = 0.0
                total_workday = 0.0
                total_premi = 0.0
                total_shi_realization = 0.0
                total_shi_total_nilai = 0.0
                total_shi_total_nilai_1 = 0.0
                total_shi_total_workday = 0.0
                total_shi_total_premi = 0.0

                for key, data in grouped_lhm.items():
                    shi_subtotal_realization = sum(progress['shi_realization'] for progress in data['progress'])
                    shi_subtotal_nilai = sum(progress['shi_nilai'] for progress in data['progress'])
                    shi_subtotal_nilai_1 = sum(progress['shi_nilai_1'] for progress in data['progress'])
                    shi_subtotal_workday = sum(progress['shi_work_day'] for progress in data['progress'])
                    shi_subtotal_premi = sum(progress['shi_premi'] for progress in data['progress'])

                    grouped_lhm[key]['shi_subtotal_realization'] = shi_subtotal_realization
                    grouped_lhm[key]['shi_subtotal_nilai'] = shi_subtotal_nilai
                    grouped_lhm[key]['shi_subtotal_nilai_1'] = shi_subtotal_nilai_1
                    grouped_lhm[key]['shi_subtotal_workday'] = shi_subtotal_workday
                    grouped_lhm[key]['shi_subtotal_premi'] = shi_subtotal_premi
                    
                    total_realization += data.get('subtotal_realization', 0.0)
                    total_real_stock_qty += data.get('subtotal_real_stock_qty', 0.0)
                    total_nilai += data.get('subtotal_nilai', 0.0)
                    total_nilai_1 += data.get('subtotal_nilai_1', 0.0)
                    total_workday += data.get('subtotal_workday', 0.0)
                    total_premi += data.get('subtotal_premi', 0.0)

                    total_shi_realization += data.get('shi_subtotal_realization', 0.0)
                    total_shi_total_nilai += data.get('shi_subtotal_nilai', 0.0)
                    total_shi_total_nilai_1 += data.get('shi_subtotal_nilai_1', 0.0)
                    total_shi_total_workday += data.get('shi_subtotal_workday', 0.0)
                    total_shi_total_premi += data.get('shi_subtotal_premi', 0.0)
            
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
                    
                    worksheet.write(row_data, 8, line['nilai'] if line['nilai'] else 0.0, wbf['number_content'])
                    worksheet.set_column(8, 8, 14)

                    worksheet.write(row_data, 9, line['shi_nilai'] if line['shi_nilai'] else 0.0, wbf['number_content'])
                    worksheet.set_column(9, 9, 14)

                    worksheet.write(row_data, 10, '-', wbf['content'])
                    worksheet.set_column(10, 10, 18)
                    
                    worksheet.write(row_data, 11, line['product_id_2'].name if line['product_id_2'] else '-', wbf['content'])
                    worksheet.set_column(11, 11, 18)

                    worksheet.write(row_data, 12, line['uom2_id'].name if line['uom2_id'].name else '-', wbf['content'])
                    worksheet.set_column(12, 12, 18)
                    
                    worksheet.write(row_data, 13, line['nilai2'] if line['nilai2'] else 0.0, wbf['number_content'])
                    worksheet.set_column(13, 13, 14)

                    worksheet.write(row_data, 14, line['shi_nilai_1'] if line['shi_nilai_1'] else 0.0, wbf['number_content'])
                    worksheet.set_column(14, 14, 14)

                    worksheet.write(row_data, 15, '-', wbf['content'])
                    worksheet.set_column(15, 15, 18)
                    
                    worksheet.write(row_data, 16, line['work_day'] if line['work_day'] else 0.0, wbf['number_content'])
                    worksheet.set_column(16, 16, 10)

                    worksheet.write(row_data, 17, line['premi'] if line['premi'] else 0.0, wbf['number_content'])
                    worksheet.set_column(17, 17, 18)

                    worksheet.write(row_data, 18, '-', wbf['content'])
                    worksheet.set_column(18, 18, 18)
                    
                    worksheet.write(row_data, 19, line['shi_work_day'] if line['shi_work_day'] else 0.0, wbf['number_content'])
                    worksheet.set_column(19, 19, 10)

                    worksheet.write(row_data, 20, line['shi_premi'] if line['shi_premi'] else 0.0, wbf['number_content'])
                    worksheet.set_column(20, 20, 18)

                    worksheet.write(row_data, 21, '-', wbf['content'])
                    worksheet.set_column(21, 21, 18)

                    worksheet.write(row_data, 22, get_material.name if get_material else '-', wbf['content'])
                    worksheet.set_column(22, 22, 18)

                    worksheet.write(row_data, 23, get_material.date.strftime('%d-%m-%Y') if get_material else '-', wbf['content'])
                    worksheet.set_column(23, 23, 18)

                    worksheet.write(row_data, 24, line['real_stock_qty'] if line['real_stock_qty'] else 0.0, wbf['number_content'])
                    worksheet.set_column(24, 24, 18)

                    worksheet.write(row_data, 25, get_material.product_id.name if get_material else '-', wbf['content'])
                    worksheet.set_column(25, 25, 40)

                    worksheet.write(row_data, 26, get_material.product_uom_id.name if get_material else '-', wbf['content'])
                    worksheet.set_column(26, 26, 18)

                    worksheet.write(row_data, 27, line['realization'] if line['realization'] else 0.0, wbf['number_content'])
                    worksheet.set_column(27, 27, 18)

                    worksheet.write(row_data, 28, line['shi_realization'] if line['shi_realization'] else 0.0, wbf['number_content'])
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
                worksheet.write(row_data, 8, lhm_data['subtotal_nilai'], wbf['number_total'])
                worksheet.write(row_data, 9, lhm_data['shi_subtotal_nilai'], wbf['number_total'])
                worksheet.write(row_data, 10, "", wbf['total'])
                worksheet.write(row_data, 11, "", wbf['total'])
                worksheet.write(row_data, 12, "", wbf['total'])
                worksheet.write(row_data, 13, lhm_data['subtotal_nilai_1'], wbf['number_total'])
                worksheet.write(row_data, 14, lhm_data['shi_subtotal_nilai_1'], wbf['number_total'])
                worksheet.write(row_data, 15, "", wbf['total'])
                worksheet.write(row_data, 16, lhm_data['subtotal_workday'], wbf['number_total'])
                worksheet.write(row_data, 17, lhm_data['subtotal_premi'], wbf['number_total'])
                worksheet.write(row_data, 18, "", wbf['total'])
                worksheet.write(row_data, 19, lhm_data['shi_subtotal_workday'], wbf['number_total'])
                worksheet.write(row_data, 20, lhm_data['shi_subtotal_premi'], wbf['number_total'])
                worksheet.write(row_data, 21, "", wbf['total'])
                worksheet.write(row_data, 22, "", wbf['total'])
                worksheet.write(row_data, 23, "", wbf['total'])
                worksheet.write(row_data, 24, lhm_data['subtotal_real_stock_qty'], wbf['number_total'])
                worksheet.write(row_data, 25, "", wbf['total'])
                worksheet.write(row_data, 26, "", wbf['total'])
                worksheet.write(row_data, 27, lhm_data['subtotal_realization'], wbf['number_total'])
                worksheet.write(row_data, 28, lhm_data['shi_subtotal_realization'], wbf['number_total'])
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
                worksheet.write(row_data, 8, total_nilai, wbf['number_total'])
                worksheet.write(row_data, 9, total_shi_total_nilai, wbf['number_total'])
                worksheet.write(row_data, 10, "", wbf['total'])
                worksheet.write(row_data, 11, "", wbf['total'])
                worksheet.write(row_data, 12, "", wbf['total'])
                worksheet.write(row_data, 13, total_nilai_1, wbf['number_total'])
                worksheet.write(row_data, 14, total_shi_total_nilai_1, wbf['number_total'])
                worksheet.write(row_data, 15, "", wbf['total'])
                worksheet.write(row_data, 16, total_workday, wbf['number_total'])
                worksheet.write(row_data, 17, total_premi, wbf['number_total'])
                worksheet.write(row_data, 18, "", wbf['total'])
                worksheet.write(row_data, 19, total_shi_total_workday, wbf['number_total'])
                worksheet.write(row_data, 20, total_shi_total_premi, wbf['number_total'])
                worksheet.write(row_data, 21, "", wbf['total'])
                worksheet.write(row_data, 22, "", wbf['total'])
                worksheet.write(row_data, 23, "", wbf['total'])
                worksheet.write(row_data, 24, total_real_stock_qty, wbf['number_total'])
                worksheet.write(row_data, 25, "", wbf['total'])
                worksheet.write(row_data, 26, "", wbf['total'])
                worksheet.write(row_data, 27, total_realization, wbf['number_total'])
                worksheet.write(row_data, 28, total_shi_realization, wbf['number_total'])
                worksheet.write(row_data, 29, "", wbf['total'])