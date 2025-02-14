from odoo import api, models, _
from odoo.exceptions import Warning


from xlsxwriter.utility import xl_rowcol_to_cell
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class ReportFinancialXlsx(models.Model):
    _name = 'report.ny_account_report1.report_agedpartnerbalance2_xlsx'
    _description = 'Aged Partner Balance Report Excel'
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
                
        self.wbf['content_date'] = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        self.wbf['content_date'].set_left()
        self.wbf['content_date'].set_right() 
        
        self.wbf['title_doc'] = workbook.add_format({'bold': 1,'align': 'left'})
        self.wbf['title_doc'].set_font_size(12)
        
        self.wbf['company'] = workbook.add_format({'align': 'left'})
        self.wbf['company'].set_font_size(11)
        
        self.wbf['content1'] = workbook.add_format({'bold': 1})
        self.wbf['content1'].set_left()
        self.wbf['content1'].set_right() 
        self.wbf['content1'].set_top() 
        self.wbf['content1'].set_bottom() 
        # self.wbf['content1'].set_text_wrap()
        self.wbf['content1'].set_indent(2)

        self.wbf['content2'] = workbook.add_format()
        self.wbf['content2'].set_left()
        self.wbf['content2'].set_right() 
        self.wbf['content2'].set_text_wrap()
        # self.wbf['content2'].set_indent(1)
        
        self.wbf['content_float1'] = workbook.add_format({'bold': 1, 'align': 'right', 'num_format': '#,##0.00;-#,##0.00;'})
        self.wbf['content_float1'].set_right() 
        self.wbf['content_float1'].set_left()
        self.wbf['content_float1'].set_bottom() 
        self.wbf['content_float1'].set_top() 

        self.wbf['content_total'] = workbook.add_format({'bold': 1, 'bg_color': '#FFFFDB', 'align': 'right', 'num_format': '#,##0.00;-#,##0.00;'})
        self.wbf['content_total'].set_right() 
        self.wbf['content_total'].set_left()
        self.wbf['content_total'].set_bottom() 
        self.wbf['content_total'].set_top() 

        self.wbf['content_float2'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00;-#,##0.00;-'})
        self.wbf['content_float2'].set_right() 
        self.wbf['content_float2'].set_left()
        
        self.wbf['content_number2'] = workbook.add_format({'align': 'center', 'num_format': '#,##0;-#,##0;'})
        self.wbf['content_number2'].set_right() 
        self.wbf['content_number2'].set_left() 

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
        
        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        odate_from = datetime.strptime(date_from, '%Y-%m-%d').date()

        if data['form']['result_selection'] == 'customer':
            account_type = ['asset_receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['liability_payable']
        else:
            account_type = ['asset_receivable', 'liability_payable']
        
        partner_ids = data['form']['partner_ids']
        partner_aged, total, partner_move_lines = self.env['report.ny_account_report1.report_agedpartnerbalance2']._get_partner_move_lines(
            account_type, partner_ids, date_from, target_move, data['form']['period_length'])
        
        # TITLE
        print(">>>>>>>>>>>>>>>>>>", data['form'])
        next_row = 1
        # worksheet.write(next_row, 1, data['form']['account_report_id'][1], wbf['title_doc'])
        worksheet.write(next_row, 1, "Aged Partner", wbf['title_doc'])
        next_row += 2
        if data['form']['target_move']:
            worksheet.write(next_row, 1, "Target Moves", wbf['title_doc'])
            worksheet.write(next_row, 2, "All Entries" if data['form']['target_move']=='all' else "Posted Entries")
            next_row += 1
        if data['form']['date_from']:
            worksheet.write(next_row, 1, "Date From", wbf['title_doc'])
            worksheet.write(next_row, 2, data['form']['date_from'])
            next_row += 1
        
        worksheet.write(next_row, 1, "Business Partner", wbf['header'])
        worksheet.write(next_row, 2, "No. Invoice", wbf['header'])
        worksheet.write(next_row, 3, "Open Amount", wbf['header'])
        worksheet.write(next_row, 4, "Date Invoice", wbf['header'])
        worksheet.write(next_row, 5, "Due Date", wbf['header'])
        worksheet.write(next_row, 6, "Days Due", wbf['header'])
        worksheet.write(next_row, 7, "Amount Due", wbf['header'])
        worksheet.write(next_row, 8, data['form']['4']['name'], wbf['header'])
        worksheet.write(next_row, 9, data['form']['3']['name'], wbf['header'])
        worksheet.write(next_row, 10, data['form']['2']['name'], wbf['header'])
        worksheet.write(next_row, 11, data['form']['1']['name'], wbf['header'])
        worksheet.write(next_row, 12, data['form']['0']['name'], wbf['header'])
        next_row += 1

        total_amount = 0
        for partners in partner_aged:
            # worksheet.write(next_row, 1, partners['name'], wbf['content1'])
            worksheet.set_column(1,1,30) # width number
            # worksheet.write(next_row, 2, "", wbf['content1'])
            worksheet.set_column(2,2,20) # width number
            # worksheet.write(next_row, 3, partners['total'], wbf['content_float1'])
            worksheet.set_column(3,13,15) # width number
            # worksheet.write(next_row, 4, "", wbf['content1'])
            # worksheet.write(next_row, 5, "", wbf['content1'])
            # worksheet.write(next_row, 6, "", wbf['content1'])
            # worksheet.write(next_row, 7, partners['direction'], wbf['content_float1'])
            # worksheet.write(next_row, 8, partners['4'], wbf['content_float1'])
            # worksheet.write(next_row, 9, partners['3'], wbf['content_float1'])
            # worksheet.write(next_row, 10, partners['2'], wbf['content_float1'])
            # worksheet.write(next_row, 11, partners['1'], wbf['content_float1'])
            # worksheet.write(next_row, 12, partners['0'], wbf['content_float1'])
            # next_row += 1
            for invoice in partner_move_lines[partners['partner_id']]:
                worksheet.write(next_row, 1, partners['name'], wbf['content2'])
                worksheet.write(next_row, 2, invoice['line'].name or '', wbf['content2'])
                worksheet.write(next_row, 3, invoice['amount'], wbf['content_float2'])
                worksheet.write(next_row, 4, invoice['line'].date, wbf['content_date'])
                due_date = invoice['line'].date_maturity or invoice['line'].date
                worksheet.write(next_row, 5, due_date, wbf['content_date'])
                days_due = 0
                if due_date < odate_from:
                    days_due = (odate_from - due_date).days
                worksheet.write(next_row, 6, days_due, wbf['content_number2'])
                worksheet.write(next_row, 7, 0.0 if invoice['period']==6 else invoice['amount'], wbf['content_float2'])
                worksheet.write(next_row, 8, invoice['amount'] if invoice['period']==5 else 0.0, wbf['content_float2'])
                worksheet.write(next_row, 9, invoice['amount'] if invoice['period']==4 else 0.0, wbf['content_float2'])
                worksheet.write(next_row, 10, invoice['amount'] if invoice['period']==3 else 0.0, wbf['content_float2'])
                worksheet.write(next_row, 11, invoice['amount'] if invoice['period']==2 else 0.0, wbf['content_float2'])
                worksheet.write(next_row, 12, invoice['amount'] if invoice['period']==1 else 0.0, wbf['content_float2'])
                next_row += 1

            worksheet.write(next_row, 1, partners['name'], wbf['content1'])
            worksheet.write(next_row, 2, "", wbf['content1'])
            worksheet.write(next_row, 3, partners['total'], wbf['content_float1'])
            worksheet.write(next_row, 4, "", wbf['content1'])
            worksheet.write(next_row, 5, "", wbf['content1'])
            worksheet.write(next_row, 6, "", wbf['content1'])
            worksheet.write(next_row, 7, partners['direction'], wbf['content_float1'])
            worksheet.write(next_row, 8, partners['4'], wbf['content_float1'])
            worksheet.write(next_row, 9, partners['3'], wbf['content_float1'])
            worksheet.write(next_row, 10, partners['2'], wbf['content_float1'])
            worksheet.write(next_row, 11, partners['1'], wbf['content_float1'])
            worksheet.write(next_row, 12, partners['0'], wbf['content_float1'])
            
            total_amount += partners['total']

            next_row += 1

        # Baris Total
        worksheet.write(next_row, 1, 'TOTAL', wbf['header'])
        worksheet.write(next_row, 2, "", wbf['header'])
        worksheet.write(next_row, 3, total_amount, wbf['content_total'])  
        worksheet.write(next_row, 4, "", wbf['header'])
        worksheet.write(next_row, 5, "", wbf['header'])
        worksheet.write(next_row, 6, "", wbf['header'])
        worksheet.write(next_row, 7, '', wbf['header'])  
        worksheet.write(next_row, 8, '', wbf['header'])
        worksheet.write(next_row, 9, '', wbf['header'])
        worksheet.write(next_row, 10, '', wbf['header'])
        worksheet.write(next_row, 11, '', wbf['header'])
        worksheet.write(next_row, 12, '', wbf['header'])
        next_row += 1
        
        # Page Layout
        worksheet.set_landscape()
        worksheet.set_paper(9) # A4
        # worksheet.set_header()
        worksheet.repeat_rows(1, 2) #Repeat column header
        worksheet.print_area(0, 0, next_row, 4)
        worksheet.set_print_scale(50)

