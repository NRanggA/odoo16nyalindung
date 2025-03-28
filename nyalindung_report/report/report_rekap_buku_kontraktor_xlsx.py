from odoo import api, models, fields, _
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name
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
        ### FONT props
        bold = {'bold': 1} # True or False
        italic = {'italic': 1} # True or False
        font_name = {'font_name': 'Calibri'}
        font_color = {'font_color': '#000000'} # can be 'black', 'white', or hex format ('#00000') color
        font_size = {'font_size': 8}
        font_color_header = {'font_color': '#000000'}
        font_color_subtotal = {'font_color': '#000000'}
        font_color_grandtotal = {'font_color': '#000000'}
        # numeric
        num_format = {'num_format': '#,##0.00'}
        pct_format = {'num_format': '0.00%'}
        date_format = {'num_format': 'dd/mm/yyyy'}
        datetime_format = {'num_format': 'dd/mm/yyyy hh:mm:ss'}

        ### ALIGNMENT props
        text_wrap = {'text_wrap': 1} # True or False
        indent_1 = {'indent': 1} # first indentation level
        # set_text_h_align()
        align_left = {'align': 'left'}
        align_right = {'align': 'right'}
        align_center = {'align': 'center'}
        valign_top = {'valign': 'top'}
        valign_bot = {'valign': 'bottom'}
        valign_center = {'valign': 'vcenter'}
        # set_text_v_align()
        align_top = {'align': 'top'}
        align_vcenter = {'align': 'vcenter'}
        align_bottom = {'align': 'bottom'}

        ### PATTERN props
        bg_color = {'bg_color': 'white'} # can be 'black', 'white', or hex format ('#00000') color
        fg_color = {'fg_color': 'white'}
        pattern = {'pattern': 1}
        bg_color_header = {'bg_color': '#FFFFDB'}
        bg_color_subtotal = {'bg_color': '#FFFFDB'}
        bg_color_grandtotal = {'bg_color': '#FFFFDB'}

        ### BORDER props
        # there are 0 - 13 style that can be use
        # see for more style https://xlsxwriter.readthedocs.io/format.html#format-set-border
        border_all = {'border': 1} # 1 is the type of the border. will run set_border(1)
        left_and_right = {'left': 1, 'right': 1} #. will run set_left(1) and set_right(1)
        top_and_bot = {'top': 1, 'bot': 1} #. will run set_top(1) and set_bot(1)

        # HEADER STYLE
        self.wbf['header'] = workbook.add_format({
            **text_wrap,
            **align_center,
            **valign_center,
            **bold,
            **font_color_header,
            **bg_color_header,
            **border_all
        })

        self.wbf['header_filter'] = workbook.add_format({
            **text_wrap,
            **align_center,
            **valign_center,
            **bold,
            **font_color_header,
            **bg_color_header,
            **border_all,
            'font_size': 8,
        })

        # CONTENT STYLE
        self.wbf['content'] = workbook.add_format({
            **text_wrap,
            **left_and_right
        })
        
        self.wbf['content_date'] = workbook.add_format({
            **date_format,
            **left_and_right
        })
        
        self.wbf['content_float'] = workbook.add_format({
            **align_right,
            **num_format,
            **left_and_right
        })

        self.wbf['content_center'] = workbook.add_format({
            **align_center,
            **left_and_right
        })

        # SUBTOTAL STYLE
        self.wbf['subtotal_float'] = workbook.add_format({
            **bold,
            **bg_color_subtotal,
            **align_right,
            **font_color_subtotal,
            **num_format,
            **border_all
        })
        
        self.wbf['subtotal'] = workbook.add_format({
            **bold,
            **bg_color_subtotal,
            **font_color_subtotal,
            **border_all
        })

        self.wbf['subtotal_center'] = workbook.add_format({
            **bold,
            **bg_color_subtotal,
            **font_color_subtotal,
            **align_center,
            **border_all
        })

        # GRAND TOTAL STYLE
        self.wbf['total_float'] = workbook.add_format({
            **bold,
            **bg_color_grandtotal,
            **align_right,
            **font_color_grandtotal,
            **num_format,
            **border_all})
        
        self.wbf['total'] = workbook.add_format({
            **bold,
            **bg_color_grandtotal,
            **font_color_grandtotal,
            **border_all})

        self.wbf['total_center'] = workbook.add_format({
            **bold,
            **bg_color_grandtotal,
            **font_color_grandtotal,
            **align_center,
            **border_all
        })
        return workbook
 
    def generate_xlsx_report(self, workbook, data, obj):
        workbook = self.add_workbook_format(workbook)
        wbf=self.wbf

        # HEADER
        # header employee
        worksheet = workbook.add_worksheet("Detail")
        
        grand_total_rows = []
        rekap_contractors = {}
        rekap_contractors2 = {}
        rekap2_sumifs_rcond_col = [0,0,0]
        rekap2_sumifs_rsum_col = []

        next_row = 1
        col = 1
        worksheet.write(next_row, col, 'Tanggal' , wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, 'Kontraktor / Pemborong' , wbf['header'])
        rekap2_sumifs_rcond_col[2] = col
        worksheet.set_column(col,col,30)
        col += 1
        worksheet.write(next_row, col, "Lokasi", wbf['header'])
        rekap2_sumifs_rcond_col[0] = col
        worksheet.set_column(col,col,25)
        col += 1
        worksheet.write(next_row, col, "Aktifitas", wbf['header'])
        rekap2_sumifs_rcond_col[1] = col
        worksheet.set_column(col,col,50)
        col += 1
        worksheet.write(next_row, col, "Hasil 1", wbf['header'])
        rekap2_sumifs_rsum_col.append(col)
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Satuan 1", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Hasil 2", wbf['header'])
        rekap2_sumifs_rsum_col.append(col)
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Satuan 2", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Tarif", wbf['header'])
        worksheet.set_column(col,col,12)
        col += 1
        worksheet.write(next_row, col, "Jumlah", wbf['header'])
        rekap2_sumifs_rsum_col.append(col)
        worksheet.set_column(col,col,15)
        col += 1
        next_row += 1
        
        for c in range(1,col):
            worksheet.write(next_row, c, c, wbf['header_filter'])
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
            if line.get('location_id') not in rekap_contractors2.keys():
                rekap_contractors2.update({line.get('location_id'): []})
            if (line.get('activity_id'),line.get('supplier_id')) not in rekap_contractors2[line.get('location_id')]:
                rekap_contractors2[line.get('location_id')].append((line.get('activity_id'),line.get('supplier_id')))

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
            worksheet.write_formula(next_row, col, f"=SUM({','.join([xl_rowcol_to_cell(grow,col) for grow in grand_total_rows])})", wbf['total_float'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({','.join([xl_rowcol_to_cell(grow,col) for grow in grand_total_rows])})", wbf['total_float'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write_formula(next_row, col, f"=SUM({','.join([xl_rowcol_to_cell(grow,col) for grow in grand_total_rows])})", wbf['total_float'])
            col += 1
            next_row += 1

        worksheet.set_landscape()
        worksheet.set_paper(9)
        worksheet.repeat_rows(1, 2) 
        worksheet.print_area(0, 0, next_row, col+1)
        worksheet.set_print_scale(50)

        ########################################################### SHEET 2
        # HEADER
        # header employee
        worksheet2 = workbook.add_worksheet("Per Lokasi")
        
        rekap2_sumifs_cond_col = []

        next_row = 1
        col = 1
        worksheet2.write(next_row, col, 'Lokasi' , wbf['header'])
        rekap2_sumifs_cond_col.append(col)
        worksheet2.set_column(col,col,25)
        col += 1
        worksheet.freeze_panes(next_row, col)
        worksheet2.write(next_row, col, 'Aktifitas' , wbf['header'])
        rekap2_sumifs_cond_col.append(col)
        worksheet2.set_column(col,col,50)
        col += 1
        worksheet2.write(next_row, col, 'Kontraktor / Pemborong' , wbf['header'])
        rekap2_sumifs_cond_col.append(col)
        worksheet2.set_column(col,col,30)
        col += 1
        worksheet2.write(next_row, col, 'Hasil 1' , wbf['header'])
        worksheet2.set_column(col,col,10)
        col += 1
        worksheet2.write(next_row, col, 'Hasil 2' , wbf['header'])
        worksheet2.set_column(col,col,10)
        col += 1
        worksheet2.write(next_row, col, 'Total' , wbf['header'])
        worksheet2.set_column(col,col,15)
        
        next_row += 1
        grand_total_rows2 = [] 
        for location2, list_act_contr in rekap_contractors2.items():
            sub_first_row = next_row
            for activity_kontraktor in list_act_contr:
                activity2, kontraktor2 = activity_kontraktor
                col = 1
                worksheet2.write(next_row, col, location2[1] if location2 else '', wbf['content'])
                col += 1
                worksheet2.write(next_row, col, activity2[1] if activity2 else '', wbf['content'])
                col += 1
                worksheet2.write(next_row, col, kontraktor2[1] if kontraktor2 else '', wbf['content'])
                col += 1
                worksheet2.write_formula(next_row, col, f"""=SUMIFS(Detail!{xl_col_to_name(rekap2_sumifs_rsum_col[0])}:{xl_col_to_name(rekap2_sumifs_rsum_col[0])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[0])}:{xl_col_to_name(rekap2_sumifs_rcond_col[0])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[0])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[1])}:{xl_col_to_name(rekap2_sumifs_rcond_col[1])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[1])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[2])}:{xl_col_to_name(rekap2_sumifs_rcond_col[2])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[2])})""", wbf['content_float'])
                col += 1
                worksheet2.write_formula(next_row, col, f"""=SUMIFS(Detail!{xl_col_to_name(rekap2_sumifs_rsum_col[1])}:{xl_col_to_name(rekap2_sumifs_rsum_col[1])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[0])}:{xl_col_to_name(rekap2_sumifs_rcond_col[0])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[0])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[1])}:{xl_col_to_name(rekap2_sumifs_rcond_col[1])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[1])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[2])}:{xl_col_to_name(rekap2_sumifs_rcond_col[2])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[2])})""", wbf['content_float'])
                col += 1
                worksheet2.write_formula(next_row, col, f"""=SUMIFS(Detail!{xl_col_to_name(rekap2_sumifs_rsum_col[2])}:{xl_col_to_name(rekap2_sumifs_rsum_col[2])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[0])}:{xl_col_to_name(rekap2_sumifs_rcond_col[0])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[0])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[1])}:{xl_col_to_name(rekap2_sumifs_rcond_col[1])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[1])}, 
                                        Detail!{xl_col_to_name(rekap2_sumifs_rcond_col[2])}:{xl_col_to_name(rekap2_sumifs_rcond_col[2])}, 
                                        {xl_rowcol_to_cell(next_row, rekap2_sumifs_cond_col[2])})""", wbf['content_float'])
                col += 1
                next_row += 1
            col = 1
            worksheet2.write(next_row, col, f"Subtotal: {location2[1] if location2 else ''}", wbf['subtotal'])
            col += 1
            worksheet2.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet2.write(next_row, col, "", wbf['subtotal'])
            col += 1
            worksheet2.write(next_row, col, f"=SUM({xl_rowcol_to_cell(sub_first_row, col)})" if sub_first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(sub_first_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
            col += 1
            worksheet2.write(next_row, col, f"=SUM({xl_rowcol_to_cell(sub_first_row, col)})" if sub_first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(sub_first_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
            col += 1
            worksheet2.write(next_row, col, f"=SUM({xl_rowcol_to_cell(sub_first_row, col)})" if sub_first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(sub_first_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['subtotal_float'])
            col += 1
            grand_total_rows2.append(next_row)
            next_row += 1
        
        if grand_total_rows2:
            col = 1
            worksheet2.write(next_row, col, f"Total", wbf['total'])
            col += 1
            worksheet2.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet2.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet2.write(next_row, col, f"=SUM({','.join([xl_rowcol_to_cell(grow2, col) for grow2 in grand_total_rows2])})", wbf['total_float'])
            col += 1
            worksheet2.write(next_row, col, f"=SUM({','.join([xl_rowcol_to_cell(grow2, col) for grow2 in grand_total_rows2])})", wbf['total_float'])
            col += 1
            worksheet2.write(next_row, col, f"=SUM({','.join([xl_rowcol_to_cell(grow2, col) for grow2 in grand_total_rows2])})", wbf['total_float'])
            col += 1
            grand_total_rows2.append(next_row)
            next_row += 1
        
        # Page Layout
        worksheet2.set_landscape()
        worksheet2.set_paper(9) # A4
        # worksheet2.set_header()
        worksheet2.repeat_rows(1, 2) #Repeat column header
        worksheet2.print_area(0, 0, next_row, col+1)
        worksheet2.set_print_scale(50)

        ########################################################### SHEET 3
        # HEADER
        # header employee
        worksheet3 = workbook.add_worksheet("Per Kontraktor")
        
        next_row = 1
        col = 1
        worksheet3.write(next_row, col, 'No.' , wbf['header'])
        worksheet3.set_column(col,col,5)
        col += 1
        worksheet3.write(next_row, col, 'Kontraktor / Pemborong' , wbf['header'])
        worksheet3.set_column(col,col,30)
        col += 1
        worksheet3.write(next_row, col, 'Total' , wbf['header'])
        worksheet3.set_column(col,col,15)
        col += 1
        worksheet3.write(next_row, col, 'GrossUp Upah' , wbf['header'])
        worksheet3.set_column(col,col,15)
        col += 1
        worksheet3.write(next_row, col, 'PPH 21 Upah' , wbf['header'])
        worksheet3.set_column(col,col,15)
        
        next_row += 1

        indx = 0
        first_row = next_row
        for partner, subtotal_pos in rekap_contractors.items():
            indx += 1
            col = 1
            worksheet3.write(next_row, col, indx, wbf['content_center'])
            col += 1
            worksheet3.write(next_row, col, partner[1], wbf['content'])
            col += 1
            worksheet3.write_formula(next_row, col, f"=Detail!{xl_rowcol_to_cell(subtotal_pos['row'], subtotal_pos['col'])}", wbf['content_float'])
            col += 1
            worksheet3.write_formula(next_row, col, f"={xl_rowcol_to_cell(next_row, col-1)}+({xl_rowcol_to_cell(next_row, col-1)}*2.5/97.5)", wbf['content_float'])
            col += 1
            worksheet3.write_formula(next_row, col, f"={xl_rowcol_to_cell(next_row, col-2)}*2.5/97.5", wbf['content_float'])
            col += 1
            next_row += 1
        if rekap_contractors:
            col = 1
            worksheet3.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet3.write(next_row, col, "Total", wbf['total'])
            col += 1
            worksheet3.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_row, col)})" if first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['total_float'])
            col += 1
            worksheet3.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_row, col)})" if first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['total_float'])
            col += 1
            worksheet3.write_formula(next_row, col, f"=SUM({xl_rowcol_to_cell(first_row, col)})" if first_row==(next_row-1) else f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row-1, col)})", wbf['total_float'])
            col += 1
            next_row += 1
        # Page Layout
        worksheet3.set_landscape()
        worksheet3.set_paper(9) # A4
        # worksheet3.set_header()
        worksheet3.repeat_rows(1, 2) #Repeat column header
        worksheet3.print_area(0, 0, next_row, col+1)
        worksheet3.set_print_scale(50)
