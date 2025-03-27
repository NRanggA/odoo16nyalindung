from odoo import api, models, fields, _
from xlsxwriter.utility import xl_rowcol_to_cell
# from odoo.exceptions import Warning
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta

class RekapBukuKontraktor(models.AbstractModel):
    _name = 'report.nyalindung_report.rekap_buku_kontraktor_xlsx'
    _description = "Rekap Buku Kontraktor Excel"
    _inherit = 'report.report_xlsx.abstract'

    wbf = {}

    # def _get_objs_for_report(self, docids, data):
    #     options = data.get('options', {})
    #     wizard = self.env['payroll.report.wizard'].browse(options['src_id'])
    #     return wizard.payslip_ids

    def add_workbook_format(self, workbook):
        font_color = '#000000'
        font_color_header = font_color
        font_color_subtotal = font_color
        font_color_grandtotal = font_color

        bg_color_header = '#FFFFDB'
        bg_color_subtotal = '#FFFFDB'
        bg_color_grandtotal = '#FFFFDB'
        # HEADER STYLE
        self.wbf['header'] = workbook.add_format({'bold': 1,
                                'align': 'center',
                                'bg_color': bg_color_header,
                                'font_color': font_color_header})
        self.wbf['header'].set_border()
        self.wbf['header'].set_text_wrap()
        self.wbf['header'].set_align('vcenter')

        self.wbf['header_no'] = workbook.add_format({'bold': 1,
                                'align': 'center',
                                'bg_color': bg_color_header,
                                'font_color': font_color_header})
        self.wbf['header_no'].set_border()
        self.wbf['header_no'].set_font_size(8)
        self.wbf['header_no'].set_align('vcenter')
                
        self.wbf['footer'] = workbook.add_format({'align':'left'})
        self.wbf['footer'].set_bottom()
        
        # CONTENT STYLE
        self.wbf['content'] = workbook.add_format()
        self.wbf['content'].set_left()
        self.wbf['content'].set_right() 
        self.wbf['content'].set_text_wrap()
        
        self.wbf['content_date'] = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        self.wbf['content_date'].set_left()
        self.wbf['content_date'].set_right()
        
        self.wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        self.wbf['content_datetime'].set_left()
        self.wbf['content_datetime'].set_right()
        
        self.wbf['content_float'] = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        self.wbf['content_float'].set_right() 
        self.wbf['content_float'].set_left()

        self.wbf['content_center'] = workbook.add_format({'align': 'centre'})
                
        self.wbf['content_percent'] = workbook.add_format({'align': 'right','num_format': '0.00%'})
        self.wbf['content_percent'].set_right()
        self.wbf['content_percent'].set_left()
        
        # SUBTOTAL STYLE
        self.wbf['subtotal_float'] = workbook.add_format({'bold':1,'bg_color': bg_color_header,
                        'align': 'right',
                        'font_color': font_color_grandtotal,
                        'num_format': '#,##0.00'})
        self.wbf['subtotal_float'].set_top()
        self.wbf['subtotal_float'].set_bottom()            
        self.wbf['subtotal_float'].set_left()
        self.wbf['subtotal_float'].set_right()         
        
        self.wbf['subtotal'] = workbook.add_format({'bold':1,
                        'bg_color': bg_color_grandtotal,
                        'font_color': font_color_grandtotal})
        self.wbf['subtotal'].set_left()
        self.wbf['subtotal'].set_right()
        self.wbf['subtotal'].set_top()
        self.wbf['subtotal'].set_bottom()

        self.wbf['subtotal_center'] = workbook.add_format({'bold':1,
                        'bg_color': bg_color_grandtotal,
                        'font_color': font_color_grandtotal,
                        'align':'center'})
        self.wbf['subtotal_center'].set_left()
        self.wbf['subtotal_center'].set_right()
        self.wbf['subtotal_center'].set_top()
        self.wbf['subtotal_center'].set_bottom()

        # GRAND TOTAL STYLE
        self.wbf['total_float'] = workbook.add_format({'bold':1,'bg_color': bg_color_header,
                        'align': 'right',
                        'font_color': font_color_grandtotal,
                        'num_format': '#,##0.00'})
        self.wbf['total_float'].set_top()
        self.wbf['total_float'].set_bottom()            
        self.wbf['total_float'].set_left()
        self.wbf['total_float'].set_right()         
        
        self.wbf['total'] = workbook.add_format({'bold':1,
                        'bg_color': bg_color_grandtotal,
                        'font_color': font_color_grandtotal})
        self.wbf['total'].set_left()
        self.wbf['total'].set_right()
        self.wbf['total'].set_top()
        self.wbf['total'].set_bottom()

        self.wbf['total_center'] = workbook.add_format({'bold':1,
                        'bg_color': bg_color_grandtotal,
                        'font_color': font_color_grandtotal,
                        'align':'center'})
        self.wbf['total_center'].set_left()
        self.wbf['total_center'].set_right()
        self.wbf['total_center'].set_top()
        self.wbf['total_center'].set_bottom()
        
        return workbook
 
    def generate_xlsx_report(self, workbook, data, obj):
        workbook = self.add_workbook_format(workbook)
        wbf=self.wbf

        # HEADER
        # header employee
        worksheet = workbook.add_worksheet("Detail")
        
        next_row = 1
        col = 1
        worksheet.write(next_row, col, 'Tanggal' , wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, 'Kontraktor / Pemborong' , wbf['header'])
        worksheet.set_column(col,col,30)
        col += 1
        worksheet.write(next_row, col, "Lokasi", wbf['header'])
        worksheet.set_column(col,col,15)
        col += 1
        worksheet.write(next_row, col, "Aktifitas", wbf['header'])
        worksheet.set_column(col,col,30)
        col += 1
        worksheet.write(next_row, col, "Hasil 1", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Satuan 1", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Hasil 2", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Satuan 2", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Tarif", wbf['header'])
        worksheet.set_column(col,col,12)
        col += 1
        worksheet.write(next_row, col, "Jumlah", wbf['header'])
        worksheet.set_column(col,col,15)
        col += 1
        next_row += 1
        
        for c in range(1,col):
            worksheet.write(next_row, c, c, wbf['header_no'])
        next_row += 1
        worksheet.freeze_panes(next_row, 3)

        domain = [('date','>=',obj.from_date),('date','<=',obj.to_date),('state','in',['confirmed','done'])]
        if obj.partner_ids:
            if len(obj.partner_ids)>1:
                domain.append(('supplier_id','in',obj.partner_ids.ids))
            else:
                domain.append(('supplier_id','=',obj.partner_ids.id))
        fields = ['date','supplier_id','location_id','activity_id','nilai','uom_id','nilai2','uom2_id','unit_price','unit_price_2','total']
        datas = self.env['lhm.contractor.line'].search_read(domain, fields=fields, order='supplier_id, date asc')
        prev_partner = False
        first_partner_row = next_row
        grand_total_rows = []
        rekap_contractors = {}
        for line in datas:
            # Write subtotal
            if prev_partner and prev_partner!=line.get('supplier_id',[0,'']):
                col = 1
                worksheet.write(next_row, col, f"Subtotal: {prev_partner[1]}", wbf['subtotal'])
                col += 1
                worksheet.write(next_row, col, "", wbf['subtotal'])
                col += 1
                worksheet.write(next_row, col, "", wbf['subtotal'])
                col += 1
                worksheet.write(next_row, col, "", wbf['subtotal'])
                col += 1
                worksheet.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_partner_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
                col += 1
                worksheet.write(next_row, col, "", wbf['subtotal'])
                col += 1
                worksheet.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_partner_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
                col += 1
                worksheet.write(next_row, col, "", wbf['subtotal'])
                col += 1
                worksheet.write(next_row, col, "", wbf['subtotal'])
                col += 1
                worksheet.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_partner_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
                rekap_contractors.update({prev_partner: {'row': next_row, 'col': col}})
                col += 1
                grand_total_rows.append(next_row)
                next_row += 1
                prev_partner = line.get('supplier_id',[0,''])
                first_partner_row = next_row
            elif not prev_partner:
                prev_partner = line.get('supplier_id',[0,''])
            
            # Write Detail
            col = 1
            worksheet.write(next_row, col, line.get('date', ''), wbf['content_date'])
            col += 1
            worksheet.write(next_row, col, line.get('supplier_id', [0,''])[1], wbf['content'])
            col += 1
            worksheet.write(next_row, col, line.get('location_id', [0,''])[1] if line.get('location_id') else '', wbf['content'])
            col += 1
            worksheet.write(next_row, col, line.get('activity_id', [0,''])[1] if line.get('activity_id') else '', wbf['content'])
            col += 1
            worksheet.write(next_row, col, line.get('nilai', 0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('uom_id', [0,''])[1] if line.get('uom_id') else '', wbf['content'])
            col += 1
            worksheet.write(next_row, col, line.get('nilai2', 0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('uom2_id', [0,''])[1] if line.get('uom2_id') else '', wbf['content'])
            col += 1
            worksheet.write(next_row, col, line.get('unit_price', 0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('total', 0), wbf['content_float'])
            col += 1
            next_row += 1
        
        # Write last subtotal
        if prev_partner:
            col = 1
            worksheet.write(next_row, col, f"Subtotal: {prev_partner[1]}", wbf['subtotal'])
            col += 1
            worksheet.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_partner_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
            col += 1
            worksheet.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_partner_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
            col += 1
            worksheet.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_partner_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
            rekap_contractors.update({prev_partner: {'row': next_row, 'col': col}})
            col += 1
            grand_total_rows.append(next_row)
            next_row += 1

        # Write grandtotal
        if grand_total_rows:
            col = 1
            worksheet.write(next_row, col, f"Grandtotal", wbf['total'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({';'.join([xl_rowcol_to_cell(grow,col) for grow in grand_total_rows])})", wbf['total_float'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({';'.join([xl_rowcol_to_cell(grow,col) for grow in grand_total_rows])})", wbf['total_float'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({';'.join([xl_rowcol_to_cell(grow,col) for grow in grand_total_rows])})", wbf['total_float'])
            col += 1
            grand_total_rows.append(next_row)
            next_row += 1

        worksheet.set_landscape()
        worksheet.set_paper(9)
        worksheet.repeat_rows(1, 2) 
        worksheet.print_area(0, 0, next_row, col+1)
        worksheet.set_print_scale(50)

        ########################################################### SHEET 2
        # HEADER
        # header employee
        worksheet2 = workbook.add_worksheet("Rekap")
        
        next_row = 1
        col = 1
        worksheet2.write(next_row, col, 'No.' , wbf['header'])
        worksheet2.set_column(col,col,5)
        col += 1
        worksheet2.write(next_row, col, 'Kontraktor / Pemborong' , wbf['header'])
        worksheet2.set_column(col,col,30)
        col += 1
        worksheet2.write(next_row, col, 'Total' , wbf['header'])
        worksheet2.set_column(col,col,15)
        col += 1
        worksheet2.write(next_row, col, 'GrossUp Upah' , wbf['header'])
        worksheet2.set_column(col,col,15)
        col += 1
        worksheet2.write(next_row, col, 'PPH 21 Upah' , wbf['header'])
        worksheet2.set_column(col,col,15)
        
        next_row += 1

        indx = 0
        first_row = next_row
        for partner, subtotal_pos in rekap_contractors.items():
            indx += 1
            col = 1
            worksheet2.write(next_row, col, indx, wbf['content_center'])
            col += 1
            worksheet2.write(next_row, col, partner[1], wbf['content'])
            col += 1
            worksheet2.write_formula(next_row, col, f"=Detail!{xl_rowcol_to_cell(subtotal_pos['row'], subtotal_pos['col'])}", wbf['content_float'])
            col += 1
            worksheet2.write(next_row, col, 0, wbf['content_float'])
            col += 1
            worksheet2.write(next_row, col, 0, wbf['content_float'])
            col += 1
            next_row += 1
        if rekap_contractors:
            col = 1
            worksheet2.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet2.write(next_row, col, "Total", wbf['total'])
            col += 1
            worksheet2.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_row, col)})" if first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(first_row, col)}:{next_row-1, col})", wbf['total_float'])
            col += 1
            worksheet2.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_row, col)})" if first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(first_row, col)}:{next_row-1, col})", wbf['total_float'])
            col += 1
            worksheet2.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_row, col)})" if first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(first_row, col)}:{next_row-1, col})", wbf['total_float'])
            col += 1
            next_row += 1
        # Page Layout
        worksheet2.set_landscape()
        worksheet2.set_paper(9) # A4
        # worksheet2.set_header()
        worksheet2.repeat_rows(1, 2) #Repeat column header
        worksheet2.print_area(0, 0, next_row, col+1)
        worksheet2.set_print_scale(50)
