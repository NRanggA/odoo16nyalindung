from odoo import api, models, fields, _
# from odoo.exceptions import Warning
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
from xlsxwriter.utility import xl_rowcol_to_cell

class PlantationClosingReportExcel(models.AbstractModel):
    _name = 'report.ny_closing.plantation_closing_xlsx'
    _description = "Summery Closing Plantation"
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
    
    def _query_longterm_tm_tbm(self, data, obj):
        query = f"""
            SELECT
                pv.id as org_id,
                pv.name as org,
                lpb.id as location_id,
                lpb.name as location,
                cp.status,
                SUM(CASE WHEN cp.status='tbm' THEN cpl.total_cost ELSE 0 END) as tbm_value,
                SUM(CASE WHEN cp.status='tm' and caa.name->>'en_US'~'BIAYA PANEN' THEN cpl.total_cost ELSE 0 END) as cost_panen,
                SUM(CASE WHEN cp.status='tm' and caa.name->>'en_US'~'BIAYA RAWAT' THEN cpl.total_cost ELSE 0 END) as cost_rawat,
                SUM(CASE WHEN cp.status='tm' and caa.name->>'en_US'!~'BIAYA PANEN' and caa.name->>'en_US'!~'BIAYA RAWAT' THEN cpl.total_cost ELSE 0 END) as cost_other1,
                SUM(CASE WHEN caj.name->>'en_US' IN ('LHM Payroll','Buku Kontraktor') and caa.name->>'en_US'~'BIAYA PANEN' THEN cpl.total_cost ELSE 0 END) as cost_manpower_panen,
                SUM(CASE WHEN caj.name->>'en_US' IN ('LHM Payroll','Buku Kontraktor') and caa.name->>'en_US'~'BIAYA RAWAT' THEN cpl.total_cost ELSE 0 END) as cost_manpower_rawat,
                SUM(CASE WHEN caj.name->>'en_US'='INVENTORY JOURNAL' THEN cpl.total_cost ELSE 0 END) as cost_material,
                SUM(CASE WHEN 
                            caj.name->>'en_US' NOT IN ('LHM Payroll','Buku Kontraktor','INVENTORY JOURNAL')
                            or (caj.name->>'en_US' IN ('LHM Payroll','Buku Kontraktor') and caa.name->>'en_US'!~'BIAYA PANEN' and caa.name->>'en_US'!~'BIAYA RAWAT')
                        THEN cpl.total_cost ELSE 0 END) as cost_other2,
                SUM(cpl.total_cost) as total_cost
            FROM
                closing_plantation cp
                INNER JOIN closing_plantation_line cpl ON cpl.closing_id=cp.id
                INNER JOIN lhm_plant_block lpb ON lpb.id=cp.plant_block_id
                INNER JOIN plant_varieties pv ON pv.id=lpb.varieties_id
                INNER JOIN lhm_activity lact ON lact.id=cpl.plantation_activity_id
                INNER JOIN account_account caa ON caa.id=lact.cost_account_id
                INNER JOIN account_journal caj ON caj.id=cpl.plantation_src_journal_id
            WHERE
                cp.closing_process_id = {obj.id}
                and cp.type_of_plant = 'longterm_tbm_tm'
            GROUP BY
                pv.id, pv.name, lpb.id, lpb.name, cp.status
            ORDER BY
                pv.id, cp.status, lpb.id
        """
        return query
 
    def _query_longterm_season(self, data, obj):
        query1 = f"""
            SELECT
                pv.id as org_id,
                pv.name as org,
                lpb.id as location_id,
                lpb.name as location,
                cp.status,
                SUM(CASE WHEN cp.status='tbm' THEN cpl.total_cost ELSE 0 END) as tbm_value,
                SUM(CASE WHEN cp.status='tm' and cpl.to_be_deferred=true THEN cpl.total_cost ELSE 0 END) as prepaid_value,
                SUM(CASE WHEN cp.status='tm' and cpl.to_be_deferred=false and caa.name->>'en_US'~'BIAYA PANEN' THEN cpl.total_cost ELSE 0 END) as cost_panen1,
                SUM(CASE WHEN cp.status='tm' and cpl.to_be_deferred=false and caa.name->>'en_US'~'BIAYA RAWAT' THEN cpl.total_cost ELSE 0 END) as cost_rawat1,
                SUM(CASE WHEN cp.status='tm' and cpl.to_be_deferred=false and caa.name->>'en_US'!~'BIAYA PANEN' and caa.name->>'en_US'!~'BIAYA RAWAT' THEN cpl.total_cost ELSE 0 END) as cost_other1,
                SUM(CASE WHEN caj.name->>'en_US' IN ('LHM Payroll','Buku Kontraktor') and caa.name->>'en_US'~'BIAYA PANEN' THEN cpl.total_cost ELSE 0 END) as cost_manpower_panen1,
                SUM(CASE WHEN caj.name->>'en_US' IN ('LHM Payroll','Buku Kontraktor') and caa.name->>'en_US'~'BIAYA RAWAT' THEN cpl.total_cost ELSE 0 END) as cost_manpower_rawat1,
                SUM(CASE WHEN caj.name->>'en_US'='INVENTORY JOURNAL' THEN cpl.total_cost ELSE 0 END) as cost_material,
                SUM(CASE WHEN 
                        caj.name->>'en_US' NOT IN ('LHM Payroll','Buku Kontraktor','INVENTORY JOURNAL') 
                        or (caj.name->>'en_US' IN ('LHM Payroll','Buku Kontraktor') and caa.name->>'en_US'!~'BIAYA PANEN' and caa.name->>'en_US'!~'BIAYA RAWAT')
                    THEN cpl.total_cost ELSE 0 END) as cost_other2,
                SUM(cpl.total_cost) as total_cost1,
                SUM(0) as cost_panen2,
                SUM(0) as cost_rawat2,
                SUM(0) as cost_other3,
                SUM(0) as total_cost2
            FROM
                closing_plantation cp
                INNER JOIN closing_plantation_line cpl ON cpl.closing_id=cp.id
                INNER JOIN lhm_plant_block lpb ON lpb.id=cp.plant_block_id
                INNER JOIN plant_varieties pv ON pv.id=lpb.varieties_id
                INNER JOIN lhm_activity lact ON lact.id=cpl.plantation_activity_id
                INNER JOIN account_account caa ON caa.id=lact.cost_account_id
                INNER JOIN account_journal caj ON caj.id=cpl.plantation_src_journal_id
            WHERE
                cp.closing_process_id = {obj.id}
                and cp.type_of_plant = 'longterm_seasonal'
            GROUP BY
                pv.id, pv.name, lpb.id, lpb.name, cp.status
            ORDER BY
                pv.id, cp.status, lpb.id
        """
        query2 = f"""
            SELECT
                pv.id as org_id,
                pv.name as org,
                lpb.id as location_id,
                lpb.name as location,
                cp.status,
                SUM(0) as tbm_value,
                SUM(0) as prepaid_value,
                SUM(0) as cost_panen1,
                SUM(0) as cost_rawat1,
                SUM(0) as cost_other1,
                SUM(0) as cost_manpower_panen1,
                SUM(0) as cost_manpower_rawat1,
                SUM(0) as cost_material,
                SUM(0) as cost_other2,
                SUM(0) as total_cost1,
                SUM(CASE WHEN caa.name->>'en_US'~'BIAYA PANEN' and cpd.cost_to_post>0 THEN cpd.cost_to_post ELSE 0 END) as cost_panen2,
                SUM(CASE WHEN caa.name->>'en_US'~'BIAYA RAWAT' and cpd.cost_to_post>0 THEN cpd.cost_to_post ELSE 0 END) as cost_rawat2,
                SUM(CASE WHEN caa.name->>'en_US'!~'BIAYA PANEN' and caa.name->>'en_US'!~'BIAYA RAWAT' and cpd.cost_to_post>0 THEN cpd.cost_to_post ELSE 0 END) as cost_other3,
                SUM(CASE WHEN cpd.cost_to_post>0 THEN cpd.cost_to_post ELSE 0 END) as total_cost2
            FROM
                closing_plantation cp
                INNER JOIN closing_plantation_deferred cpd ON cpd.closing_id=cp.id
                INNER JOIN lhm_plant_block lpb ON lpb.id=cp.plant_block_id
                INNER JOIN plant_varieties pv ON pv.id=lpb.varieties_id
                INNER JOIN lhm_activity lact ON lact.id=cpd.plantation_activity_id
                INNER JOIN account_account caa ON caa.id=lact.cost_account_id
                INNER JOIN account_journal caj ON caj.id=cpd.plantation_src_journal_id
            WHERE
                cp.closing_process_id = {obj.id}
                and cp.type_of_plant = 'longterm_seasonal'
            GROUP BY
                pv.id, pv.name, lpb.id, lpb.name, cp.status
            ORDER BY
                pv.id, cp.status, lpb.id
        """
        query = f"""
            SELECT 
                org_id, org, location_id, location, status, 
                sum(tbm_value) as tbm_value,
                sum(prepaid_value) as prepaid_value,
                sum(cost_panen1) as cost_panen1,
                sum(cost_rawat1) as cost_rawat1,
                sum(cost_other1) as cost_other1,
                sum(cost_manpower_panen1) as cost_manpower_panen1,
                sum(cost_manpower_rawat1) as cost_manpower_rawat1,
                sum(cost_material) as cost_material,
                sum(cost_other2) as cost_other2,
                sum(total_cost1) as total_cost1,
                sum(cost_panen2) as cost_panen2,
                sum(cost_rawat2) as cost_rawat2,
                sum(cost_other3) as cost_other3,
                sum(total_cost2) as total_cost2
            FROM (
                ({query1})
                UNION ALL
                ({query2})
            ) sub
            GROUP BY org_id, org, location_id, location, status
            ORDER BY org_id, status, location_id
        """
        return query
 

    def generate_xlsx_report(self, workbook, data, obj):
        workbook = self.add_workbook_format(workbook)
        wbf=self.wbf

        ############################################################
        #                     Longterm Plant                       #
        ############################################################
        # HEADER
        # header employee
        worksheet = workbook.add_worksheet("Jangka Panjang")
        
        next_row = 1
        worksheet.merge_range(next_row, 1, next_row+1, 1, 'ORG' , wbf['header'])
        worksheet.set_column(1,1,15)
        worksheet.merge_range(next_row, 2, next_row+1, 2, 'Blok Tanam' , wbf['header'])
        worksheet.set_column(2,2,35)
        worksheet.merge_range(next_row, 3, next_row+1, 3, 'Status' , wbf['header'])
        worksheet.set_column(3,3,7)
        worksheet.set_column(4,13,15)
        worksheet.merge_range(next_row, 4, next_row, 7, 'Hasil Alokasi' , wbf['header'])
        worksheet.write(next_row+1, 4, 'Harga Perolehan' , wbf['header'])
        worksheet.write(next_row+1, 5, 'Biaya Panen' , wbf['header'])
        worksheet.write(next_row+1, 6, 'Biaya Rawat' , wbf['header'])
        worksheet.write(next_row+1, 7, 'Biaya Lainnya' , wbf['header'])
        worksheet.merge_range(next_row, 8, next_row+1, 8, 'Total' , wbf['header'])
        worksheet.merge_range(next_row, 9, next_row, 12, 'Asal Biaya' , wbf['header'])
        worksheet.write(next_row+1, 9, 'Biaya Pekerja Panen' , wbf['header'])
        worksheet.write(next_row+1, 10, 'Biaya Pekerja Rawat' , wbf['header'])
        worksheet.write(next_row+1, 11, 'Biaya Material' , wbf['header'])
        worksheet.write(next_row+1, 12, 'Biaya Lainnya' , wbf['header'])
        worksheet.merge_range(next_row, 13, next_row+1, 13, 'Total' , wbf['header'])

        next_row += 2
        for c in range(13):
            worksheet.write(next_row, c+1, c+1, wbf['header'])
        next_row += 1
        start_row = next_row
        worksheet.freeze_panes(next_row, 4)

        self.env.cr.execute(self._query_longterm_tm_tbm(data, obj))
        for line in self.env.cr.dictfetchall():
            worksheet.write(next_row, 1, line.get('org',''), wbf['content'])
            worksheet.write(next_row, 2, line.get('location',''), wbf['content'])
            worksheet.write(next_row, 3, line.get('status',''), wbf['content'])
            worksheet.write(next_row, 4, line.get('tbm_value',0.0), wbf['content_float'])
            worksheet.write(next_row, 5, line.get('cost_panen',0.0), wbf['content_float'])
            worksheet.write(next_row, 6, line.get('cost_rawat',0.0), wbf['content_float'])
            worksheet.write(next_row, 7, line.get('cost_other1',0.0), wbf['content_float'])
            worksheet.write(next_row, 8, line.get('total_cost',0.0), wbf['content_float'])
            worksheet.write(next_row, 9, line.get('cost_manpower_panen',0.0), wbf['content_float'])
            worksheet.write(next_row,10, line.get('cost_manpower_rawat',0.0), wbf['content_float'])
            worksheet.write(next_row,11, line.get('cost_material',0.0), wbf['content_float'])
            worksheet.write(next_row,12, line.get('cost_other2',0.0), wbf['content_float'])
            worksheet.write(next_row,13, line.get('total_cost',0.0), wbf['content_float'])
            next_row += 1
        
        next_row += 1
        worksheet.write(next_row, 1, "", wbf['total'])
        worksheet.write(next_row, 2, "Total", wbf['total'])
        worksheet.write(next_row, 3, "", wbf['total'])
        worksheet.write_formula(next_row, 4, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,4)}:{xl_rowcol_to_cell(next_row-2,4)})", wbf['total_float'])
        worksheet.write_formula(next_row, 5, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,5)}:{xl_rowcol_to_cell(next_row-2,5)})", wbf['total_float'])
        worksheet.write_formula(next_row, 6, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,6)}:{xl_rowcol_to_cell(next_row-2,6)})", wbf['total_float'])
        worksheet.write_formula(next_row, 7, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,7)}:{xl_rowcol_to_cell(next_row-2,7)})", wbf['total_float'])
        worksheet.write_formula(next_row, 8, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,8)}:{xl_rowcol_to_cell(next_row-2,8)})", wbf['total_float'])
        worksheet.write_formula(next_row, 9, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,9)}:{xl_rowcol_to_cell(next_row-2,9)})", wbf['total_float'])
        worksheet.write_formula(next_row,10, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,10)}:{xl_rowcol_to_cell(next_row-2,10)})", wbf['total_float'])
        worksheet.write_formula(next_row,11, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,11)}:{xl_rowcol_to_cell(next_row-2,11)})", wbf['total_float'])
        worksheet.write_formula(next_row,12, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,12)}:{xl_rowcol_to_cell(next_row-2,12)})", wbf['total_float'])
        worksheet.write_formula(next_row,13, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,13)}:{xl_rowcol_to_cell(next_row-2,13)})", wbf['total_float'])
        
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.repeat_rows(1, 4)
        worksheet.print_area(0, 0, next_row, 14)
        worksheet.set_print_scale(78)

        ############################################################
        #                     Longterm Seasonal                    #
        ############################################################
        # HEADER
        # header employee
        worksheet = workbook.add_worksheet("Jangka Pendek")
        
        next_row = 1
        worksheet.merge_range(next_row, 1, next_row+1, 1, 'ORG' , wbf['header'])
        worksheet.set_column(1,1,15)
        worksheet.merge_range(next_row, 2, next_row+1, 2, 'Blok Tanam' , wbf['header'])
        worksheet.set_column(2,2,35)
        worksheet.merge_range(next_row, 3, next_row+1, 3, 'Status' , wbf['header'])
        worksheet.set_column(3,3,7)
        worksheet.set_column(4,18,15)
        worksheet.merge_range(next_row, 4, next_row, 8, 'Hasil Alokasi' , wbf['header'])
        worksheet.write(next_row+1, 4, 'Harga Perolehan' , wbf['header'])
        worksheet.write(next_row+1, 5, 'Prepaid Biaya' , wbf['header'])
        worksheet.write(next_row+1, 6, 'Biaya Panen' , wbf['header'])
        worksheet.write(next_row+1, 7, 'Biaya Rawat' , wbf['header'])
        worksheet.write(next_row+1, 8, 'Biaya Lainnya' , wbf['header'])
        worksheet.merge_range(next_row, 9, next_row+1, 9, 'Total' , wbf['header'])
        worksheet.merge_range(next_row, 10, next_row, 13, 'Asal Biaya' , wbf['header'])
        worksheet.write(next_row+1, 10, 'Biaya Pekerja Panen' , wbf['header'])
        worksheet.write(next_row+1, 11, 'Biaya Pekerja Rawat' , wbf['header'])
        worksheet.write(next_row+1, 12, 'Biaya Material' , wbf['header'])
        worksheet.write(next_row+1, 13, 'Biaya Lainnya' , wbf['header'])
        worksheet.merge_range(next_row, 14, next_row+1, 14, 'Total' , wbf['header'])
        worksheet.merge_range(next_row, 15, next_row, 17, 'Prepaid yang dibiayakan' , wbf['header'])
        worksheet.write(next_row+1, 15, 'Biaya Panen' , wbf['header'])
        worksheet.write(next_row+1, 16, 'Biaya Rawat' , wbf['header'])
        worksheet.write(next_row+1, 17, 'Biaya Lainnya' , wbf['header'])
        worksheet.merge_range(next_row, 18, next_row+1, 18, 'Total' , wbf['header'])

        next_row += 2
        for c in range(18):
            worksheet.write(next_row, c+1, c+1, wbf['header'])
        next_row += 1
        start_row = next_row
        worksheet.freeze_panes(next_row, 4)

        self.env.cr.execute(self._query_longterm_season(data, obj))
        for line in self.env.cr.dictfetchall():
            worksheet.write(next_row, 1, line.get('org',''), wbf['content'])
            worksheet.write(next_row, 2, line.get('location',''), wbf['content'])
            worksheet.write(next_row, 3, line.get('status',''), wbf['content'])
            worksheet.write(next_row, 4, line.get('tbm_value',0.0), wbf['content_float'])
            worksheet.write(next_row, 5, line.get('prepaid_value',0.0), wbf['content_float'])
            worksheet.write(next_row, 6, line.get('cost_panen1',0.0), wbf['content_float'])
            worksheet.write(next_row, 7, line.get('cost_rawat1',0.0), wbf['content_float'])
            worksheet.write(next_row, 8, line.get('cost_other1',0.0), wbf['content_float'])
            worksheet.write(next_row, 9, line.get('total_cost1',0.0), wbf['content_float'])
            worksheet.write(next_row,10, line.get('cost_manpower_panen1',0.0), wbf['content_float'])
            worksheet.write(next_row,11, line.get('cost_manpower_rawat1',0.0), wbf['content_float'])
            worksheet.write(next_row,12, line.get('cost_material',0.0), wbf['content_float'])
            worksheet.write(next_row,13, line.get('cost_other2',0.0), wbf['content_float'])
            worksheet.write(next_row,14, line.get('total_cost1',0.0), wbf['content_float'])
            worksheet.write(next_row,15, line.get('cost_panen2',0.0), wbf['content_float'])
            worksheet.write(next_row,16, line.get('cost_rawat2',0.0), wbf['content_float'])
            worksheet.write(next_row,17, line.get('cost_other3',0.0), wbf['content_float'])
            worksheet.write(next_row,18, line.get('total_cost2',0.0), wbf['content_float'])
            next_row += 1
        
        next_row += 1
        worksheet.write(next_row, 1, "", wbf['total'])
        worksheet.write(next_row, 2, "Total", wbf['total'])
        worksheet.write(next_row, 3, "", wbf['total'])
        worksheet.write_formula(next_row, 4, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,4)}:{xl_rowcol_to_cell(next_row-2,4)})", wbf['total_float'])
        worksheet.write_formula(next_row, 5, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,5)}:{xl_rowcol_to_cell(next_row-2,5)})", wbf['total_float'])
        worksheet.write_formula(next_row, 6, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,6)}:{xl_rowcol_to_cell(next_row-2,6)})", wbf['total_float'])
        worksheet.write_formula(next_row, 7, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,7)}:{xl_rowcol_to_cell(next_row-2,7)})", wbf['total_float'])
        worksheet.write_formula(next_row, 8, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,8)}:{xl_rowcol_to_cell(next_row-2,8)})", wbf['total_float'])
        worksheet.write_formula(next_row, 9, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,9)}:{xl_rowcol_to_cell(next_row-2,9)})", wbf['total_float'])
        worksheet.write_formula(next_row,10, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,10)}:{xl_rowcol_to_cell(next_row-2,10)})", wbf['total_float'])
        worksheet.write_formula(next_row,11, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,11)}:{xl_rowcol_to_cell(next_row-2,11)})", wbf['total_float'])
        worksheet.write_formula(next_row,12, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,12)}:{xl_rowcol_to_cell(next_row-2,12)})", wbf['total_float'])
        worksheet.write_formula(next_row,13, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,13)}:{xl_rowcol_to_cell(next_row-2,13)})", wbf['total_float'])
        worksheet.write_formula(next_row,14, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,14)}:{xl_rowcol_to_cell(next_row-2,14)})", wbf['total_float'])
        worksheet.write_formula(next_row,15, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,15)}:{xl_rowcol_to_cell(next_row-2,15)})", wbf['total_float'])
        worksheet.write_formula(next_row,16, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,16)}:{xl_rowcol_to_cell(next_row-2,16)})", wbf['total_float'])
        worksheet.write_formula(next_row,17, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,17)}:{xl_rowcol_to_cell(next_row-2,17)})", wbf['total_float'])
        worksheet.write_formula(next_row,18, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,18)}:{xl_rowcol_to_cell(next_row-2,18)})", wbf['total_float'])
        
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.repeat_rows(1, 4)
        worksheet.print_area(0, 0, next_row, 19)
        worksheet.set_print_scale(78)

        ############################################################
        #                     HARGA PEROLEHAN                      #
        ############################################################
        # HEADER
        # header employee
        worksheet = workbook.add_worksheet("Harga Perolehan")
        
        next_row = 1
        worksheet.merge_range(next_row, 1, next_row+1, 1, 'ORG' , wbf['header'])
        worksheet.set_column(1,1,15)
        worksheet.merge_range(next_row, 2, next_row+1, 2, 'Blok Tanam' , wbf['header'])
        worksheet.set_column(2,2,35)
        worksheet.set_column(3,7,15)
        worksheet.merge_range(next_row-1, 3, next_row-1, 7, 'Harga Perolehan' , wbf['header'])
        worksheet.merge_range(next_row, 3, next_row+1, 3, 'Saldo Akhir\nTahun Lalu' , wbf['header'])
        worksheet.merge_range(next_row, 4, next_row, 6, 'Tahun Berjalan' , wbf['header'])
        worksheet.write(next_row+1, 4, 'Saldo Awal' , wbf['header'])
        worksheet.write(next_row+1, 5, 'Bulan Ini' , wbf['header'])
        worksheet.write(next_row+1, 6, 'Penyesuaian' , wbf['header'])
        # worksheet.write(next_row+1, 7, 'Saldo Akhir' , wbf['header'])
        worksheet.merge_range(next_row, 7, next_row+1, 7, 'Saldo Akhir' , wbf['header'])

        next_row += 2
        for c in range(7):
            worksheet.write(next_row, c+1, c+1, wbf['header'])
        next_row += 1
        start_row = next_row
        worksheet.freeze_panes(next_row, 2)

        for line in obj.closing_plantation_ids.filtered(lambda l: l.status=='tbm').sorted(key=lambda l: l.plant_block_id.varieties_id.id):
            worksheet.write(next_row, 1, line.plant_block_id.varieties_id.name, wbf['content'])
            worksheet.write(next_row, 2, line.plant_block_id.code, wbf['content'])
            # worksheet.write(next_row, 3, line.accumulated_tbm_cost or 0.0, wbf['content_float'])
            worksheet.write(next_row, 3, line.accumulated_tbm_cost_last_year or 0.0, wbf['content_float'])
            worksheet.write(next_row, 4, line.accumulated_tbm_cost_this_year or 0.0, wbf['content_float'])
            worksheet.write(next_row, 5, line.current_period_cost or 0.0, wbf['content_float'])
            worksheet.write(next_row, 6, line.adjustment_period_cost or 0.0, wbf['content_float'])
            # worksheet.write(next_row, 7, line.accumulated_tbm_cost + line.current_period_cost + line.adjustment_period_cost, wbf['content_float'])
            worksheet.write(next_row, 7, line.accumulated_tbm_cost_last_year + line.accumulated_tbm_cost_this_year + line.current_period_cost + line.adjustment_period_cost, wbf['content_float'])
            next_row += 1
        
        next_row += 1
        worksheet.write(next_row, 1, "", wbf['total'])
        worksheet.write(next_row, 2, "Total", wbf['total'])
        worksheet.write_formula(next_row, 3, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,3)}:{xl_rowcol_to_cell(next_row-2,3)})", wbf['total_float'])
        worksheet.write_formula(next_row, 4, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,4)}:{xl_rowcol_to_cell(next_row-2,4)})", wbf['total_float'])
        worksheet.write_formula(next_row, 5, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,5)}:{xl_rowcol_to_cell(next_row-2,5)})", wbf['total_float'])
        worksheet.write_formula(next_row, 6, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,6)}:{xl_rowcol_to_cell(next_row-2,6)})", wbf['total_float'])
        worksheet.write_formula(next_row, 7, f"=SUBTOTAL(9, {xl_rowcol_to_cell(start_row,7)}:{xl_rowcol_to_cell(next_row-2,7)})", wbf['total_float'])
        
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.repeat_rows(1, 4)
        worksheet.print_area(0, 0, next_row, 13)
        worksheet.set_print_scale(78)