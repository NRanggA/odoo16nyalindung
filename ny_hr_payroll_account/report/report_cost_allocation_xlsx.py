from odoo import api, models, fields, _
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name

class CostAllocation(models.AbstractModel):
    _name = 'report.ny_hr_payroll_account.payroll_cost_allocation_xlsx'
    _description = "Payroll Cost Allocation Excel"
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
        worksheet = workbook.add_worksheet("Payroll Cost Allocation")
        
        next_row = 1
        col = 1
        worksheet.write(next_row, col, 'Employee' , wbf['header'])
        worksheet.set_column(col,col,40)
        col += 1
        worksheet.write(next_row, col, 'Salary Rule' , wbf['header'])
        worksheet.set_column(col,col,30)
        col += 1
        worksheet.write(next_row, col, "ORG", wbf['header'])
        worksheet.set_column(col,col,20)
        col += 1
        worksheet.write(next_row, col, "Tipe Lokasi", wbf['header'])
        worksheet.set_column(col,col,15)
        col += 1
        worksheet.write(next_row, col, "Lokasi", wbf['header'])
        worksheet.set_column(col,col,25)
        col += 1
        worksheet.write(next_row, col, "Aktifitas", wbf['header'])
        worksheet.set_column(col,col,50)
        col += 1
        worksheet.write(next_row, col, "Account", wbf['header'])
        worksheet.set_column(col,col,50)
        col += 1
        worksheet.write(next_row, col, "Debit", wbf['header'])
        worksheet.set_column(col,col,15)
        col += 1
        worksheet.write(next_row, col, "Credit", wbf['header'])
        worksheet.set_column(col,col,15)
        col += 1
        worksheet.write(next_row, col, "Partner", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        next_row += 1
        
        for c in range(1,col):
            worksheet.write(next_row, c, c, wbf['header_filter'])
        next_row += 1
        worksheet.freeze_panes(next_row, 3)

        for line in obj.payslip_run_ids.cost_map_ids.filtered(lambda l: l.type=='reclass').sorted(key=lambda r: (r.slip_id.id, r.rule_id.sequence, r.id)):
            if line.gc_distribution:
                col = 1
                worksheet.write(next_row, col, line.sudo().slip_id.sudo().employee_id.sudo().name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.sudo().rule_id.name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_varieties_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_type_id.code or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.code or '') + '-' + (line.plantation_activity_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.account_id.name or '') + '-' + (line.plantation_activity_id.account_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.gc_distribution_debit_amount, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, 0.0, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, line.partner_id.name or '', wbf['content'])
                col += 1
                next_row += 1
            elif line.gc_distributed:
                col = 1
                worksheet.write(next_row, col, line.sudo().slip_id.sudo().employee_id.sudo().name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.sudo().rule_id.name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_varieties_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_type_id.code or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.code or '') + '-' + (line.plantation_activity_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.account_id.name or '') + '-' + (line.plantation_activity_id.account_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.debit_amount, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, line.credit_amount, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, line.partner_id.name or '', wbf['content'])
                col += 1
                next_row += 1

                col = 1
                worksheet.write(next_row, col, line.sudo().slip_id.sudo().employee_id.sudo().name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.sudo().rule_id.name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_varieties_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_type_id.code or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.code or '') + '-' + (line.plantation_activity_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.account_id.name or '') + '-' + (line.plantation_activity_id.account_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, 0.0, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, line.gc_distribution_credit_amount, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, line.partner_id.name or '', wbf['content'])
                col += 1
                next_row += 1
            else:
                col = 1
                worksheet.write(next_row, col, line.sudo().slip_id.sudo().employee_id.sudo().name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.sudo().rule_id.name, wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_varieties_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_type_id.code or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.plantation_location_id.name or '', wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.code or '') + '-' + (line.plantation_activity_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, (line.plantation_activity_id.account_id.name or '') + '-' + (line.plantation_activity_id.account_id.name or ''), wbf['content'])
                col += 1
                worksheet.write(next_row, col, line.debit_amount, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, line.credit_amount, wbf['content_float'])
                col += 1
                worksheet.write(next_row, col, line.partner_id.name or '', wbf['content'])
                col += 1
                next_row += 1
        
        worksheet.set_landscape()
        worksheet.set_paper(9)
        worksheet.repeat_rows(1, 2) 
        worksheet.print_area(0, 0, next_row, col+1)
        worksheet.set_print_scale(50)