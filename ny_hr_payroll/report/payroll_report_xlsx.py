from odoo import api, models, fields, _
# from odoo.exceptions import Warning
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta

class WmsInventoryAgingReportExcel(models.AbstractModel):
    _name = 'report.ny_hr_payroll.payroll_report_xlsx'
    _description = "Payroll Report Excel"
    _inherit = 'report.report_xlsx.abstract'

    wbf = {}

    def _get_objs_for_report(self, docids, data):
        options = data.get('options', {})
        wizard = self.env['payroll.report.wizard'].browse(options['src_id'])
        return wizard.payslip_ids

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
        # heading_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 14})
        workbook = self.add_workbook_format(workbook)
        wbf=self.wbf

        # HEADER
        # header employee
        worksheet = workbook.add_worksheet("Payroll")
        
        next_row = 1
        worksheet.merge_range(next_row, 1, next_row+1, 1, 'No.' , wbf['header'])
        worksheet.set_column(1,1,3)
        worksheet.merge_range(next_row, 2, next_row, 7, 'Karyawan' , wbf['header'])
        worksheet.write(next_row+1, 2, "NIP", wbf['header'])
        worksheet.set_column(2,2,15)
        worksheet.write(next_row+1, 3, "Nama", wbf['header'])
        worksheet.set_column(3,3,15)
        worksheet.write(next_row+1, 4, "Kemandoran", wbf['header'])
        worksheet.set_column(4,4,25)
        worksheet.write(next_row+1, 5, "NPWP", wbf['header'])
        worksheet.set_column(5,5,25)
        worksheet.write(next_row+1, 6, "KTP", wbf['header'])
        worksheet.set_column(6,6,26)
        worksheet.write(next_row+1, 7, "Jabatan", wbf['header'])
        worksheet.set_column(7,7,15)
        worksheet.write(next_row+1, 8, "Tgl. Masuk", wbf['header'])
        worksheet.set_column(8,8,10)

        rules_basic = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='BASIC')
        rules_allowance = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='ALW' and 'Premi' not in r.name)
        rules_gross = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='GROSS')
        rules_premi = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='ALW' and 'Premi' in r.name)
        rules_deduction = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='DED')
        rules_net = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='NET')
        cur_col = 9
        if rules_basic:
            if len(rules_basic.ids)>1:
                worksheet.merge_range(next_row, cur_col, next_row, cur_col+len(rules_basic.ids)-1, "Gaji Pokok", wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                for rb in rules_basic.sorted(key=lambda x: x.sequence):
                    worksheet.set_column(cur_col,cur_col,12)
                    worksheet.write(next_row+1, cur_col, rb.name, wbf['header'])
                    cur_col += 1
            else:
                worksheet.merge_range(next_row, cur_col, next_row+1, cur_col, rules_basic.name, wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                cur_col += 1
        if rules_allowance:
            if len(rules_allowance.ids)>1:
                worksheet.merge_range(next_row, cur_col, next_row, cur_col+len(rules_allowance.ids)-1, "Tunjangan", wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                for ra in rules_allowance.sorted(key=lambda x: x.sequence):
                    worksheet.write(next_row+1, cur_col, ra.name, wbf['header'])
                    worksheet.set_column(cur_col,cur_col,12)
                    cur_col += 1
            else:
                worksheet.merge_range(next_row, cur_col, next_row+1, cur_col, rules_allowance.name, wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                cur_col += 1
        
        if rules_premi:
            if len(rules_premi.ids)>1:
                worksheet.merge_range(next_row, cur_col, next_row, cur_col+len(rules_premi.ids)-1, "Premi", wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                for rp in rules_premi.sorted(key=lambda x: x.sequence):
                    worksheet.write(next_row+1, cur_col, rp.name, wbf['header'])
                    worksheet.set_column(cur_col,cur_col,12)
                    cur_col += 1
            else:
                worksheet.merge_range(next_row, cur_col, next_row+1, cur_col, rules_premi.name, wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                cur_col += 1
        
        worksheet.merge_range(next_row, cur_col, next_row+1, cur_col, 'Total Pendapatan\n(Gross)', wbf['header'])
        worksheet.set_column(cur_col,cur_col,15)
        cur_col += 1
        
        if rules_deduction:
            if len(rules_deduction.ids)>1:
                worksheet.merge_range(next_row, cur_col, next_row, cur_col+len(rules_deduction.ids)-1, "Potongan", wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                for rd in rules_deduction.sorted(key=lambda x: x.sequence):
                    worksheet.write(next_row+1, cur_col, rd.name, wbf['header'])
                    worksheet.set_column(cur_col,cur_col,12)
                    cur_col += 1
            else:
                worksheet.merge_range(next_row, cur_col, next_row+1, cur_col, rules_deduction.name, wbf['header'])
                worksheet.set_column(cur_col,cur_col,12)
                cur_col += 1
            
            worksheet.merge_range(next_row, cur_col, next_row+1, cur_col, 'Total Potongan', wbf['header'])
            worksheet.set_column(cur_col,cur_col,12)
            cur_col += 1
        
        worksheet.merge_range(next_row, cur_col, next_row+1, cur_col, 'Dibayarkan (Net)', wbf['header'])
        worksheet.set_column(cur_col,cur_col,12)
        cur_col += 1
        next_row += 2

        for c in range(1,cur_col):
            worksheet.write(next_row, c, c, wbf['header_no'])
        next_row += 1

        # Freeze
        worksheet.freeze_panes(next_row, 4)
        indx = 1
        for payslip in obj:
            worksheet.write(next_row, 1, indx, wbf['content'])
            indx += 1
            worksheet.write(next_row, 2, payslip.employee_id.no_induk or '', wbf['content'])
            worksheet.write(next_row, 3, payslip.employee_id.name or '', wbf['content'])
            worksheet.write(next_row, 4, payslip.employee_id.kemandoran_id.name or '', wbf['content'])
            worksheet.write(next_row, 5, payslip.employee_id.npwp or '', wbf['content'])
            worksheet.write(next_row, 6, payslip.employee_id.identification_id or '', wbf['content'])
            worksheet.write(next_row, 7, payslip.employee_id.job_id.name if payslip.employee_id.job_id else '', wbf['content'])
            worksheet.write(next_row, 8, payslip.employee_id.work_start_date or '', wbf['content_date'])
            
            mapped_line = dict(map(lambda l: (l.salary_rule_id.id, l.total), payslip.line_ids))

            l_cur_col = 9
            for rb in rules_basic.sorted(key=lambda x: x.sequence):
                worksheet.write(next_row, l_cur_col, mapped_line.get(rb.id, 0.0), wbf['content_float'])
                l_cur_col += 1
            for ra in rules_allowance.sorted(key=lambda x: x.sequence):
                worksheet.write(next_row, l_cur_col, mapped_line.get(ra.id, 0.0), wbf['content_float'])
                l_cur_col += 1
            for rp in rules_premi.sorted(key=lambda x: x.sequence):
                worksheet.write(next_row, l_cur_col, mapped_line.get(rp.id, 0.0), wbf['content_float'])
                l_cur_col += 1
            
            worksheet.write(next_row, l_cur_col, mapped_line.get(rules_gross.id, 0.0), wbf['content_float'])
            l_cur_col += 1
            
            total_potongan = 0.0
            for rd in rules_deduction.sorted(key=lambda x: x.sequence):
                worksheet.write(next_row, l_cur_col, mapped_line.get(rd.id, 0.0), wbf['content_float'])
                total_potongan += mapped_line.get(rd.id, 0.0)
                l_cur_col += 1

            worksheet.write(next_row, l_cur_col, total_potongan, wbf['content_float'])
            l_cur_col += 1
            
            worksheet.write(next_row, l_cur_col, mapped_line.get(rules_net.id, 0.0), wbf['content_float'])
            l_cur_col += 1
            
            next_row+=1

        # Page Layout
        worksheet.set_landscape()
        worksheet.set_paper(9) # A4
        # worksheet.set_header()
        worksheet.repeat_rows(1, 2) #Repeat column header
        worksheet.print_area(0, 0, next_row, cur_col)
        worksheet.set_print_scale(50)

        # worksheet2 = workbook.add_worksheet("Rekap")
        ########################################################### SHEET 2
        # HEADER
        # header employee
        worksheet2 = workbook.add_worksheet("Rekap Gaji")
        
        next_row = 1
        worksheet2.merge_range(next_row, 1, next_row+1, 1, 'No.' , wbf['header'])
        worksheet2.set_column(1,1,3)
        worksheet2.merge_range(next_row, 2, next_row+1, 2, 'Kemandoran' , wbf['header'])
        # worksheet2.write(next_row+1, 2, "Kemandoran", wbf['header'])
        worksheet2.set_column(2,2,25)
        
        rules_basic2 = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='BASIC')
        rules_allowance2 = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='ALW' and 'Premi' not in r.name)
        rules_gross2 = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='GROSS')
        rules_premi2 = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='ALW' and 'Premi' in r.name)
        rules_deduction2 = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='DED')
        rules_net2 = obj.line_ids.salary_rule_id.filtered(lambda r: r.appears_on_payslip and r.category_id.code=='NET')
        cur_col = 3
        if rules_basic2:
            if len(rules_basic2.ids)>1:
                worksheet2.merge_range(next_row, cur_col, next_row, cur_col+len(rules_basic2.ids)-1, "Gaji Pokok", wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                for rb in rules_basic2.sorted(key=lambda x: x.sequence):
                    worksheet2.set_column(cur_col,cur_col,12)
                    worksheet2.write(next_row+1, cur_col, rb.name, wbf['header'])
                    cur_col += 1
            else:
                worksheet2.merge_range(next_row, cur_col, next_row+1, cur_col, rules_basic2.name, wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                cur_col += 1
        if rules_allowance2:
            if len(rules_allowance2.ids)>1:
                worksheet2.merge_range(next_row, cur_col, next_row, cur_col+len(rules_allowance2.ids)-1, "Tunjangan", wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                for ra in rules_allowance2.sorted(key=lambda x: x.sequence):
                    worksheet2.write(next_row+1, cur_col, ra.name, wbf['header'])
                    worksheet2.set_column(cur_col,cur_col,12)
                    cur_col += 1
            else:
                worksheet2.merge_range(next_row, cur_col, next_row+1, cur_col, rules_allowance2.name, wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                cur_col += 1
        
        if rules_premi2:
            if len(rules_premi2.ids)>1:
                worksheet2.merge_range(next_row, cur_col, next_row, cur_col+len(rules_premi2.ids)-1, "Premi", wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                for rp in rules_premi2.sorted(key=lambda x: x.sequence):
                    worksheet2.write(next_row+1, cur_col, rp.name, wbf['header'])
                    worksheet2.set_column(cur_col,cur_col,12)
                    cur_col += 1
            else:
                worksheet2.merge_range(next_row, cur_col, next_row+1, cur_col, rules_premi2.name, wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                cur_col += 1
        
        worksheet2.merge_range(next_row, cur_col, next_row+1, cur_col, 'Total Pendapatan\n(Gross)', wbf['header'])
        worksheet2.set_column(cur_col,cur_col,15)
        cur_col += 1
        
        if rules_deduction2:
            if len(rules_deduction2.ids)>1:
                worksheet2.merge_range(next_row, cur_col, next_row, cur_col+len(rules_deduction2.ids)-1, "Potongan", wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                for rd in rules_deduction2.sorted(key=lambda x: x.sequence):
                    worksheet2.write(next_row+1, cur_col, rd.name, wbf['header'])
                    worksheet2.set_column(cur_col,cur_col,12)
                    cur_col += 1
            else:
                worksheet2.merge_range(next_row, cur_col, next_row+1, cur_col, rules_deduction2.name, wbf['header'])
                worksheet2.set_column(cur_col,cur_col,12)
                cur_col += 1
            
            worksheet2.merge_range(next_row, cur_col, next_row+1, cur_col, 'Total Potongan', wbf['header'])
            worksheet2.set_column(cur_col,cur_col,12)
            cur_col += 1
        
        worksheet2.merge_range(next_row, cur_col, next_row+1, cur_col, 'Dibayarkan (Net)', wbf['header'])
        worksheet2.set_column(cur_col,cur_col,12)
        cur_col += 1
        next_row += 2

        for c in range(1,cur_col):
            worksheet2.write(next_row, c, c, wbf['header_no'])
        next_row += 1

        # Freeze
        worksheet2.freeze_panes(next_row, 4)
        indx = 1
        for kemandoran in obj.employee_id.kemandoran_id:
            worksheet2.write(next_row, 1, indx, wbf['content'])
            indx += 1
            worksheet2.write(next_row, 2, kemandoran.name or '', wbf['content'])
            payslips = obj.filtered(lambda p : p.employee_id.kemandoran_id.id==kemandoran.id)
            mapped_line = {}
            for line in payslips.line_ids:
                if line.salary_rule_id.id not in mapped_line.keys():
                    mapped_line.update({line.salary_rule_id.id: 0.0})
                mapped_line[line.salary_rule_id.id] += line.total

            l_cur_col = 3
            for rb in rules_basic2.sorted(key=lambda x: x.sequence):
                worksheet2.write(next_row, l_cur_col, mapped_line.get(rb.id, 0.0), wbf['content_float'])
                l_cur_col += 1
            for ra in rules_allowance2.sorted(key=lambda x: x.sequence):
                worksheet2.write(next_row, l_cur_col, mapped_line.get(ra.id, 0.0), wbf['content_float'])
                l_cur_col += 1
            for rp in rules_premi2.sorted(key=lambda x: x.sequence):
                worksheet2.write(next_row, l_cur_col, mapped_line.get(rp.id, 0.0), wbf['content_float'])
                l_cur_col += 1
            
            worksheet2.write(next_row, l_cur_col, mapped_line.get(rules_gross2.id, 0.0), wbf['content_float'])
            l_cur_col += 1
            
            total_potongan = 0.0
            for rd in rules_deduction2.sorted(key=lambda x: x.sequence):
                worksheet2.write(next_row, l_cur_col, mapped_line.get(rd.id, 0.0), wbf['content_float'])
                total_potongan += mapped_line.get(rd.id, 0.0)
                l_cur_col += 1
            
            worksheet2.write(next_row, l_cur_col, total_potongan, wbf['content_float'])
            l_cur_col += 1
            
            worksheet2.write(next_row, l_cur_col, mapped_line.get(rules_net2.id, 0.0), wbf['content_float'])
            l_cur_col += 1
            
            next_row+=1

        # Page Layout
        worksheet2.set_landscape()
        worksheet2.set_paper(9) # A4
        # worksheet2.set_header()
        worksheet2.repeat_rows(1, 2) #Repeat column header
        worksheet2.print_area(0, 0, next_row, cur_col)
        worksheet2.set_print_scale(50)
