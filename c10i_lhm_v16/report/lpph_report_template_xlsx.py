from odoo import fields, models, api
from datetime import datetime, timedelta
from collections import defaultdict

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

        self.wbf['header_total'] = workbook.add_format({'bold': 1, 'align': 'center', 'font_color': '#000000','bg_color': '#F5F4F4'})
        self.wbf['header_total'].set_border()
        self.wbf['header_total'].set_text_wrap()
        self.wbf['header_total'].set_align('vcenter')
        self.wbf['header_total'].set_font_size(8)
        
        self.wbf['signature'] = workbook.add_format({'align': 'center', 'font_color': '#000000'})
        self.wbf['signature'].set_border()
        self.wbf['signature'].set_text_wrap()
        self.wbf['signature'].set_align('center')
        self.wbf['signature'].set_align('top')
        self.wbf['signature'].set_font_size(10)

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

#     def generate_xlsx_report(self, workbook, data, objects):
#         workbook = self.add_workbook_format(workbook)
#         worksheet = workbook.add_worksheet("Laporan Progress Kerja Harian")
#         worksheet2 = workbook.add_worksheet("Pending Store Issue")
        
#         wbf = self.wbf

#         worksheet.set_column(0, 12, 15)
#         worksheet2.set_column(0, 12, 15)

#         for o in objects:
#             # Header
#             date_from = o.date_start.strftime('%d-%m-%Y')
#             date_to = o.date_end.strftime('%d-%m-%Y')
#             date = date_from if date_from == date_to else f"{(date_from) + ' s/d ' + (date_to)}"

#             lhm_transaction = self.env['lhm.transaction'].search([
#                                 ('date','=',o.date_start),
#                                 # ('date','<=',o.date_end),
#                                 ('state','=','done')
#                             ])
            
#             shi_month = o.date_start.month
#             shi_year = o.date_start.year
#             shi_date_from = datetime(shi_year, shi_month, 1)

#             shi_lhm_transaction = self.env['lhm.transaction'].search([
#                                 ('date','>=',shi_date_from),
#                                 ('date','<=',o.date_start),
#                                 ('state','=','done')
#                             ])

#             locations = []
#             for lhm_data in lhm_transaction:
#                 if lhm_data.location not in locations:
#                     locations.append(lhm_data.location)

#             location_name = ', '.join([location for location in locations])

            # row = 1
            # worksheet.write(row, 0, (o.company_id.name), wbf['title'])
            # worksheet.write(row + 1, 0, "LAPORAN PROGRES PEKERJAAN HARIAN - DETAIL MATERIAL", wbf['title'])
            # worksheet.write(row + 2, 0, "AFDELING BAGIAN", wbf['title'])
            # worksheet.write(row + 2, 1, ": %s" %(location_name), wbf['title'])
            # worksheet.write(row + 3, 0, "TYPE PEKERJA", wbf['title'])
            # worksheet.write(row + 3, 1, ": %s" %(o.type.upper()), wbf['title'])
            # worksheet.write(row + 4, 0, "TANGGAL", wbf['title'])
            # worksheet.write(row + 4, 1, ": %s" %(date), wbf['title'])
            # worksheet.set_row(row, 18)
            # worksheet.set_row(row + 1, 18)
            # worksheet.set_row(row + 2, 18)
            # worksheet.set_column(row + 2, 0, 20)
            # worksheet.set_row(row + 3, 18)
            # worksheet.set_row(row + 4, 18)
            
            # worksheet.merge_range(row, 25, row + 3, 26, "Diperiksa Oleh,", wbf['signature'])
            # worksheet.merge_range(row + 4, 25, row + 4, 26, "Ka. Afdeling/Kabag", wbf['header'])
            # worksheet.merge_range(row, 27, row + 3, 29, "Disetujui Oleh,", wbf['signature'])
            # worksheet.merge_range(row + 4, 27, row + 4, 29, "Asisten Kepala", wbf['header'])

            # next_row = row + 6
            # worksheet.merge_range(next_row, 0, next_row + 2, 0, "TYPE", wbf['header'])
            # worksheet.set_column(0, 0, 18)
            # worksheet.merge_range(next_row, 1, next_row + 1, 3, "LOKASI", wbf['header'])
            # worksheet.write(next_row + 2, 1, "KODE", wbf['header'])
            # worksheet.set_column(1, 1, 14)
            # worksheet.write(next_row + 2, 2, "SATUAN", wbf['header'])
            # worksheet.set_column(2, 2, 14)
            # worksheet.write(next_row + 2, 3, "QTY", wbf['header'])
            # worksheet.set_column(3, 3, 14)
            # worksheet.merge_range(next_row, 4, next_row + 1, 5, "KEGIATAN", wbf['header'])
            # worksheet.write(next_row + 2, 4, "COA", wbf['header'])
            # worksheet.set_column(4, 4, 14)
            # worksheet.write(next_row + 2, 5, "DESKRIPSI", wbf['header'])
            # worksheet.set_column(5, 5, 40)
            # worksheet.merge_range(next_row, 6, next_row + 2, 6, "PRODUCT 1", wbf['header'])
            # worksheet.set_column(6, 6, 18)
            # worksheet.merge_range(next_row, 7, next_row + 2, 7, "SATUAN 1", wbf['header'])
            # worksheet.set_column(7, 7, 18)
            # worksheet.merge_range(next_row, 8, next_row + 1, 9, "HASIL KERJA", wbf['header'])
            # worksheet.write(next_row + 2, 8, "HI", wbf['header'])
            # worksheet.set_column(8, 8, 14)
            # worksheet.write(next_row + 2, 9, "SHI", wbf['header'])
            # worksheet.set_column(9, 9, 14)
            # worksheet.merge_range(next_row, 10, next_row + 2, 10, "VARIANCE\n(+/-)", wbf['header'])
            # worksheet.set_column(10, 10, 18)
            # worksheet.merge_range(next_row, 11, next_row + 2, 11, "PRODUCT 2", wbf['header'])
            # worksheet.set_column(11, 11, 18)
            # worksheet.merge_range(next_row, 12, next_row + 2, 12, "SATUAN 2", wbf['header'])
            # worksheet.set_column(12, 12, 18)
            # worksheet.merge_range(next_row, 13, next_row + 1, 14, "HASIL KERJA", wbf['header'])
            # worksheet.write(next_row + 2, 13, "HI", wbf['header'])
            # worksheet.set_column(13, 13, 14)
            # worksheet.write(next_row + 2, 14, "SHI", wbf['header'])
            # worksheet.set_column(14, 14, 14)
            # worksheet.merge_range(next_row, 15, next_row + 2, 15, "VARIANCE\n(+/-)", wbf['header'])
            # worksheet.set_column(15, 15, 18)
            # worksheet.merge_range(next_row, 16, next_row, 21, "BIAYA", wbf['header'])
            # worksheet.merge_range(next_row + 1, 16, next_row + 1, 18, "HI", wbf['header'])
            # worksheet.write(next_row + 2, 16, "HK", wbf['header'])
            # worksheet.set_column(16, 16, 16)
            # worksheet.write(next_row + 2, 17, "BORONG/PREMI/LEMBUR", wbf['header'])
            # worksheet.set_column(17, 17, 23)
            # worksheet.write(next_row + 2, 18, "TOTAL", wbf['header'])
            # worksheet.set_column(18, 18, 18)
            # worksheet.merge_range(next_row + 1, 19, next_row + 1, 21, "SHI", wbf['header'])
            # worksheet.write(next_row + 2, 19, "HK", wbf['header'])
            # worksheet.set_column(19, 19, 10)
            # worksheet.write(next_row + 2, 20, "BORONG/PREMI/LEMBUR", wbf['header'])
            # worksheet.set_column(20, 20, 23)
            # worksheet.write(next_row + 2, 21, "TOTAL", wbf['header'])
            # worksheet.set_column(21, 21, 18)
            # worksheet.merge_range(next_row, 22, next_row, 29, "PEMAKAIAN MATERIAL", wbf['header'])
            # worksheet.merge_range(next_row + 1, 22, next_row + 1, 24, "SKB", wbf['header'])
            # worksheet.write(next_row + 2, 22, "NO. BPB", wbf['header'])
            # worksheet.set_column(22, 22, 18)
            # worksheet.write(next_row + 2, 23, "TANGGAL", wbf['header'])
            # worksheet.set_column(23, 23, 18)
            # worksheet.write(next_row + 2, 24, "QTY", wbf['header'])
            # worksheet.set_column(24, 24, 18)
            # worksheet.merge_range(next_row + 1, 25, next_row + 2, 25, "NAMA MATERIAL", wbf['header'])
            # worksheet.set_column(25, 25, 40)
            # worksheet.merge_range(next_row + 1, 26, next_row + 2, 26, "SATUAN", wbf['header'])
            # worksheet.set_column(26, 26, 18)
            # worksheet.merge_range(next_row + 1, 27, next_row + 1, 28, "TOTAL", wbf['header'])
            # worksheet.write(next_row + 2, 27, "HI", wbf['header'])
            # worksheet.set_column(27, 27, 18)
            # worksheet.write(next_row + 2, 28, "SHI", wbf['header'])
            # worksheet.set_column(28, 28, 18)
            # worksheet.merge_range(next_row + 1, 29, next_row + 2, 29, "VARIANCE\n(+/-)", wbf['header'])
#             worksheet.set_column(29, 29, 18)

#             grouped_lhm = {}

#             for line in lhm_transaction.process_line_ids:
#                 key = line.location_id.type_id
#                 if key.id not in grouped_lhm:
#                     grouped_lhm[key.id] = {
#                         'key': key,
#                         'progress': [],
#                         'subtotal_realization': 0.0,
#                         'subtotal_real_stock_qty': 0.0,
#                         'subtotal_nilai': 0.0,
#                         'subtotal_nilai_1': 0.0,
#                         'subtotal_workday': 0.0,
#                         'subtotal_premi': 0.0,
#                         'shi_subtotal_realization': 0.0,
#                         'shi_subtotal_nilai': 0.0,
#                         'shi_subtotal_nilai_1': 0.0,
#                         'shi_subtotal_workday': 0.0,
#                         'shi_subtotal_premi': 0.0,
#                         'shi_subtotal_workdaypremi': 0.0,
#                         'realization': 0.0,
#                         'real_stock_qty': 0.0,
#                         'shi_realization': 0.0,
#                         'subtotal_total': 0.0,
#                         'subtotal_workdaypremi': 0.0,
#                     }

#                 transaction_line = self.env['lhm.transaction.line'].search([
#                     ('lhm_id', '=', line.lhm_id.id)
#                 ], limit=1)
#                 contract_wage_value = transaction_line.contract_wage_value if transaction_line else 0.0
#                 premi_value = contract_wage_value if transaction_line and transaction_line.is_borong else line.premi
                
#                 work_day_adjusted = line.work_day * contract_wage_value
#                 total_hk_premi = work_day_adjusted + premi_value

#                 materials = self.env['lhm.transaction.material.line'].search([
#                     ('progress_id', '=', line.id),
#                     ('realization', '>', 0)
#                 ])
#                 material_realization_sum = sum(m.realization for m in materials)
#                 real_stock_qty_sum = sum(m.real_stock_qty for m in materials)
                
#                 existing_progress = next((progress for progress in grouped_lhm[key.id]['progress'] 
#                     if progress['activity_id'] == line.activity_id and progress['location_id'] == line.location_id),None)

#                 if existing_progress:
#                     existing_progress['realization'] += material_realization_sum
#                     existing_progress['real_stock_qty'] += real_stock_qty_sum
#                     existing_progress['nilai'] += line.nilai
#                     existing_progress['nilai2'] += line.nilai2
#                     existing_progress['work_day'] += work_day_adjusted
#                     existing_progress['premi'] += premi_value
#                     existing_progress['total'] += total_hk_premi
#                 else:
#                     grouped_lhm[key.id]['progress'].append({
#                         'progress_id': line.id,
#                         'name': line.name,
#                         'product_id': line.product_id,
#                         'uom_id': line.uom_id,
#                         'product_id_2': line.product_id_2,
#                         'uom2_id': line.uom2_id,
#                         'activity_id': line.activity_id,
#                         'location_id': line.location_id,
#                         'work_day': work_day_adjusted,
#                         'premi': premi_value,
#                         'realization': material_realization_sum,                        
#                         'real_stock_qty': real_stock_qty_sum,
#                         'nilai': line.nilai,
#                         'nilai2': line.nilai2,
#                         'total': total_hk_premi,
#                     })
#                     grouped_lhm[key.id]['subtotal_realization'] += material_realization_sum
#                     grouped_lhm[key.id]['subtotal_real_stock_qty'] += real_stock_qty_sum
#                     grouped_lhm[key.id]['subtotal_nilai'] += line.nilai
#                     grouped_lhm[key.id]['subtotal_nilai_1'] += line.nilai2
#                     grouped_lhm[key.id]['subtotal_workday'] += work_day_adjusted
#                     grouped_lhm[key.id]['subtotal_premi'] += premi_value
#                     grouped_lhm[key.id]['subtotal_total'] += total_hk_premi
#                     grouped_lhm[key.id]['subtotal_workdaypremi'] += work_day_adjusted

#             if lhm_transaction:
#                 for line in shi_lhm_transaction.process_line_ids:
#                     key = line.location_id.type_id

#                     if key.id not in grouped_lhm:
#                         grouped_lhm[key.id] = {
#                             'key': key,
#                             'progress': [],
#                             'subtotal_realization': 0.0,
#                             'realization': 0.0,
#                             'subtotal_real_stock_qty': 0.0,
#                             'real_stock_qty': 0.0,
#                             'nilai': 0.0,
#                             'nilai_1': 0.0,
#                             'subtotal_nilai': 0.0,
#                             'subtotal_nilai_1': 0.0,
#                             'subtotal_workday': 0.0,
#                             'subtotal_premi': 0.0,
#                             'shi_subtotal_realization': 0.0,
#                             'shi_realization': 0.0,
#                             'shi_nilai': 0.0,
#                             'shi_nilai_1': 0.0,
#                             'shi_subtotal_nilai': 0.0,
#                             'shi_subtotal_nilai_1': 0.0,
#                             'shi_subtotal_workday': 0.0,
#                             'shi_subtotal_premi': 0.0,
#                             'shi_subtotal_workdaypremi': 0.0,
#                         }

#                     transaction_line = self.env['lhm.transaction.line'].search([
#                         ('lhm_id', '=', line.lhm_id.id)
#                     ], limit=1)
#                     contract_wage_value = transaction_line.contract_wage_value if transaction_line else 0.0
#                     premi_value = contract_wage_value if transaction_line and transaction_line.is_borong else line.premi
                    
#                     work_day_adjusted = line.work_day * contract_wage_value
#                     total_hk_premi = work_day_adjusted + premi_value

#                     materials = self.env['lhm.transaction.material.line'].search([
#                             ('progress_id', '=', line.id),
#                             ('realization', '>', 0)
#                         ])
#                     material_realization_sum = sum(m.realization for m in materials)
#                     real_stock_qty_sum = sum(m.real_stock_qty for m in materials)
                    
#                     existing_progress = next((progress for progress in grouped_lhm[key.id]['progress'] 
#                         if progress['activity_id'] == line.activity_id and progress['location_id'] == line.location_id),None)
        
#                     if existing_progress:
#                         existing_progress['shi_realization'] = existing_progress.get('shi_realization', 0.0) + material_realization_sum
#                         existing_progress['shi_nilai'] = existing_progress.get('shi_nilai', 0.0) + line.nilai
#                         existing_progress['shi_nilai_1'] = existing_progress.get('shi_nilai_1', 0.0) + line.nilai2
#                         existing_progress['shi_work_day'] = existing_progress.get('shi_work_day', 0.0) + work_day_adjusted
#                         existing_progress['shi_premi'] = existing_progress.get('shi_premi', 0.0) + premi_value
#                         existing_progress['shi_workdaypremi'] = existing_progress.get('shi_workdaypremi', 0.0) + total_hk_premi
#                     else:
#                         grouped_lhm[key.id]['progress'].append({
#                             'progress_id': line.id,
#                             'name': line.name,
#                             'product_id': line.product_id,
#                             'uom_id': line.uom_id,
#                             'product_id_2': line.product_id_2,
#                             'uom2_id': line.uom2_id,
#                             'activity_id': line.activity_id,
#                             'location_id': line.location_id,
#                             'work_day': line.work_day,
#                             'premi': line.premi,
#                             'realization': material_realization_sum,
#                             'real_stock_qty': real_stock_qty_sum,
#                             'nilai': line.nilai,
#                             'nilai2': line.nilai2,
#                             'shi_work_day': work_day_adjusted,
#                             'shi_premi': premi_value,
#                             'shi_workdaypremi': total_hk_premi,
#                             'shi_realization': material_realization_sum,
#                             'shi_nilai': line.nilai,
#                             'shi_nilai_1': line.nilai2,
#                         })
#                         grouped_lhm[key.id]['subtotal_realization'] += sum(m.realization for m in materials)
#                         grouped_lhm[key.id]['subtotal_real_stock_qty'] += sum(m.real_stock_qty for m in materials)
#                         grouped_lhm[key.id]['subtotal_nilai'] += line.nilai
#                         grouped_lhm[key.id]['subtotal_nilai_1'] += line.nilai2
#                         grouped_lhm[key.id]['subtotal_workday'] += work_day_adjusted
#                         grouped_lhm[key.id]['subtotal_premi'] += premi_value
#                         grouped_lhm[key.id]['subtotal_workdaypremi'] += total_hk_premi
                        

#                 shi_subtotal_nilai = 0.0
#                 shi_subtotal_nilai_1 = 0.0
#                 shi_subtotal_workday = 0.0
#                 shi_subtotal_premi = 0.0
#                 shi_subtotal_workdaypremi = 0.0
#                 shi_subtotal_realization = 0.0
                
#                 total_realization = 0.0
#                 total_real_stock_qty = 0.0
#                 total_nilai = 0.0
#                 total_nilai_1 = 0.0
#                 total_workday = 0.0
#                 total_premi = 0.0
#                 total_workdaypremi = 0.0
#                 total_shi_realization = 0.0
#                 total_shi_total_nilai = 0.0
#                 total_shi_total_nilai_1 = 0.0
#                 total_shi_total_workday = 0.0
#                 total_shi_total_premi = 0.0
#                 total_shi_total_workdaypremi = 0.0

#                 for key, data in grouped_lhm.items():
#                     shi_subtotal_realization = sum(progress['shi_realization'] for progress in data['progress'])
#                     shi_subtotal_nilai = sum(progress['shi_nilai'] for progress in data['progress'])
#                     shi_subtotal_nilai_1 = sum(progress['shi_nilai_1'] for progress in data['progress'])
#                     shi_subtotal_workday = sum(progress['shi_work_day'] for progress in data['progress'])
#                     shi_subtotal_premi = sum(progress['shi_premi'] for progress in data['progress'])
#                     shi_subtotal_workdaypremi = sum(progress['shi_workdaypremi'] for progress in data['progress'])

#                     grouped_lhm[key]['shi_subtotal_realization'] = shi_subtotal_realization
#                     grouped_lhm[key]['shi_subtotal_nilai'] = shi_subtotal_nilai
#                     grouped_lhm[key]['shi_subtotal_nilai_1'] = shi_subtotal_nilai_1
#                     grouped_lhm[key]['shi_subtotal_workday'] = shi_subtotal_workday
#                     grouped_lhm[key]['shi_subtotal_premi'] = shi_subtotal_premi
#                     grouped_lhm[key]['shi_subtotal_workdaypremi'] = shi_subtotal_workdaypremi
                    
#                     total_realization += data.get('subtotal_realization', 0.0)
#                     total_real_stock_qty += data.get('subtotal_real_stock_qty', 0.0)
#                     total_nilai += data.get('subtotal_nilai', 0.0)
#                     total_nilai_1 += data.get('subtotal_nilai_1', 0.0)
#                     total_workday += data.get('subtotal_workday', 0.0)
#                     total_workdaypremi += data.get('subtotal_workdaypremi', 0.0)
#                     total_premi += data.get('subtotal_premi', 0.0)

#                     total_shi_realization += data.get('shi_subtotal_realization', 0.0)
#                     total_shi_total_nilai += data.get('shi_subtotal_nilai', 0.0)
#                     total_shi_total_nilai_1 += data.get('shi_subtotal_nilai_1', 0.0)
#                     total_shi_total_workday += data.get('shi_subtotal_workday', 0.0)
#                     total_shi_total_premi += data.get('shi_subtotal_premi', 0.0)
#                     total_shi_total_workdaypremi += data.get('shi_subtotal_workdaypremi', 0.0)
            
#             row_data = next_row + 4

#             for lhm_data in grouped_lhm.values():
#                 for line in lhm_data['progress']:

#                     get_material = self.env['lhm.transaction.material.line'].search([
#                         ('progress_id', '=', line['progress_id']),
#                         ('realization', '>', 0)
#                     ])
#                     # for material in get_material:

#                     worksheet.write(row_data, 0, lhm_data['key'].code, wbf['content'])
#                     worksheet.set_column(0, 0, 18)

#                     worksheet.write(row_data, 1, line['location_id'].code, wbf['content'])
#                     worksheet.set_column(1, 1, 14)

#                     worksheet.write(row_data, 2, '-', wbf['content'])
#                     worksheet.set_column(2, 2, 14)

#                     worksheet.write(row_data, 3, '-', wbf['content'])
#                     worksheet.set_column(3, 3, 14)

#                     worksheet.write(row_data, 4, line['activity_id'].code if line['activity_id'] else '-', wbf['content'])
#                     worksheet.set_column(4, 4, 14)

#                     worksheet.write(row_data, 5, line['name'] if line['name'] else '-', wbf['content'])
#                     worksheet.set_column(5, 5, 40)

#                     worksheet.write(row_data, 6, line['product_id'].name if line['product_id'] else '-', wbf['content'])
#                     worksheet.set_column(6, 6, 18)

#                     worksheet.write(row_data, 7, line['uom_id'].name if line['uom_id'] else '-', wbf['content'])
#                     worksheet.set_column(7, 7, 18)
                    
#                     worksheet.write(row_data, 8, line['nilai'] if line['nilai'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(8, 8, 14)

#                     worksheet.write(row_data, 9, line['shi_nilai'] if line['shi_nilai'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(9, 9, 14)

#                     worksheet.write(row_data, 10, '-', wbf['content'])
#                     worksheet.set_column(10, 10, 18)
                    
#                     worksheet.write(row_data, 11, line['product_id_2'].name if line['product_id_2'] else '-', wbf['content'])
#                     worksheet.set_column(11, 11, 18)

#                     worksheet.write(row_data, 12, line['uom2_id'].name if line['uom2_id'].name else '-', wbf['content'])
#                     worksheet.set_column(12, 12, 18)
                    
#                     worksheet.write(row_data, 13, line['nilai2'] if line['nilai2'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(13, 13, 14)

#                     worksheet.write(row_data, 14, line['shi_nilai_1'] if line['shi_nilai_1'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(14, 14, 14)

#                     worksheet.write(row_data, 15, '-', wbf['content'])
#                     worksheet.set_column(15, 15, 18)
                    
#                     worksheet.write(row_data, 16, line['work_day'] if line['work_day'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(16, 16, 10)

#                     worksheet.write(row_data, 17, line['premi'] if line['premi'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(17, 17, 18)

#                     worksheet.write(row_data, 18, line['total'] if line['total'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(18, 18, 18)
                    
#                     worksheet.write(row_data, 19, line['shi_work_day'] if line['shi_work_day'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(19, 19, 10)

#                     worksheet.write(row_data, 20, line['shi_premi'] if line['shi_premi'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(20, 20, 18)

#                     worksheet.write(row_data, 21, line['shi_workdaypremi'] if line['shi_workdaypremi'] else 0.0, wbf['number_content'])
#                     worksheet.set_column(21, 21, 18)

#                     if get_material:
#                         material_row = row_data

#                         for material in get_material:

#                             worksheet.write(row_data, 22, material.move_id.picking_id.name , wbf['content'])
#                             worksheet.set_column(22, 22, 18)

#                             worksheet.write(row_data, 23, material.date.strftime('%d-%m-%Y') , wbf['content'])
#                             worksheet.set_column(23, 23, 18)

#                             worksheet.write(row_data, 24, material.real_stock_qty, wbf['number_content'])
#                             worksheet.set_column(24, 24, 18)

#                             worksheet.write(row_data, 25, material.product_id.name , wbf['content'])
#                             worksheet.set_column(25, 25, 40)

#                             worksheet.write(row_data, 26, material.product_uom_id.name , wbf['content'])
#                             worksheet.set_column(26, 26, 18)

#                             worksheet.write(row_data, 27, material.realization, wbf['number_content'])
#                             worksheet.set_column(27, 27, 18)

#                             worksheet.write(row_data, 28, material.realization, wbf['number_content'])
#                             worksheet.set_column(28, 28, 18)

#                             worksheet.write(row_data, 29, '-', wbf['content'])
#                             worksheet.set_column(29, 29, 18)

#                             row_data += 1

#                         # worksheet.merge_range(material_row,27,row_data-1,27,line['realization'] if line['realization'] else 0.0,wbf['number_content'])
#                         # worksheet.set_column(27, 27, 18)

#                         # worksheet.merge_range(material_row,28,row_data-1,28,line['shi_realization'] if line['shi_realization'] else 0.0,wbf['number_content'])
#                         # worksheet.set_column(28, 28, 18)

#                         # worksheet.merge_range(material_row,29,row_data-1,29,'-',wbf['number_content'])
#                         # worksheet.set_column(29, 29, 18)

#                     else:
#                         worksheet.write(row_data, 22, '-' , wbf['content'])
#                         worksheet.set_column(22, 22, 18)

#                         worksheet.write(row_data, 23, '-' , wbf['content'])
#                         worksheet.set_column(23, 23, 18)

#                         worksheet.write(row_data, 24, 0.0, wbf['number_content'])
#                         worksheet.set_column(24, 24, 18)

#                         worksheet.write(row_data, 25, '-' , wbf['content'])
#                         worksheet.set_column(25, 25, 40)

#                         worksheet.write(row_data, 26, '-' , wbf['content'])
#                         worksheet.set_column(26, 26, 18)


#                         worksheet.write(row_data, 27, line['realization'] if line['realization'] else 0.0, wbf['number_content'])
#                         worksheet.set_column(27, 27, 18)

#                         worksheet.write(row_data, 28, line['shi_realization'] if line['shi_realization'] else 0.0, wbf['number_content'])
#                         worksheet.set_column(28, 28, 18)

#                         worksheet.write(row_data, 29, '-', wbf['content'])
#                         worksheet.set_column(29, 29, 18)

#                         row_data += 1

#                 worksheet.write(row_data, 0, "Subtotal", wbf['total'])
#                 worksheet.write(row_data, 1, "", wbf['total'])
#                 worksheet.write(row_data, 2, "", wbf['total'])
#                 worksheet.write(row_data, 3, "", wbf['total'])
#                 worksheet.write(row_data, 4, "", wbf['total'])
#                 worksheet.write(row_data, 5, "", wbf['total'])
#                 worksheet.write(row_data, 6, "", wbf['total'])
#                 worksheet.write(row_data, 7, "", wbf['total'])
#                 worksheet.write(row_data, 8, lhm_data['subtotal_nilai'], wbf['number_total'])
#                 worksheet.write(row_data, 9, lhm_data['shi_subtotal_nilai'], wbf['number_total'])
#                 worksheet.write(row_data, 10, "", wbf['total'])
#                 worksheet.write(row_data, 11, "", wbf['total'])
#                 worksheet.write(row_data, 12, "", wbf['total'])
#                 worksheet.write(row_data, 13, lhm_data['subtotal_nilai_1'], wbf['number_total'])
#                 worksheet.write(row_data, 14, lhm_data['shi_subtotal_nilai_1'], wbf['number_total'])
#                 worksheet.write(row_data, 15, "", wbf['total'])
#                 worksheet.write(row_data, 16, lhm_data['subtotal_workday'], wbf['number_total'])
#                 worksheet.write(row_data, 17, lhm_data['subtotal_premi'], wbf['number_total'])
#                 worksheet.write(row_data, 18, lhm_data['subtotal_total'], wbf['number_total'])
#                 worksheet.write(row_data, 19, lhm_data['shi_subtotal_workday'], wbf['number_total'])
#                 worksheet.write(row_data, 20, lhm_data['shi_subtotal_premi'], wbf['number_total'])
#                 worksheet.write(row_data, 21, lhm_data['shi_subtotal_workdaypremi'], wbf['number_total'])
#                 worksheet.write(row_data, 22, "", wbf['total'])
#                 worksheet.write(row_data, 23, "", wbf['total'])
#                 worksheet.write(row_data, 24, lhm_data['subtotal_real_stock_qty'], wbf['number_total'])
#                 worksheet.write(row_data, 25, "", wbf['total'])
#                 worksheet.write(row_data, 26, "", wbf['total'])
#                 worksheet.write(row_data, 27, lhm_data['subtotal_realization'], wbf['number_total'])
#                 worksheet.write(row_data, 28, lhm_data['shi_subtotal_realization'], wbf['number_total'])
#                 worksheet.write(row_data, 29, "", wbf['total'])

#                 row_data += 1

#                 worksheet.write(row_data, 0, "Grand Total", wbf['total'])
#                 worksheet.write(row_data, 1, "", wbf['total'])
#                 worksheet.write(row_data, 2, "", wbf['total'])
#                 worksheet.write(row_data, 3, "", wbf['total'])
#                 worksheet.write(row_data, 4, "", wbf['total'])
#                 worksheet.write(row_data, 5, "", wbf['total'])
#                 worksheet.write(row_data, 6, "", wbf['total'])
#                 worksheet.write(row_data, 7, "", wbf['total'])
#                 worksheet.write(row_data, 8, total_nilai, wbf['number_total'])
#                 worksheet.write(row_data, 9, total_shi_total_nilai, wbf['number_total'])
#                 worksheet.write(row_data, 10, "", wbf['total'])
#                 worksheet.write(row_data, 11, "", wbf['total'])
#                 worksheet.write(row_data, 12, "", wbf['total'])
#                 worksheet.write(row_data, 13, total_nilai_1, wbf['number_total'])
#                 worksheet.write(row_data, 14, total_shi_total_nilai_1, wbf['number_total'])
#                 worksheet.write(row_data, 15, "", wbf['total'])
#                 worksheet.write(row_data, 16, total_workday, wbf['number_total'])
#                 worksheet.write(row_data, 17, total_premi, wbf['number_total'])
#                 worksheet.write(row_data, 18, total_workdaypremi, wbf['number_total'])
#                 worksheet.write(row_data, 19, total_shi_total_workday, wbf['number_total'])
#                 worksheet.write(row_data, 20, total_shi_total_premi, wbf['number_total'])
#                 worksheet.write(row_data, 21, total_shi_total_workdaypremi, wbf['number_total'])
#                 worksheet.write(row_data, 22, "", wbf['total'])
#                 worksheet.write(row_data, 23, "", wbf['total'])
#                 worksheet.write(row_data, 24, total_real_stock_qty, wbf['number_total'])
#                 worksheet.write(row_data, 25, "", wbf['total'])
#                 worksheet.write(row_data, 26, "", wbf['total'])
#                 worksheet.write(row_data, 27, total_realization, wbf['number_total'])
#                 worksheet.write(row_data, 28, total_shi_realization, wbf['number_total'])
#                 worksheet.write(row_data, 29, "", wbf['total'])

# ###################################     SHEET 2       #####################
#             row = 1
#             worksheet2.write(row, 0, (o.company_id.name), wbf['title'])
#             worksheet2.write(row + 1, 0, "LAPORAN PROGRES PEKERJAAN HARIAN - DETAIL MATERIAL", wbf['title'])
#             worksheet2.write(row + 2, 0, "AFDELING BAGIAN", wbf['title'])
#             worksheet2.write(row + 2, 1, ": %s" %(location_name), wbf['title'])
#             worksheet2.write(row + 3, 0, "TYPE PEKERJA", wbf['title'])
#             worksheet2.write(row + 3, 1, ": %s" %(o.type.upper()), wbf['title'])
#             worksheet2.write(row + 4, 0, "TANGGAL", wbf['title'])
#             worksheet2.write(row + 4, 1, ": %s" %(date), wbf['title'])
            
#             worksheet2.merge_range(row, 6, row + 3, 6, "Diperiksa Oleh,", wbf['signature'])
#             worksheet2.write(row + 4, 6, "Ka. Afdeling/Kabag", wbf['header'])
#             worksheet2.merge_range(row, 7, row + 3, 7, "Disetujui Oleh,", wbf['signature'])
#             worksheet2.write(row + 4, 7, "Asisten Kepala", wbf['header'])

#             next_row = row + 6
#             worksheet2.merge_range(next_row, 0, next_row + 2, 0, "TYPE", wbf['header'])
#             worksheet2.set_column(0, 0, 18)
#             worksheet2.merge_range(next_row, 1, next_row + 1, 1, "LOKASI", wbf['header'])
#             worksheet2.write(next_row + 2, 1, "KODE", wbf['header'])
#             worksheet2.set_column(1, 1, 14)
#             worksheet2.merge_range(next_row, 2, next_row + 1, 3, "KEGIATAN", wbf['header'])
#             worksheet2.write(next_row + 2, 2, "COA", wbf['header'])
#             worksheet2.set_column(2, 2, 14)
#             worksheet2.write(next_row + 2, 3, "DESKRIPSI", wbf['header'])
#             worksheet2.set_column(3, 3, 40)
#             worksheet2.merge_range(next_row, 4, next_row, 8, "PEMAKAIAN MATERIAL", wbf['header'])
#             worksheet2.merge_range(next_row + 1, 4, next_row + 1, 6, "SKB", wbf['header'])
#             worksheet2.write(next_row + 2, 4, "NO. BPB", wbf['header'])
#             worksheet2.set_column(4, 4, 18)
#             worksheet2.write(next_row + 2, 5, "TANGGAL", wbf['header'])
#             worksheet2.set_column(5, 5, 18)
#             worksheet2.write(next_row + 2, 6, "QTY", wbf['header'])
#             worksheet2.set_column(6, 6, 18)
#             worksheet2.merge_range(next_row + 1, 7, next_row + 2, 7, "NAMA MATERIAL", wbf['header'])
#             worksheet2.set_column(7, 7, 40)
#             worksheet2.merge_range(next_row + 1, 8, next_row + 2, 8, "SATUAN", wbf['header'])
#             worksheet2.set_column(8, 8, 18)

#             stock_move_ids = self.env['stock.move'].search([
#                                 ('picking_type_id.code', '=', 'issue'),
#                                 # ('allocation_residual_qty', '>', 0),
#                                 ('pending_material_allocation', '>', 0),
#                                 ('state','=','done')
#                             ],order="date desc, plantation_activity_id asc")

#             row_data = next_row + 3
#             activity_ids = []
#             grand_total_qty = 0
#             subtotal_qty = 0
#             coa = False
#             activity_name = False
#             for move_id in stock_move_ids:
#                 move_data = [
#                     move_id.plantation_location_type_id.code,
#                     move_id.plantation_location_id.code,
#                     move_id.plantation_activity_id.code,
#                     move_id.plantation_activity_name,
#                     move_id.picking_id.name,
#                     move_id.date,
#                     move_id.product_uom_qty,
#                     move_id.product_id.name,
#                     move_id.product_uom.name
#                 ]
#                 coa = move_id.plantation_activity_id.code
#                 activity_name = move_id.plantation_activity_name
                

#                 if move_id.plantation_activity_id.id not in activity_ids and activity_ids:
#                     worksheet2.write(row_data, 0, "Subtotal", wbf['total'])
#                     worksheet2.write(row_data, 1, "", wbf['total'])
#                     worksheet2.write(row_data, 2, move_data[1], wbf['total'])
#                     worksheet2.write(row_data, 6, subtotal_qty, wbf['total'])

#                     row_data += 1
#                     subtotal_qty = 0  
                

#                 worksheet2.write(row_data, 0, move_data[0], wbf['content'])
#                 worksheet2.set_column(0, 0, 18)

#                 worksheet2.write(row_data, 1, move_data[1], wbf['content'])
#                 worksheet2.set_column(1, 1, 14)

#                 worksheet2.write(row_data, 2, move_data[2], wbf['content'])
#                 worksheet2.set_column(2, 2, 14)

#                 worksheet2.write(row_data, 3, move_data[3], wbf['content'])
#                 worksheet2.set_column(3, 3, 40)

#                 worksheet2.write(row_data, 4, move_data[4] or '-', wbf['content'])
#                 worksheet2.set_column(4, 4, 14)

#                 worksheet2.write(row_data, 5, move_data[5], wbf['content'])
#                 worksheet2.set_column(5, 5, 14)

#                 worksheet2.write(row_data, 6, move_data[6], wbf['content'])
#                 worksheet2.set_column(6, 6, 14)

#                 worksheet2.write(row_data, 7, move_data[7] or '-', wbf['content'])
#                 worksheet2.set_column(7, 7, 40)

#                 worksheet2.write(row_data, 8, move_data[8], wbf['content'])
#                 worksheet2.set_column(8, 8, 14)

#                 subtotal_qty += move_data[6]
#                 grand_total_qty += move_data[6]

#                 activity_ids.append(move_id.plantation_activity_id.id)
#                 row_data += 1

#             worksheet2.write(row_data, 0, "Subtotal", wbf['total'])
#             worksheet2.write(row_data, 1, "", wbf['total'])
#             worksheet2.write(row_data, 2, coa, wbf['total'])
#             worksheet2.write(row_data, 3, activity_name, wbf['total'])
#             worksheet2.write(row_data, 4, "", wbf['total'])
#             worksheet2.write(row_data, 5, "", wbf['total'])
#             worksheet2.write(row_data, 6, subtotal_qty, wbf['total'])
#             worksheet2.write(row_data, 7, "", wbf['total'])
#             worksheet2.write(row_data, 8, "", wbf['total'])
#             row_data += 1

#             worksheet2.write(row_data, 0, "Grand Total", wbf['total'])
#             worksheet2.write(row_data, 1, "", wbf['total'])
#             worksheet2.write(row_data, 2, "", wbf['total'])
#             worksheet2.write(row_data, 3, "", wbf['total'])
#             worksheet2.write(row_data, 4, "", wbf['total'])
#             worksheet2.write(row_data, 5, "", wbf['total'])
#             worksheet2.write(row_data, 6, grand_total_qty, wbf['total'])
#             worksheet2.write(row_data, 7, "", wbf['total'])
#             worksheet2.write(row_data, 8, "", wbf['total'])

    def get_combined_report(self, date_start, date_end):
        query = """
            SELECT 
                main.location_type_id,
                ltp.code as type_location_code,
                main.location_id,
                ll.name as location_name,
                main.activity_id,
                la.name as activity_name,
                la.code as activity_code,
                main.product_id,
                pt.name->>'en_US' as product1_name,
                main.product_id_2,
                pt2.name->>'en_US' as product2_name,
                main.uom_id,
                uu1.name->>'en_US' as uom1_name,
                main.uom2_id,
                uu2.name->>'en_US' as uom2_name,
                main.hasil1,
                main.hasil1_shi,
                main.hasil2,
                main.hasil2_shi,
                main.hk_value,
                main.hk_value_shi,
                main.borong_value,
                main.borong_value_shi,
                main.kontraktor_value,
                main.kontraktor_value_shi,
                
                -- Pemakaian Material
                COALESCE(mat.total_consumed_hi, 0) AS total_consumed_hi,
                COALESCE(mat.total_consumed_shi, 0) AS total_consumed_shi,
                mat.product_id as product_material,
                pt3.name->>'en_US' as product_material_name,
                mat.product_uom_id as product_uom_material,
                uu3.name->>'en_US' as uom_material_name
                
            FROM (
                -- Query Pak hendra get hasil
                SELECT
                    sub.location_type_id,
                    sub.location_id,
                    sub.activity_id,
                    sub.product_id,
                    sub.product_id_2,
                    sub.uom_id,
                    sub.uom2_id,
                    SUM(sub.hasil1) AS hasil1,
                    SUM(sub.hasil1_shi) AS hasil1_shi,
                    SUM(sub.hasil2) AS hasil2,
                    SUM(sub.hasil2_shi) AS hasil2_shi,
                    SUM(sub.hk_value) AS hk_value,
                    SUM(sub.hk_value_shi) AS hk_value_shi,
                    SUM(sub.borong_value) AS borong_value,
                    SUM(sub.borong_value_shi) AS borong_value_shi,
                    SUM(sub.kontraktor_value) AS kontraktor_value,
                    SUM(sub.kontraktor_value_shi) AS kontraktor_value_shi
                FROM (
                    SELECT
                        ltl.location_type_id,
                        ltl.location_id,
                        ltl.activity_id,
                        ltl.product_id,
                        ltl.product_id_2,
                        ltl.satuan_1 AS uom_id,
                        ltl.satuan_2 AS uom2_id,
                        SUM(CASE WHEN ltl.date = %s THEN ltl.hasil_1 ELSE 0 END) AS hasil1,
                        SUM(ltl.hasil_1) AS hasil1_shi,
                        SUM(CASE WHEN ltl.date = %s THEN ltl.hasil_2 ELSE 0 END) AS hasil2,
                        SUM(ltl.hasil_2) AS hasil2_shi,
                        SUM(CASE WHEN ltl.is_borong = FALSE AND ltl.date = %s THEN ltl.contract_wage_value ELSE 0 END) AS hk_value,
                        SUM(CASE WHEN ltl.is_borong = FALSE THEN ltl.contract_wage_value ELSE 0 END) AS hk_value_shi,
                        SUM(CASE WHEN ltl.is_borong = TRUE AND ltl.date = %s THEN ltl.contract_wage_value ELSE 0 END) AS borong_value,
                        SUM(CASE WHEN ltl.is_borong = TRUE THEN ltl.contract_wage_value ELSE 0 END) AS borong_value_shi,
                        SUM(0) AS kontraktor_value,
                        SUM(0) AS kontraktor_value_shi
                    FROM lhm_transaction_line ltl
                    WHERE ltl.date BETWEEN %s AND %s AND ltl.state = 'done'
                    GROUP BY ltl.location_type_id, ltl.activity_id, ltl.location_id, ltl.product_id, ltl.product_id_2, ltl.satuan_1, ltl.satuan_2
                    
                    UNION ALL
                    
                    SELECT
                        lcl.location_type_id,
                        lcl.location_id,
                        lcl.activity_id,
                        lcl.product_id,
                        lcl.product_id_2,
                        lcl.uom_id AS uom_id,
                        lcl.uom2_id AS uom2_id,
                        SUM(CASE WHEN lcl.date = %s THEN lcl.nilai ELSE 0 END) AS hasil1,
                        SUM(lcl.nilai) AS hasil1_shi,
                        SUM(CASE WHEN lcl.date = %s THEN lcl.nilai2 ELSE 0 END) AS hasil2,
                        SUM(lcl.nilai2) AS hasil2_shi,
                        SUM(0) AS hk_value,
                        SUM(0) AS hk_value_shi,
                        SUM(0) AS borong_value,
                        SUM(0) AS borong_value_shi,
                        SUM(CASE WHEN lcl.date = %s THEN lcl.total ELSE 0 END) AS kontraktor_value,
                        SUM(lcl.total) AS kontraktor_value_shi
                    FROM lhm_contractor_line lcl
                    WHERE lcl.date BETWEEN %s AND %s AND lcl.state = 'confirmed'
                    GROUP BY lcl.location_type_id, lcl.activity_id, lcl.location_id, lcl.product_id, lcl.product_id_2, lcl.uom_id, lcl.uom2_id
                ) sub
                GROUP BY sub.location_type_id, sub.location_id, sub.activity_id, sub.product_id, sub.product_id_2, sub.uom_id, sub.uom2_id
            ) main 

            -- Query pemakaian material
            LEFT JOIN (
                SELECT
                    lml.location_id,
                    lml.activity_id,
                    lml.product_id,
                    lml.product_uom_id,
                    SUM(CASE WHEN lt.date = %s THEN lml.realization ELSE 0 END) AS total_consumed_hi,
                    SUM(lml.realization) AS total_consumed_shi
                FROM lhm_transaction_material_line lml
                JOIN lhm_transaction lt ON lml.lhm_id = lt.id
                WHERE lt.date BETWEEN %s AND %s
                AND lml.realization > 0
                GROUP BY lml.location_id, lml.activity_id, lml.product_id, lml.product_uom_id
                
                UNION ALL
                
                SELECT
                    lcl.location_id,
                    lcl.activity_id,
                    lcl.product_id,
                    lcl.product_uom_id,
                    SUM(CASE WHEN lcl.date = %s THEN lcl.realization ELSE 0 END) AS total_consumed_hi,
                    SUM(lcl.realization) AS total_consumed_shi
                FROM lhm_contractor_material_line lcl
                WHERE lcl.date BETWEEN %s AND %s
                AND lcl.realization > 0
                GROUP BY lcl.location_id, lcl.activity_id, lcl.product_id, lcl.product_uom_id
            ) mat ON main.location_id = mat.location_id AND main.activity_id = mat.activity_id
            LEFT JOIN lhm_activity la on la.id = main.activity_id
            LEFT JOIN lhm_location_type ltp on ltp.id = main.location_type_id
            LEFT JOIN lhm_location ll on ll.id = main.location_id
            
            LEFT JOIN uom_uom uu1 on uu1.id = main.uom_id
            LEFT JOIN uom_uom uu2 on uu2.id = main.uom2_id
            
            LEFT JOIN product_product pp on pp.id = main.product_id
            LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id
            LEFT JOIN product_product pp2 on pp2.id = main.product_id_2
            LEFT JOIN product_template pt2 on pt2.id = pp2.product_tmpl_id
            
            LEFT JOIN product_product pp3 on pp3.id = mat.product_id
            LEFT JOIN product_template pt3 on pt3.id = pp3.product_tmpl_id
            LEFT JOIN uom_uom uu3 on uu3.id = mat.product_uom_id
            ORDER BY location_type_id, location_id;
        """

        self.env.cr.execute(query, (date_end, date_end, date_end, date_end, date_start, date_end, 
                                    date_end, date_end, date_end, date_start, date_end, 
                                    date_end, date_start, date_end, date_end, date_start, date_end))
        # return self.env.cr.fetchall()
        columns = [desc[0] for desc in self.env.cr.description]
        result = [dict(zip(columns, row)) for row in self.env.cr.fetchall()]
        return result

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        worksheet = workbook.add_worksheet("Laporan Progress Kerja Harian")
        worksheet2 = workbook.add_worksheet("Pending Store Issue")
        data_report = self.get_combined_report(obj.date_start, obj.date_end)

        date_from = obj.date_start.strftime('%d-%m-%Y')
        date_to = obj.date_end.strftime('%d-%m-%Y')
        date = date_from if date_from == date_to else f"{(date_from) + ' s/d ' + (date_to)}"

        row = 1
        worksheet.write(row, 0, (obj.company_id.name), wbf['title'])
        worksheet.write(row + 1, 0, "LAPORAN PROGRES PEKERJAAN HARIAN - DETAIL MATERIAL", wbf['title'])
        worksheet.write(row + 2, 0, "AFDELING BAGIAN", wbf['title'])
        worksheet.write(row + 2, 1, ": " , wbf['title'])
        worksheet.write(row + 3, 0, "TYPE PEKERJA", wbf['title'])
        worksheet.write(row + 3, 1, ": %s" %(obj.type.upper()), wbf['title'])
        worksheet.write(row + 4, 0, "TANGGAL", wbf['title'])
        worksheet.write(row + 4, 1, ": %s" %(date), wbf['title'])
        worksheet.set_row(row, 18)
        worksheet.set_row(row + 1, 18)
        worksheet.set_row(row + 2, 18)
        worksheet.set_column(row + 2, 0, 20)
        worksheet.set_row(row + 3, 18)
        worksheet.set_row(row + 4, 18)
        
        worksheet.merge_range(row, 25, row + 3, 26, "Diperiksa Oleh,", wbf['signature'])
        worksheet.merge_range(row + 4, 25, row + 4, 26, "Ka. Afdeling/Kabag", wbf['header'])
        worksheet.merge_range(row, 27, row + 3, 29, "Disetujui Oleh,", wbf['signature'])
        worksheet.merge_range(row + 4, 27, row + 4, 29, "Asisten Kepala", wbf['header'])

        next_row = row + 6
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

        worksheet.merge_range(next_row, 16, next_row, 23, "BIAYA", wbf['header'])
        worksheet.merge_range(next_row + 1, 16, next_row + 1, 19, "HI", wbf['header'])
        worksheet.write(next_row + 2, 16, "HK", wbf['header'])
        worksheet.set_column(16, 16, 16)
        worksheet.write(next_row + 2, 17, "BORONG/PREMI/LEMBUR", wbf['header'])
        worksheet.set_column(17, 17, 23)
        worksheet.write(next_row + 2, 18, "Kontraktor", wbf['header'])
        worksheet.set_column(17, 17, 23)
        worksheet.write(next_row + 2, 19, "TOTAL", wbf['header'])
        worksheet.set_column(18, 18, 18)

        worksheet.merge_range(next_row + 1, 20, next_row + 1, 23, "SHI", wbf['header'])
        worksheet.write(next_row + 2, 20, "HK", wbf['header'])
        worksheet.set_column(19, 19, 10)
        worksheet.write(next_row + 2, 21, "BORONG/PREMI/LEMBUR", wbf['header'])
        worksheet.set_column(20, 20, 23)
        worksheet.write(next_row + 2, 22, "Kontraktor", wbf['header'])
        worksheet.set_column(20, 20, 23)
        worksheet.write(next_row + 2, 23, "TOTAL", wbf['header'])
        worksheet.set_column(21, 21, 18)
        
        worksheet.merge_range(next_row, 24, next_row, 31, "PEMAKAIAN MATERIAL", wbf['header'])
        worksheet.merge_range(next_row + 1, 24, next_row + 1, 26, "SKB", wbf['header'])
        worksheet.write(next_row + 2, 24, "NO. BPB", wbf['header'])
        worksheet.set_column(22, 22, 18)
        worksheet.write(next_row + 2, 25, "TANGGAL", wbf['header'])
        worksheet.set_column(23, 23, 18)
        worksheet.write(next_row + 2, 26, "QTY", wbf['header'])
        worksheet.set_column(24, 24, 18)
        worksheet.merge_range(next_row + 1, 27, next_row + 2, 27, "NAMA MATERIAL", wbf['header'])
        worksheet.set_column(25, 25, 40)
        worksheet.merge_range(next_row + 1, 28, next_row + 2, 28, "SATUAN", wbf['header'])
        worksheet.set_column(26, 26, 18)
        worksheet.merge_range(next_row + 1, 29, next_row + 1, 30, "TOTAL", wbf['header'])
        worksheet.write(next_row + 2, 29, "HI", wbf['header'])
        worksheet.set_column(27, 27, 18)
        worksheet.write(next_row + 2, 30, "SHI", wbf['header'])
        worksheet.set_column(28, 28, 18)
        worksheet.merge_range(next_row + 1, 31, next_row + 2, 31, "VARIANCE\n(+/-)", wbf['header'])
        worksheet.set_column(29, 29, 18)

        row = next_row + 3 # Mulai dari baris setelah header
        previous_location_type = 0
        hk_hi = 0
        hk_shi = 0
        hk2_hi = 0
        hk2_shi = 0
        biaya_hi_hk = 0
        biaya_hi_premi = 0
        biaya_hi_kontraktor = 0
        biaya_hi_total = 0
        biaya_shi_hk = 0
        biaya_shi_premi = 0
        biaya_shi_kontraktor = 0
        biaya_shi_total = 0
        material_total_hi = 0
        material_total_shi = 0

        # Untuk grand total
        grand_hk_hi = 0
        grand_hk_shi = 0
        grand_hk2_hi = 0
        grand_hk2_shi = 0
        grand_biaya_hi_hk = 0
        grand_biaya_hi_premi = 0
        grand_biaya_hi_kontraktor = 0
        grand_biaya_shi_hk = 0
        grand_biaya_shi_premi = 0
        grand_biaya_shi_kontraktor = 0
        grand_material_total_hi = 0
        grand_material_total_shi = 0


        for data in data_report:
            if previous_location_type != data['type_location_code']:
                if previous_location_type != 0:
                    col = 0
                    worksheet.write(row, col, 'Subtotal', wbf['header_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-' , wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, hk_hi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, hk_shi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, hk2_hi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, hk2_shi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, biaya_hi_hk, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, biaya_hi_premi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, biaya_hi_kontraktor, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, biaya_shi_hk, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, biaya_shi_premi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, biaya_shi_kontraktor, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, material_total_hi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, material_total_shi, wbf['number_total'])
                    col+=1
                    worksheet.write(row, col, '-', wbf['number_total'])
                    col+=1

                    row += 1

                    # Akumulasi ke grand total
                    grand_hk_hi += hk_hi
                    grand_hk_shi += hk_shi
                    grand_hk2_hi += hk2_hi
                    grand_hk2_shi += hk2_shi
                    grand_biaya_hi_hk += biaya_hi_hk
                    grand_biaya_hi_premi += biaya_hi_premi
                    grand_biaya_hi_kontraktor += biaya_hi_kontraktor
                    grand_biaya_shi_hk += biaya_shi_hk
                    grand_biaya_shi_premi += biaya_shi_premi
                    grand_biaya_shi_kontraktor += biaya_shi_kontraktor
                    grand_material_total_hi += material_total_hi
                    grand_material_total_shi += material_total_shi

                    hk_hi = 0
                    hk_shi = 0
                    hk2_hi = 0
                    hk2_shi = 0
                    biaya_hi_hk = 0
                    biaya_hi_premi = 0
                    biaya_hi_kontraktor = 0
                    biaya_hi_total = 0
                    biaya_shi_hk = 0
                    biaya_shi_premi = 0
                    biaya_shi_kontraktor = 0
                    biaya_shi_total = 0
                    material_total_hi = 0
                    material_total_shi = 0

                previous_location_type = data['type_location_code']

            col = 0
            worksheet.write(row, col, data['type_location_code'] if data['type_location_code'] else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['location_name'] if data['location_name']  else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, '-', wbf['content'])
            col+=1
            worksheet.write(row, col, '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['activity_code'] if data['activity_code']  else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['activity_name'] if data['activity_name'] else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['product1_name'] if data['product1_name']  else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['uom1_name'] if data['uom1_name']  else '-' , wbf['content'])
            col+=1
            worksheet.write(row, col, data['hasil1'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['hasil1_shi'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, '-', wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['product2_name'] if data['product2_name']  else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['uom2_name'] if data['uom2_name']  else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['hasil2'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['hasil2_shi'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, '-', wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['hk_value'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['borong_value'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['kontraktor_value'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, '-', wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['hk_value_shi'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['borong_value_shi'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['kontraktor_value_shi'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, '-', wbf['content'])
            col+=1
            worksheet.write(row, col, '-', wbf['content'])
            col+=1
            worksheet.write(row, col, '-', wbf['content'])
            col+=1
            worksheet.write(row, col, '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['product_material_name'] if data['product_material_name']  else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['uom_material_name'] if data['uom_material_name']  else '-', wbf['content'])
            col+=1
            worksheet.write(row, col, data['total_consumed_hi'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, data['total_consumed_shi'], wbf['number_content'])
            col+=1
            worksheet.write(row, col, '-', wbf['content'])
            col+=1
            
            hk_hi += data['hasil1']
            hk_shi += data['hasil1_shi']
            hk2_hi += data['hasil2']
            hk2_shi += data['hasil2_shi']

            biaya_hi_hk += data['hk_value']
            biaya_hi_premi += data['borong_value']
            biaya_hi_kontraktor += data['kontraktor_value']
            # biaya_hi_total += data['hasil2']

            biaya_shi_hk += data['hk_value_shi']
            biaya_shi_premi += data['borong_value_shi']
            biaya_shi_kontraktor += data['kontraktor_value_shi']
            # biaya_shi_total += data['hasil2']

            material_total_hi += data['total_consumed_hi']
            material_total_shi += data['total_consumed_shi']

            row += 1 


        # Grand total
        row += 1
        col = 0
        worksheet.write(row, col, 'Grand Total', wbf['header_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-' , wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_hk_hi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_hk_shi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_hk2_hi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_hk2_shi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_biaya_hi_hk, wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_biaya_hi_premi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_biaya_hi_kontraktor, wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_biaya_shi_hk, wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_biaya_shi_premi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_biaya_shi_kontraktor, wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_material_total_hi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, grand_material_total_shi, wbf['number_total'])
        col+=1
        worksheet.write(row, col, '-', wbf['number_total'])
        col+=1

        row += 1
    
        # Page Layout
        worksheet.set_landscape()
        worksheet.set_paper(9) # A4
        # worksheet.set_header()
        worksheet.repeat_rows(1, 4)
        worksheet.print_area(0, 0, row, 13)
        worksheet.set_print_scale(78)


        row = 1
        worksheet2.write(row, 0, (obj.company_id.name), wbf['title'])
        worksheet2.write(row + 1, 0, "LAPORAN PROGRES PEKERJAAN HARIAN - DETAIL MATERIAL", wbf['title'])
        worksheet2.write(row + 2, 0, "AFDELING BAGIAN", wbf['title'])
        worksheet2.write(row + 2, 1, ":", wbf['title'])
        worksheet2.write(row + 3, 0, "TYPE PEKERJA", wbf['title'])
        worksheet2.write(row + 3, 1, ": %s" %(obj.type.upper()), wbf['title'])
        worksheet2.write(row + 4, 0, "TANGGAL", wbf['title'])
        worksheet2.write(row + 4, 1, ": %s" %(date), wbf['title'])

        worksheet2.merge_range(row, 6, row + 3, 6, "Diperiksa Oleh,", wbf['signature'])
        worksheet2.write(row + 4, 6, "Ka. Afdeling/Kabag", wbf['header'])
        worksheet2.merge_range(row, 7, row + 3, 7, "Disetujui Oleh,", wbf['signature'])
        worksheet2.write(row + 4, 7, "Asisten Kepala", wbf['header'])

        next_row = row + 6
        worksheet2.merge_range(next_row, 0, next_row + 2, 0, "TYPE", wbf['header'])
        worksheet2.set_column(0, 0, 18)
        worksheet2.merge_range(next_row, 1, next_row + 1, 1, "LOKASI", wbf['header'])
        worksheet2.write(next_row + 2, 1, "KODE", wbf['header'])
        worksheet2.set_column(1, 1, 14)
        worksheet2.merge_range(next_row, 2, next_row + 1, 3, "KEGIATAN", wbf['header'])
        worksheet2.write(next_row + 2, 2, "COA", wbf['header'])
        worksheet2.set_column(2, 2, 14)
        worksheet2.write(next_row + 2, 3, "DESKRIPSI", wbf['header'])
        worksheet2.set_column(3, 3, 40)
        worksheet2.merge_range(next_row, 4, next_row, 8, "PEMAKAIAN MATERIAL", wbf['header'])
        worksheet2.merge_range(next_row + 1, 4, next_row + 1, 6, "SKB", wbf['header'])
        worksheet2.write(next_row + 2, 4, "NO. BPB", wbf['header'])
        worksheet2.set_column(4, 4, 18)
        worksheet2.write(next_row + 2, 5, "TANGGAL", wbf['header'])
        worksheet2.set_column(5, 5, 18)
        worksheet2.write(next_row + 2, 6, "QTY", wbf['header'])
        worksheet2.set_column(6, 6, 18)
        worksheet2.merge_range(next_row + 1, 7, next_row + 2, 7, "NAMA MATERIAL", wbf['header'])
        worksheet2.set_column(7, 7, 40)
        worksheet2.merge_range(next_row + 1, 8, next_row + 2, 8, "SATUAN", wbf['header'])
        worksheet2.set_column(8, 8, 18)

        stock_move_ids = self.env['stock.move'].search([
                            ('picking_type_id.code', '=', 'issue'),
                            # ('allocation_residual_qty', '>', 0),
                            ('pending_material_allocation', '>', 0),
                            ('state','=','done')
                        ],order="date desc, plantation_activity_id asc")

        row_data = next_row + 3
        activity_ids = []
        grand_total_qty = 0
        subtotal_qty = 0
        coa = False
        activity_name = False
        for move_id in stock_move_ids:
            move_data = [
                move_id.plantation_location_type_id.code,
                move_id.plantation_location_id.code,
                move_id.plantation_activity_id.code,
                move_id.plantation_activity_name,
                move_id.picking_id.name,
                move_id.date,
                move_id.product_uom_qty,
                move_id.product_id.name,
                move_id.product_uom.name
            ]
            coa = move_id.plantation_activity_id.code
            activity_name = move_id.plantation_activity_name
    

            if move_id.plantation_activity_id.id not in activity_ids and activity_ids:
                worksheet2.write(row_data, 0, "Subtotal", wbf['total'])
                worksheet2.write(row_data, 1, "", wbf['total'])
                worksheet2.write(row_data, 2, move_data[1], wbf['total'])
                worksheet2.write(row_data, 6, subtotal_qty, wbf['total'])

                row_data += 1
                subtotal_qty = 0  
    

            worksheet2.write(row_data, 0, move_data[0], wbf['content'])
            worksheet2.set_column(0, 0, 18)

            worksheet2.write(row_data, 1, move_data[1], wbf['content'])
            worksheet2.set_column(1, 1, 14)

            worksheet2.write(row_data, 2, move_data[2], wbf['content'])
            worksheet2.set_column(2, 2, 14)

            worksheet2.write(row_data, 3, move_data[3], wbf['content'])
            worksheet2.set_column(3, 3, 40)

            worksheet2.write(row_data, 4, move_data[4] or '-', wbf['content'])
            worksheet2.set_column(4, 4, 14)

            worksheet2.write(row_data, 5, move_data[5], wbf['content'])
            worksheet2.set_column(5, 5, 14)

            worksheet2.write(row_data, 6, move_data[6], wbf['content'])
            worksheet2.set_column(6, 6, 14)

            worksheet2.write(row_data, 7, move_data[7] or '-', wbf['content'])
            worksheet2.set_column(7, 7, 40)

            worksheet2.write(row_data, 8, move_data[8], wbf['content'])
            worksheet2.set_column(8, 8, 14)

            subtotal_qty += move_data[6]
            grand_total_qty += move_data[6]

            activity_ids.append(move_id.plantation_activity_id.id)
            row_data += 1

        worksheet2.write(row_data, 0, "Subtotal", wbf['total'])
        worksheet2.write(row_data, 1, "", wbf['total'])
        worksheet2.write(row_data, 2, coa, wbf['total'])
        worksheet2.write(row_data, 3, activity_name, wbf['total'])
        worksheet2.write(row_data, 4, "", wbf['total'])
        worksheet2.write(row_data, 5, "", wbf['total'])
        worksheet2.write(row_data, 6, subtotal_qty, wbf['total'])
        worksheet2.write(row_data, 7, "", wbf['total'])
        worksheet2.write(row_data, 8, "", wbf['total'])
        row_data += 1

        worksheet2.write(row_data, 0, "Grand Total", wbf['total'])
        worksheet2.write(row_data, 1, "", wbf['total'])
        worksheet2.write(row_data, 2, "", wbf['total'])
        worksheet2.write(row_data, 3, "", wbf['total'])
        worksheet2.write(row_data, 4, "", wbf['total'])
        worksheet2.write(row_data, 5, "", wbf['total'])
        worksheet2.write(row_data, 6, grand_total_qty, wbf['total'])
        worksheet2.write(row_data, 7, "", wbf['total'])
        worksheet2.write(row_data, 8, "", wbf['total'])


