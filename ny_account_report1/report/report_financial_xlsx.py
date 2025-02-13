from odoo import api, models, _
from odoo.exceptions import Warning
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from xlsxwriter.utility import xl_rowcol_to_cell

class ReportFinancialXlsx(models.Model):
    _name = 'report.ny_account_report1.report_financial2_xlsx'
    _description = 'Financial Report Excel'
    _inherit = 'report.report_xlsx.abstract'

    wbf = {}

    def add_workbook_format(self, workbook):
        self.wbf['header'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#0000000'})
        self.wbf['header'].set_border()
        self.wbf['header'].set_text_wrap()
        self.wbf['header'].set_align('vcenter')

        self.wbf['header_no'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#0000000'})
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
        # heading_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 14})
        workbook = self.add_workbook_format(workbook)
        wbf=self.wbf
        worksheet = workbook.add_worksheet("Financial Report")
        
        report_lines = self.env['report.ny_account_report1.report_financial2'].get_account_lines(data.get('form'))

        # TITLE
        next_row = 1
        worksheet.write(next_row, 1, data['form']['account_report_id'][1], wbf['title_doc'])
        next_row += 2
        if data['form']['target_move']:
            worksheet.write(next_row, 1, "Target Moves", wbf['title_doc'])
            worksheet.write(next_row, 2, "All Entries" if data['form']['target_move']=='all' else "Posted Entries")
            next_row += 1
        if data['form']['date_from']:
            worksheet.write(next_row, 1, "Date From", wbf['title_doc'])
            worksheet.write(next_row, 2, data['form']['date_from'])
            next_row += 1
        if data['form']['date_to']:
            worksheet.write(next_row, 1, "Date To", wbf['title_doc'])
            worksheet.write(next_row, 2, data['form']['date_to'])
            next_row += 1
        
        max_level = max([int(x.get('level',0)) for x in report_lines])
        if data['form']['debit_credit']:
            worksheet.write(next_row, 1, "Name", wbf['header'])
            worksheet.set_column(1,1,60) # width number
            worksheet.write(next_row, 2, "Debit", wbf['header'])
            worksheet.write(next_row, 3, "Credit", wbf['header'])
            worksheet.write(next_row, 4, "Balance", wbf['header'])
            worksheet.set_column(2,4,15) # width number
            next_row += 1
            for a in report_lines:
                if int(a.get('level',0)) in (1,0):
                    content_float_style = workbook.add_format({'font_color': '#000000', 'bold': 1, 'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format({'font_color': '#000000','bold': 1})
                elif not a.get('is_child',False):
                    content_float_style = workbook.add_format({'font_color': '#0d578c', 'bold': 1, 'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format({'font_color': '#0d578c','bold': 1})
                else:
                    content_float_style = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format()
                content_style.set_left()
                content_style.set_right()
                content_style.set_text_wrap()
                content_style.set_indent(int(a.get('level',0)))
                content_float_style.set_right()
                    
                worksheet.write(next_row, 1, a.get('name', ''), content_style)
                worksheet.write(next_row, 2, a.get('debit', 0.0), content_float_style)
                worksheet.write(next_row, 3, a.get('credit', 0.0), content_float_style)
                worksheet.write(next_row, 4, a.get('balance', 0.0), content_float_style)
                next_row += 1
            worksheet.merge_range(next_row, 1, next_row, 4, "", wbf['total_float'])
        elif not data['form']['enable_filter'] and not data['form']['debit_credit']:
            worksheet.write(next_row, 1, "Name", wbf['header'])
            worksheet.set_column(1,1,60) # width number
            worksheet.write(next_row, 2, "Balance", wbf['header'])
            worksheet.set_column(2,2,15) # width number
            next_row += 1
            for a in report_lines:
                if int(a.get('level',0)) in (1,0):
                    content_float_style = workbook.add_format({'font_color': '#000000', 'bold': 1, 'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format({'font_color': '#000000','bold': 1})
                elif not a.get('is_child',False):
                    content_float_style = workbook.add_format({'font_color': '#0d578c', 'bold': 1, 'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format({'font_color': '#0d578c','bold': 1})
                else:
                    content_float_style = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format()
                content_style.set_left()
                content_style.set_right() 
                content_style.set_text_wrap()
                content_style.set_indent(int(a.get('level',0)))
                content_float_style.set_right()
                    
                worksheet.write(next_row, 1, a.get('name', ''), content_style)
                worksheet.write(next_row, 2, a.get('balance', 0.0), content_float_style)
                next_row += 1
            worksheet.merge_range(next_row, 1, next_row, 2, "", wbf['total_float'])
        elif data['form']['enable_filter'] == 1 and not data['form']['debit_credit']:
            worksheet.write(next_row, 1, "Name", wbf['header'])
            worksheet.set_column(1,1,60) # width number
            worksheet.write(next_row, 2, "Balance", wbf['header'])
            worksheet.write(next_row, 3, data['form']['label_filter'], wbf['header'])
            worksheet.set_column(2,3,15) # width number
            next_row += 1
            # # Freeze
            # worksheet.freeze_panes(next_row, 1)
            for a in report_lines:
                if int(a.get('level',0)) in (1,0):
                    content_float_style = workbook.add_format({'font_color': '#000000', 'bold': 1, 'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format({'font_color': '#000000','bold': 1})
                elif not a.get('is_child',False):
                    content_float_style = workbook.add_format({'font_color': '#0d578c', 'bold': 1, 'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format({'font_color': '#0d578c','bold': 1})
                else:
                    content_float_style = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
                    content_style = workbook.add_format()
                content_style.set_left()
                content_style.set_right() 
                content_style.set_text_wrap()
                content_style.set_indent(int(a.get('level',0)))
                content_float_style.set_right()
                    
                worksheet.write(next_row, 1, a.get('name', ''), content_style)
                worksheet.write(next_row, 2, a.get('balance', 0.0), content_float_style)
                worksheet.write(next_row, 3, a.get('balance_cmp', 0.0), content_float_style)
                next_row += 1
            worksheet.merge_range(next_row, 1, next_row, 3, "", wbf['total_float'])
        
        # Page Layout
        worksheet.set_landscape()
        worksheet.set_paper(9) # A4
        # worksheet.set_header()
        worksheet.repeat_rows(1, 2) #Repeat column header
        worksheet.print_area(0, 0, next_row, 4)
        worksheet.set_print_scale(50)

