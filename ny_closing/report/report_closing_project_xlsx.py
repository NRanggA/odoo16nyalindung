from odoo import api, models, fields, _
# from odoo.exceptions import Warning
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
from xlsxwriter.utility import xl_rowcol_to_cell

class ProjectClosingReportExcel(models.AbstractModel):
    _name = 'report.ny_closing.project_closing_xlsx'
    _description = "Summary Closing Project"
    _inherit = 'report.report_xlsx.abstract'

    wbf = {}

    # def _get_objs_for_report(self, docids, data):
    #     options = data.get('options', {})
    #     # wizard = self.env['payroll.report.detail.wizard'].browse(options['src_id'])
    #     return wizard.payslip_ids

    def add_workbook_format(self, workbook):
        self.wbf['header'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        self.wbf['header'].set_border()
        self.wbf['header'].set_text_wrap()
        self.wbf['header'].set_align('vcenter')

        self.wbf['header_no'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        self.wbf['header_no'].set_border()
        self.wbf['header_no'].set_font_size(8)
        self.wbf['header_no'].set_align('vcenter')
                
        self.wbf['footer'] = workbook.add_format({'align':'left'})
        self.wbf['footer'].set_bottom()
        
        self.wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        self.wbf['content_datetime'].set_left()
        self.wbf['content_datetime'].set_right()
        
        self.wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        self.wbf['content_date'].set_left()
        self.wbf['content_date'].set_right() 
        
        self.wbf['title_doc'] = workbook.add_format({'bold': 1,'align': 'left'})
        self.wbf['title_doc'].set_font_size(12)
        
        self.wbf['company'] = workbook.add_format({'align': 'left'})
        self.wbf['company'].set_font_size(11)
        
        self.wbf['content'] = workbook.add_format()
        self.wbf['content'].set_left()
        self.wbf['content'].set_right() 
        self.wbf['content'].set_text_wrap()
        
        self.wbf['content_float'] = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        self.wbf['content_float'].set_right() 
        self.wbf['content_float'].set_left()

        self.wbf['content_center'] = workbook.add_format({'align': 'centre'})
        
        self.wbf['content_number'] = workbook.add_format({'align': 'right'})
        self.wbf['content_number'].set_right() 
        self.wbf['content_number'].set_left() 
                
        self.wbf['content_percent'] = workbook.add_format({'align': 'right','num_format': '0.00%'})
        self.wbf['content_percent'].set_right() 
        self.wbf['content_percent'].set_left() 
                
        self.wbf['total_float'] = workbook.add_format({'bold':1,'bg_color': '#FFFFDB','align': 'right','num_format': '#,##0.00'})
        self.wbf['total_float'].set_top()
        self.wbf['total_float'].set_bottom()            
        self.wbf['total_float'].set_left()
        self.wbf['total_float'].set_right()         
        
        self.wbf['total_number'] = workbook.add_format({'align':'right','bg_color': '#FFFFDB','bold':1})
        self.wbf['total_number'].set_top()
        self.wbf['total_number'].set_bottom()            
        self.wbf['total_number'].set_left()
        self.wbf['total_number'].set_right()
        
        self.wbf['total'] = workbook.add_format({'bold':1,'bg_color': '#FFFFDB','align':'center'})
        self.wbf['total'].set_left()
        self.wbf['total'].set_right()
        self.wbf['total'].set_top()
        self.wbf['total'].set_bottom()
        
        return workbook
    
    def generate_xlsx_report(self, workbook, data, obj):
        workbook = self.add_workbook_format(workbook)
        wbf=self.wbf

        ############################################################
        #              HARGA PEROLEHAN PROJECT CIP                 #
        ############################################################
        # HEADER
        # header employee
        worksheet = workbook.add_worksheet("Project CIP")
        
        next_row = 1
        worksheet.merge_range(next_row, 1, next_row+1, 1, 'Code' , wbf['header'])
        worksheet.set_column(1,1,15)
        worksheet.merge_range(next_row, 2, next_row+1, 2, 'Project' , wbf['header'])
        worksheet.set_column(2,2,35)
        worksheet.set_column(3,6,15)
        worksheet.merge_range(next_row-1, 3, next_row-1, 6, 'Alumulasi CIP' , wbf['header'])
        worksheet.merge_range(next_row, 3, next_row+1, 3, 'Saldo Akhir\nTahun Lalu' , wbf['header'])
        worksheet.merge_range(next_row, 4, next_row, 5, 'Tahun Berjalan' , wbf['header'])
        worksheet.write(next_row+1, 4, 'Saldo Awal' , wbf['header'])
        worksheet.write(next_row+1, 5, 'Bulan Ini' , wbf['header'])
        # worksheet.write(next_row+1, 6, 'Penyesuaian' , wbf['header'])
        worksheet.merge_range(next_row, 6, next_row+1, 6, 'Saldo Akhir' , wbf['header'])

        next_row += 2
        for c in range(6):
            worksheet.write(next_row, c+1, c+1, wbf['header'])
        next_row += 1
        start_row = next_row
        worksheet.freeze_panes(next_row, 2)

        for line in obj.closing_project_ids.filtered(lambda l: not l.project_tanaman):
            worksheet.write(next_row, 1, line.project_id.code, wbf['content'])
            worksheet.write(next_row, 2, line.project_id.name, wbf['content'])
            worksheet.write(next_row, 3, line.accumultated_cip_last_year or 0.0, wbf['content_float'])
            worksheet.write(next_row, 4, line.accumultated_cip_this_year or 0.0, wbf['content_float'])
            worksheet.write(next_row, 5, line.total_cost or 0.0, wbf['content_float'])
            # worksheet.write(next_row, 6, line.adjustment_period_cost or 0.0, wbf['content_float'])
            worksheet.write(next_row, 6, line.accumultated_cip_last_year + line.accumultated_cip_this_year + line.total_cost, wbf['content_float'])
            next_row += 1
        
        next_row += 1
        worksheet.write(next_row, 1, "", wbf['total'])
        worksheet.write(next_row, 2, "Total", wbf['total'])
        worksheet.write_formula(next_row, 3, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,3)}:{xl_rowcol_to_cell(next_row-2,3)})", wbf['total_float'])
        worksheet.write_formula(next_row, 4, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,4)}:{xl_rowcol_to_cell(next_row-2,4)})", wbf['total_float'])
        worksheet.write_formula(next_row, 5, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,5)}:{xl_rowcol_to_cell(next_row-2,5)})", wbf['total_float'])
        worksheet.write_formula(next_row, 6, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,6)}:{xl_rowcol_to_cell(next_row-2,6)})", wbf['total_float'])
        # worksheet.write_formula(next_row, 7, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,7)}:{xl_rowcol_to_cell(next_row-2,7)})", wbf['total_float'])
        
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.repeat_rows(1, 4)
        worksheet.print_area(0, 0, next_row, 13)
        worksheet.set_print_scale(78)

        ############################################################
        #            HARGA PEROLEHAN PROJECT TANAM                 #
        ############################################################
        # HEADER
        # header employee
        # worksheet = workbook.add_worksheet("Project Tanaman")
        
        # next_row = 1
        # worksheet.merge_range(next_row, 1, next_row+1, 1, 'ORG' , wbf['header'])
        # worksheet.set_column(1,1,15)
        # worksheet.merge_range(next_row, 2, next_row+1, 2, 'Blok Tanam' , wbf['header'])
        # worksheet.set_column(2,2,35)
        # worksheet.set_column(3,6,15)
        # worksheet.merge_range(next_row-1, 3, next_row-1, 6, 'Harga Perolehan' , wbf['header'])
        # worksheet.merge_range(next_row-1, 3, next_row, 3, 'Saldo Akhir\nTahun Lalu' , wbf['header'])
        # worksheet.merge_range(next_row, 4, next_row, 6, 'Tahun Berjalan' , wbf['header'])
        # worksheet.write(next_row+1, 4, 'Saldo Awal' , wbf['header'])
        # worksheet.write(next_row+1, 5, 'Bulan Ini' , wbf['header'])
        # worksheet.write(next_row+1, 6, 'Penyesuaian' , wbf['header'])
        # # worksheet.write(next_row+1, 7, 'Saldo Akhir' , wbf['header'])
        # worksheet.merge_range(next_row-1, 7, next_row, 7, 'Saldo Akhir' , wbf['header'])

        # next_row += 2
        # for c in range(7):
        #     worksheet.write(next_row, c+1, c+1, wbf['header'])
        # next_row += 1
        # start_row = next_row
        # worksheet.freeze_panes(next_row, 2)

        # for line in obj.closing_plantation_ids.filtered(lambda l: l.status=='tbm').sorted(key=lambda l: l.plant_block_id.varieties_id.id):
        #     worksheet.write(next_row, 1, line.plant_block_id.varieties_id.name, wbf['content'])
        #     worksheet.write(next_row, 2, line.plant_block_id.code, wbf['content'])
        #     # worksheet.write(next_row, 3, line.accumulated_tbm_cost or 0.0, wbf['content_float'])
        #     worksheet.write(next_row, 3, line.accumulated_tbm_cost_last_year or 0.0, wbf['content_float'])
        #     worksheet.write(next_row, 4, line.accumulated_tbm_cost_this_year or 0.0, wbf['content_float'])
        #     worksheet.write(next_row, 5, line.total_cost or 0.0, wbf['content_float'])
        #     worksheet.write(next_row, 6, line.adjustment_period_cost or 0.0, wbf['content_float'])
        #     # worksheet.write(next_row, 7, line.accumulated_tbm_cost + line.total_cost + line.adjustment_period_cost, wbf['content_float'])
        #     worksheet.write(next_row, 7, line.accumulated_tbm_cost_last_year + line.accumulated_tbm_cost_this_year + line.total_cost + line.adjustment_period_cost, wbf['content_float'])
        #     next_row += 1
        
        # next_row += 1
        # worksheet.write(next_row, 1, "", wbf['total'])
        # worksheet.write(next_row, 2, "Total", wbf['total'])
        # worksheet.write_formula(next_row, 3, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,3)}:{xl_rowcol_to_cell(next_row-2,3)})", wbf['total_float'])
        # worksheet.write_formula(next_row, 4, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,4)}:{xl_rowcol_to_cell(next_row-2,4)})", wbf['total_float'])
        # worksheet.write_formula(next_row, 5, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,5)}:{xl_rowcol_to_cell(next_row-2,5)})", wbf['total_float'])
        # worksheet.write_formula(next_row, 6, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,6)}:{xl_rowcol_to_cell(next_row-2,6)})", wbf['total_float'])
        # worksheet.write_formula(next_row, 7, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,7)}:{xl_rowcol_to_cell(next_row-2,7)})", wbf['total_float'])
        
        # worksheet.set_landscape()
        # worksheet.set_paper(9)  # A4
        # worksheet.repeat_rows(1, 4)
        # worksheet.print_area(0, 0, next_row, 13)
        # worksheet.set_print_scale(78)