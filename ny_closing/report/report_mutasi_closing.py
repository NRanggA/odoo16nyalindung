from odoo import models

class ReportMutasiClosing(models.AbstractModel):
    _name = 'report.ny_closing.report_mutasi_closing_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Mutasi Closing Excel"

    wbf = {}

    
    def add_workbook_format(self, workbook):
        # Header format untuk judul utama (misalnya, judul laporan)
        self.wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'font_color': '#000000',
        })
        # Format untuk header kolom tabel
        self.wbf['header'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'font_size': 10,
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['header'].set_text_wrap() 
        self.wbf['header'].set_border()
        
        self.wbf['header_same_1'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#A0C878',
            'font_size': 10,
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['header_same_1'].set_text_wrap() 
        self.wbf['header_same_1'].set_border()

        self.wbf['header_same_2'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FBA518',
            'font_size': 10,
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['header_same_2'].set_text_wrap() 
        self.wbf['header_same_2'].set_border()
        
        self.wbf['header_same_3'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#A1E3F9',
            'font_size': 10,
            'font_color': '#000000',
            'border': 1
        })
        self.wbf['header_same_3'].set_text_wrap() 
        self.wbf['header_same_3'].set_border()
        
        # Format untuk footer (biasanya penutup dokumen, misal total atau sum)
        self.wbf['footer'] = workbook.add_format({
            'align': 'left',
            'font_size': 10,
        })
        self.wbf['footer'].set_bottom()

        # Format konten datetime
        self.wbf['content_datetime'] = workbook.add_format({
            'num_format': 'yyyy-mm-dd hh:mm:ss',
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_datetime'].set_border()

        # Format konten date (hanya tanggal)
        self.wbf['content_date'] = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_date'].set_border()

        # Format konten float (angka desimal)
        self.wbf['content_float'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '#,##0.00;-#,##0.00;-'
        })
        self.wbf['content_float'].set_border()
        
        # Format untuk teks konten yang rata kiri
        self.wbf['content'] = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
        })
        self.wbf['content'].set_border()

        # Format untuk konten rata tengah
        self.wbf['content_center'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })
        self.wbf['content_center'].set_border()

        # Format untuk konten persentase
        self.wbf['content_percent'] = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '0.00%'
        })
        self.wbf['content_percent'].set_border()

        # Format total float (untuk jumlah total yang bold dengan background kuning)
        self.wbf['total_float'] = workbook.add_format({
            'bold': True,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'num_format': '#,##0.00',
            'font_color': '#000000'
        })
        self.wbf['total_float'].set_border()

        # Format total number (untuk jumlah total tanpa desimal)
        self.wbf['total_number'] = workbook.add_format({
            'bold': True,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'font_color': '#000000'
        })
        self.wbf['total_number'].set_border()

        # Format total teks (untuk teks di footer atau total yang di tengah)
        self.wbf['total'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFFDB',
            'font_color': '#000000'
        })
        self.wbf['total'].set_border()

        return workbook

    def generate_xlsx_report(self, workbook, datas, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        date_from = obj.date_from.strftime('%d-%m-%Y') if obj.date_from else ''
        date_to = obj.date_to.strftime('%d-%m-%Y') if obj.date_to else ''

        # Nama worksheet
        sheet = workbook.add_worksheet("Laboratory Closing")
        sheet2 = workbook.add_worksheet("Karet Closing")
        sheet3 = workbook.add_worksheet("Pisang Closing")

        ###### CLOSING LABORATORY ######
        # Lebar kolom
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 10)
        sheet.set_column('D:N', 15)

        # Judul Laporan
        sheet.merge_range('E2:J2', 'REPORT LAB CLOSING', wbf['title_doc'])
        sheet.merge_range('E3:J3', f'{date_from} s/d {date_to}', wbf['title_doc'])

        def write_table_headers(start_row, section):
            sheet.merge_range(start_row, 0, start_row + 1, 0, 'Kode', wbf['header'])
            sheet.merge_range(start_row, 1, start_row + 1, 1, 'Nama Product', wbf['header'])
            sheet.merge_range(start_row, 2, start_row + 1, 2, 'Satuan', wbf['header'])
            
            if section == "WIP":
                sheet.merge_range(start_row, 3, start_row, 4, 'Beginning WIP', wbf['header'])
                sheet.merge_range(start_row, 5, start_row, 6, 'New Production', wbf['header'])
                sheet.merge_range(start_row, 7, start_row, 8, 'Onhand WIP', wbf['header'])
                sheet.write(start_row, 9, 'New Cost Price', wbf['header'])
                sheet.merge_range(start_row, 10, start_row, 11, 'Finished (Based on Plan)', wbf['header'])
                sheet.merge_range(start_row, 12, start_row, 13, 'Ending', wbf['header'])
            else:  # Finish Good
                sheet.merge_range(start_row, 3, start_row, 4, 'Beginning', wbf['header'])
                sheet.merge_range(start_row, 5, start_row, 6, 'Produced', wbf['header'])
                sheet.merge_range(start_row, 7, start_row, 8, 'Onhand qty', wbf['header'])
                sheet.write(start_row, 9, 'New Cost Price', wbf['header'])
                sheet.merge_range(start_row, 10, start_row, 11, 'Consumed', wbf['header'])
                sheet.merge_range(start_row, 12, start_row, 13, 'Ending', wbf['header'])
            
            sheet.write(start_row + 1, 3, 'Qty', wbf['header'])
            sheet.write(start_row + 1, 4, 'Value', wbf['header'])
            sheet.write(start_row + 1, 5, 'Qty', wbf['header'])
            sheet.write(start_row + 1, 6, 'Value', wbf['header'])
            sheet.write(start_row + 1, 7, 'Qty', wbf['header'])
            sheet.write(start_row + 1, 8, 'Value', wbf['header'])
            sheet.write(start_row + 1, 9, 'Value', wbf['header'])
            sheet.write(start_row + 1, 10, 'Qty', wbf['header'])
            sheet.write(start_row + 1, 11, 'Value', wbf['header'])
            sheet.write(start_row + 1, 12, 'Qty', wbf['header'])
            sheet.write(start_row + 1, 13, 'Value', wbf['header'])
            return start_row + 2

        # WIP LABORATORY
        row = 5
        sheet.write(row, 0, "WIP", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "WIP")
        for lab_wip in obj.closing_laboratory_ids:
            sheet.write(row, 0, lab_wip.lab_product_id.code, wbf['content'])
            sheet.write(row, 1, lab_wip.lab_product_id.product_id.name, wbf['content'])
            sheet.write(row, 2, lab_wip.lab_product_id.product_id.uom_id.name, wbf['content'])
            sheet.write(row, 3, lab_wip.opening_wip_qty, wbf['content_float'])
            sheet.write(row, 4, lab_wip.opening_wip_value, wbf['content_float'])
            sheet.write(row, 5, lab_wip.incoming_wip_qty, wbf['content_float'])
            sheet.write(row, 6, lab_wip.wip_cost_consumed, wbf['content_float'])
            sheet.write(row, 7, lab_wip.onhand_wip_qty, wbf['content_float'])
            sheet.write(row, 8, lab_wip.onhand_wip_value, wbf['content_float'])
            sheet.write(row, 9, lab_wip.new_wip_cost_price, wbf['content_float'])
            sheet.write(row, 10, lab_wip.outgoing_wip_qty, wbf['content_float'])
            sheet.write(row, 11, lab_wip.outgoing_wip_value, wbf['content_float'])
            sheet.write(row, 12, lab_wip.closing_wip_qty, wbf['content_float'])
            sheet.write(row, 13, lab_wip.closing_wip_value, wbf['content_float'])
            row += 1
        
        # TOTAL WIP LABORATORY
        start_wip_row = row - len(obj.closing_laboratory_ids)

        sheet.write(row, 0, '', wbf['header'])
        sheet.write(row, 1, "TOTAL", wbf['header'])
        sheet.write(row, 2, '', wbf['header'])

        sheet.write_formula(row, 3, f"=SUM(D{start_wip_row}:D{row})", wbf['total_float'])  
        sheet.write_formula(row, 4, f"=SUM(E{start_wip_row}:E{row})", wbf['total_float'])  

        sheet.write_formula(row, 5, f"=SUM(F{start_wip_row}:F{row})", wbf['total_float'])  
        sheet.write_formula(row, 6, f"=SUM(G{start_wip_row}:G{row})", wbf['total_float'])  

        sheet.write_formula(row, 7, f"=SUM(H{start_wip_row}:H{row})", wbf['total_float'])  
        sheet.write_formula(row, 8, f"=SUM(I{start_wip_row}:I{row})", wbf['total_float'])  

        sheet.write_formula(row, 9, f"=SUM(J{start_wip_row}:J{row})", wbf['total_float'])  

        sheet.write_formula(row, 10, f"=SUM(K{start_wip_row}:K{row})", wbf['total_float'])  
        sheet.write_formula(row, 11, f"=SUM(L{start_wip_row}:L{row})", wbf['total_float'])  

        sheet.write_formula(row, 12, f"=SUM(M{start_wip_row}:M{row})", wbf['total_float'])  
        sheet.write_formula(row, 13, f"=SUM(N{start_wip_row}:N{row})", wbf['total_float'])  

        # FINISH GOOD LABORATORY
        row += 2 
        sheet.write(row, 0, "Finished Good", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "Finish Good")
        for lab_fg in obj.closing_laboratory_ids:
            sheet.write(row, 0, lab_fg.lab_product_id.code, wbf['content'])
            sheet.write(row, 1, lab_fg.lab_product_id.product_id.name, wbf['content'])
            sheet.write(row, 2, lab_fg.lab_product_id.product_id.uom_id.name, wbf['content'])
            sheet.write(row, 3, lab_fg.opening_fg_qty, wbf['content_float'])
            sheet.write(row, 4, lab_fg.opening_fg_value, wbf['content_float'])
            sheet.write(row, 5, lab_fg.incoming_fg_qty, wbf['content_float'])
            sheet.write(row, 6, lab_fg.incoming_fg_value, wbf['content_float'])
            sheet.write(row, 7, lab_fg.onhand_fg_qty, wbf['content_float'])
            sheet.write(row, 8, lab_fg.onhand_fg_value, wbf['content_float'])
            sheet.write(row, 9, lab_fg.new_fg_cost_price, wbf['content_float'])
            sheet.write(row, 10, lab_fg.outgoing_fg_qty, wbf['content_float'])
            sheet.write(row, 11, lab_fg.outgoing_fg_value, wbf['content_float'])
            sheet.write(row, 12, lab_fg.closing_fg_qty, wbf['content_float'])
            sheet.write(row, 13, lab_fg.closing_fg_value, wbf['content_float'])
            row += 1

        # TOTAL FINISH GOOD LABORATORY
        start_fg_row = row - len(obj.closing_laboratory_ids)

        sheet.write(row, 0, '', wbf['header'])
        sheet.write(row, 1, "TOTAL", wbf['header'])
        sheet.write(row, 2, '', wbf['header'])

        sheet.write_formula(row, 3, f"=SUM(D{start_fg_row}:D{row})", wbf['total_float'])  
        sheet.write_formula(row, 4, f"=SUM(E{start_fg_row}:E{row})", wbf['total_float'])  

        sheet.write_formula(row, 5, f"=SUM(F{start_fg_row}:F{row})", wbf['total_float'])  
        sheet.write_formula(row, 6, f"=SUM(G{start_fg_row}:G{row})", wbf['total_float'])  

        sheet.write_formula(row, 7, f"=SUM(H{start_fg_row}:H{row})", wbf['total_float'])  
        sheet.write_formula(row, 8, f"=SUM(I{start_fg_row}:I{row})", wbf['total_float'])  

        sheet.write_formula(row, 9, f"=SUM(J{start_fg_row}:J{row})", wbf['total_float'])  

        sheet.write_formula(row, 10, f"=SUM(K{start_fg_row}:K{row})", wbf['total_float'])  
        sheet.write_formula(row, 11, f"=SUM(L{start_fg_row}:L{row})", wbf['total_float'])  

        sheet.write_formula(row, 12, f"=SUM(M{start_fg_row}:M{row})", wbf['total_float'])  
        sheet.write_formula(row, 13, f"=SUM(N{start_fg_row}:N{row})", wbf['total_float'])  
        ###### END CLOSING LABORATORY ######
        

        ############################################
        #           CLOSING KARET                 #
        ############################################
        sheet2.set_column('A:A', 20)
        sheet2.set_column('B:B', 30)
        sheet2.set_column('C:C', 10)
        sheet2.set_column('D:T', 15)
        
        # Judul Laporan
        sheet2.merge_range('E2:J2', 'REPORT KARET CLOSING', wbf['title_doc'])
        sheet2.merge_range('E3:J3', f'{date_from} s/d {date_to}', wbf['title_doc'])
        
        def write_table_headers(start_row, section): 
            col = 0  # Mulai dari kolom pertama

            # Header utama yang selalu ada
            sheet2.merge_range(start_row, col, start_row + 1, col, 'Kode', wbf['header'])
            col += 1
            sheet2.merge_range(start_row, col, start_row + 1, col, 'Nama Product', wbf['header'])
            col += 1
            sheet2.merge_range(start_row, col, start_row + 1, col, 'Satuan', wbf['header'])
            col += 1  # Geser ke kolom berikutnya

            if section == "Stock Lateks & Lump":
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Beginning', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Incoming', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Plantation Cost', wbf['header'])
                sheet2.write(start_row + 1, col, '% Cost', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Onhand', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.write(start_row, col, 'New Cost Price', wbf['header'])
                sheet2.write(start_row + 1, col, 'Value', wbf['header'])
                col += 1

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Production Inprogress', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header_same_1'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header_same_1'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Sales/Delivery', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Adjustment', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Ending', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2
            
            elif section == "Stock Asam Semut":
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Beginning', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Incoming', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Onhand', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.write(start_row, col, 'New Cost Price', wbf['header'])
                sheet2.write(start_row + 1, col, 'Value', wbf['header'])
                col += 1

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Consumed', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header_same_2'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Ending', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2
            
            elif section == "Work In Process Production":
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Beginning', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                sheet2.merge_range(start_row, col, start_row, col + 1, 'New MO', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header_same_1'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header_same_1'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Other Factory Cost', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.write(start_row, col, 'Cost Asam Semut', wbf['header'])
                sheet2.write(start_row + 1, col, 'Value', wbf['header_same_2'])
                col += 1

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Total WIP', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2

                sheet2.write(start_row, col, 'WIP Cost Price', wbf['header'])
                sheet2.write(start_row + 1, col, 'Value', wbf['header'])
                col += 1

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Finished MO', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header_same_3'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header_same_3'])
                col += 2

                sheet2.merge_range(start_row, col, start_row, col + 1, 'Ending WIP', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2
            
            else:  # Finish Good Valuation
                # Beginning
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Beginning', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                # Incoming
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Incoming', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header_same_3'])
                sheet2.write(start_row + 1, col + 1, 'Plantation Cost', wbf['header_same_3'])
                col += 2  

                # Onhand Qty
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Onhand Qty', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                # New Cost Price
                sheet2.write(start_row, col, 'New Cost Price', wbf['header'])
                sheet2.write(start_row + 1, col, 'Value', wbf['header'])
                col += 1  

                # Scrap
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Scrap', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                # Delivery
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Delivery', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                # Adjustment
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Adjustment', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

                # Ending
                sheet2.merge_range(start_row, col, start_row, col + 1, 'Ending', wbf['header'])
                sheet2.write(start_row + 1, col, 'Qty', wbf['header'])
                sheet2.write(start_row + 1, col + 1, 'Value', wbf['header'])
                col += 2  

            return start_row + 2
        
        
        karet_fg_items = obj.closing_production_ids.filtered(lambda r: r.varieties_type == "karet")
        products = ['latex', 'lump']
        
        ######### Stock Lateks & Lump #########
        row = 5
        sheet2.write(row, 0, "Stock Lateks & Lump", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "Stock Lateks & Lump")
        # Looping Data 
        for karet_1 in karet_fg_items:
            for product in products:
                col = 0

                sheet2.write(row, col, '-', wbf['content'])
                col += 1
                sheet2.write(row, col, eval(f"karet_1.{product}_product_id.name"), wbf['content'])
                col += 1
                sheet2.write(row, col, eval(f"karet_1.{product}_product_id.uom_id.name"), wbf['content'])
                col += 1

                # Beginning
                sheet2.write(row, col, getattr(karet_1, f"{product}_opening_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_1, f"{product}_opening_value", '-'), wbf['content_float'])
                col += 1
                # Incoming
                sheet2.write(row, col, getattr(karet_1, f"{product}_incoming_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, 0, wbf['content_float'])
                col += 1
                # Plantataion Cost
                sheet2.write(row, col, getattr(karet_1, f"pct_cost_for_{product}", '-'), wbf['content_float'])
                col += 1
                # sheet2.write(row, col, getattr(karet_1, f"{product}_plantation_cost", '-'), wbf['content_float'])
                sheet2.write(row, col, getattr(karet_1, f"{product}_plantation_cost", '-'), wbf['content_float'])
                col += 1
                # Onhand
                sheet2.write(row, col, getattr(karet_1, f"{product}_onhand_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_1, f"{product}_onhand_value", '-'), wbf['content_float'])
                col += 1
                # New Cost Price
                sheet2.write(row, col, getattr(karet_1, f"{product}_new_cost_price", '-'), wbf['content_float'])
                col += 1
                # Production Inprogress
                sheet2.write(row, col, getattr(karet_1, f"{product}_wip_incoming_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_1, f"{product}_wip_incoming_value", '-'), wbf['content_float'])
                col += 1
                # Sales/Delivery
                sheet2.write(row, col, getattr(karet_1, f"{product}_delivered_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_1, f"{product}_delivered_value", '-'), wbf['content_float'])
                col += 1
                # Adjustment
                sheet2.write(row, col, getattr(karet_1, f"{product}_adjustment_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_1, f"{product}_adjustment_value", '-'), wbf['content_float'])
                col += 1
                # Ending
                sheet2.write(row, col, getattr(karet_1, f"{product}_closing_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_1, f"{product}_closing_value", '-'), wbf['content_float'])
                col += 1


                row += 1

        start_row = row - len(karet_fg_items)
        sheet2.write(row, 0, '', wbf['header'])
        sheet2.write(row, 1, "TOTAL", wbf['header'])
        sheet2.write(row, 2, '', wbf['header'])
        sheet2.write_formula(row, 3, f"=SUM(D{start_row}:D{row})", wbf['total_float'])  
        sheet2.write_formula(row, 4, f"=SUM(E{start_row}:E{row})", wbf['total_float'])  

        sheet2.write_formula(row, 5, f"=SUM(F{start_row}:F{row})", wbf['total_float'])  
        sheet2.write_formula(row, 6, f"=SUM(G{start_row}:G{row})", wbf['total_float'])  

        sheet2.write_formula(row, 7, f"=SUM(H{start_row}:H{row})", wbf['total_float']) 
        sheet2.write_formula(row, 8, f"=SUM(I{start_row}:I{row})", wbf['total_float']) 

        sheet2.write_formula(row, 9, f"=SUM(J{start_row}:J{row})", wbf['total_float'])  

        sheet2.write_formula(row, 10, f"=SUM(K{start_row}:K{row})", wbf['total_float']) 
        sheet2.write_formula(row, 11, f"=SUM(L{start_row}:L{row})", wbf['total_float']) 
        
        sheet2.write_formula(row, 12, f"=SUM(M{start_row}:M{row})", wbf['total_float']) 
        sheet2.write_formula(row, 13, f"=SUM(N{start_row}:N{row})", wbf['total_float']) 

        sheet2.write_formula(row, 14, f"=SUM(O{start_row}:O{row})", wbf['total_float']) 
        sheet2.write_formula(row, 15, f"=SUM(P{start_row}:P{row})", wbf['total_float']) 

        sheet2.write_formula(row, 16, f"=SUM(Q{start_row}:Q{row})", wbf['total_float']) 
        sheet2.write_formula(row, 17, f"=SUM(R{start_row}:R{row})", wbf['total_float']) 
        
        sheet2.write_formula(row, 18, f"=SUM(Q{start_row}:Q{row})", wbf['total_float']) 
        sheet2.write_formula(row, 19, f"=SUM(R{start_row}:R{row})", wbf['total_float']) 

        ########### Stock Asam Semut ###########
        row += 3
        sheet2.write(row, 0, "Stock Asam Semut", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "Stock Asam Semut")
        
        col = 0
        # Looping data
        sheet2.write(row, col, '-', wbf['content'])
        col += 1
        sheet2.write(row, col, 'Asam Semut', wbf['content'])
        col += 1
        sheet2.write(row, col, 'CC', wbf['content'])
        col += 1
        
        asam_semut_fields = ['sheet_rm_opening_qty', 'sheet_rm_opening_value', 'sheet_rm_incoming_qty', 'sheet_rm_incoming_value', 'sheet_rm_onhand_qty', 'sheet_rm_onhand_value', 'sheet_rm_cost_price', 'sheet_rm_outgoing_qty', 'sheet_rm_outgoing_value', 'sheet_rm_closing_qty', 'sheet_rm_closing_value']
        total_values = [0] * len(asam_semut_fields)
        for asam_semut in asam_semut_fields:
            value = getattr(karet_fg_items, asam_semut, '-')
            sheet2.write(row, col, value, wbf['content_float'])
            total_values[col - 3] += value
            col += 1
        row += 1
        # Total
        sheet2.write(row, 0, '', wbf['header'])
        sheet2.write(row, 1, "TOTAL", wbf['header'])
        sheet2.write(row, 2, '', wbf['header'])
        col = 3  
        for total in total_values:
            sheet2.write(row, col, total, wbf['total_float'])
            col += 1


        ########## Work In Process Production ##########
        row += 3
        sheet2.write(row, 0, "Work In Process Production", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "Work In Process Production")
        #LOOPING MASING MASING DATA
        for karet_2 in karet_fg_items:
            for product_2 in products:
                col = 0
                sheet2.write(row, col, '-', wbf['content'])
                col += 1
                sheet2.write(row, col, eval(f"karet_2.{product_2}_product_id.name"), wbf['content'])
                col += 1
                sheet2.write(row, col, eval(f"karet_2.{product_2}_product_id.uom_id.name"), wbf['content'])
                col += 1

                # Beginning
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_opening_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_opening_value", '-'), wbf['content_float'])
                col += 1
                
                # New MO
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_incoming_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_incoming_value", '-'), wbf['content_float'])
                col += 1
                
                # Other Factory Cost
                if product_2 == 'latex':
                    sheet2.write(row, col, karet_2.pct_cost_for_sheet, wbf['content_float'])
                    col += 1
                    sheet2.write(row, col,  karet_2.sheet_manufacturing_cost, wbf['content_float'])
                    col += 1
                else:
                    sheet2.write(row, col, karet_2.pct_cost_for_compound, wbf['content_float'])
                    col += 1
                    sheet2.write(row, col,  karet_2.compound_manufacturing_cost, wbf['content_float'])
                    col += 1
                
                # Cost Asam Semut
                if product_2 == 'latex':
                    sheet2.write(row, col, karet_2.sheet_rm_outgoing_value or 0, wbf['content_float']) 
                    col += 1
                else:
                    sheet2.write(row, col, 0, wbf['content_float']) 
                    col += 1
                
                # Total WIP
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_onhand_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_onhand_value", '-'), wbf['content_float'])
                col += 1
                
                # WIP Cost Price
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_cost_price", '-'), wbf['content_float'])
                col += 1
                
                # Finished MO
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_outgoing_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_outgoing_value", '-'), wbf['content_float'])
                col += 1
                
                # Ending WIP
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_qty", '-'), wbf['content_float'])
                col += 1
                sheet2.write(row, col, getattr(karet_2, f"{product_2}_wip_value", '-'), wbf['content_float'])
                col += 1

                row += 1

        start_row = row - len(karet_fg_items)
        sheet2.write(row, 0, '', wbf['header'])
        sheet2.write(row, 1, "TOTAL", wbf['header'])
        sheet2.write(row, 2, '', wbf['header'])
        sheet2.write_formula(row, 3, f"=SUM(D{start_row}:D{row})", wbf['total_float'])  
        sheet2.write_formula(row, 4, f"=SUM(E{start_row}:E{row})", wbf['total_float'])  
        sheet2.write_formula(row, 5, f"=SUM(F{start_row}:F{row})", wbf['total_float'])  
        sheet2.write_formula(row, 6, f"=SUM(G{start_row}:G{row})", wbf['total_float'])  
        sheet2.write_formula(row, 7, f"=SUM(H{start_row}:H{row})", wbf['total_float']) 
        sheet2.write_formula(row, 8, f"=SUM(I{start_row}:I{row})", wbf['total_float']) 
        sheet2.write_formula(row, 9, f"=SUM(J{start_row}:J{row})", wbf['total_float'])  
        sheet2.write_formula(row, 10, f"=SUM(K{start_row}:K{row})", wbf['total_float']) 
        sheet2.write_formula(row, 11, f"=SUM(L{start_row}:L{row})", wbf['total_float']) 
        sheet2.write_formula(row, 12, f"=SUM(M{start_row}:M{row})", wbf['total_float']) 
        sheet2.write_formula(row, 13, f"=SUM(N{start_row}:N{row})", wbf['total_float']) 
        sheet2.write_formula(row, 14, f"=SUM(O{start_row}:O{row})", wbf['total_float']) 
        sheet2.write_formula(row, 15, f"=SUM(P{start_row}:P{row})", wbf['total_float']) 
        sheet2.write_formula(row, 16, f"=SUM(Q{start_row}:Q{row})", wbf['total_float']) 

        ######## Finish Good Valuation ########
        row += 3
        sheet2.write(row, 0, "Finish Good Valuation", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "Finish Good Valuation")

        for karet in karet_fg_items.fg2_valuation_ids:
            sheet2.write(row, 0, karet.product_id.default_code if karet.product_id.default_code else '-', wbf['content'])
            sheet2.write(row, 1, karet.product_id.name, wbf['content'])
            sheet2.write(row, 2, karet.product_id.uom_id.name, wbf['content'])
            
            sheet2.write(row, 3, karet.opening_qty, wbf['content_float'])
            sheet2.write(row, 4, karet.opening_value, wbf['content_float'])
            
            sheet2.write(row, 5, karet.incoming_qty, wbf['content_float'])
            sheet2.write(row, 6, karet.manufacturing_cost, wbf['content_float'])
            
            sheet2.write(row, 7, karet.onhand_qty, wbf['content_float'])
            sheet2.write(row, 8, karet.onhand_value, wbf['content_float'])
            
            sheet2.write(row, 9, karet.new_cost_price, wbf['content_float'])
            
            sheet2.write(row, 10, karet.scrap_qty, wbf['content_float'])
            sheet2.write(row, 11, karet.scrap_value, wbf['content_float'])

            sheet2.write(row, 12, karet.outgoing_qty, wbf['content_float'])
            sheet2.write(row, 13, karet.outgoing_value, wbf['content_float'])

            sheet2.write(row, 14, karet.adjustment_qty, wbf['content_float'])
            sheet2.write(row, 15, karet.adjustment_value, wbf['content_float'])

            sheet2.write(row, 16, karet.closing_qty, wbf['content_float'])
            sheet2.write(row, 17, karet.closing_value, wbf['content_float'])
            
            row += 1
        
        # Total Data finish good valuation
        start_row = row - len(karet_fg_items.fg2_valuation_ids)
        sheet2.write(row, 0, '', wbf['header'])
        sheet2.write(row, 1, "TOTAL", wbf['header'])
        sheet2.write(row, 2, '', wbf['header'])
        
        sheet2.write_formula(row, 3, f"=SUM(D{start_row}:D{row})", wbf['total_float'])  
        sheet2.write_formula(row, 4, f"=SUM(E{start_row}:E{row})", wbf['total_float'])  

        sheet2.write_formula(row, 5, f"=SUM(F{start_row}:F{row})", wbf['total_float'])  
        sheet2.write_formula(row, 6, f"=SUM(G{start_row}:G{row})", wbf['total_float'])  

        sheet2.write_formula(row, 7, f"=SUM(H{start_row}:H{row})", wbf['total_float']) 
        sheet2.write_formula(row, 8, f"=SUM(I{start_row}:I{row})", wbf['total_float']) 

        sheet2.write_formula(row, 9, f"=SUM(J{start_row}:J{row})", wbf['total_float'])  

        sheet2.write_formula(row, 10, f"=SUM(K{start_row}:K{row})", wbf['total_float']) 
        sheet2.write_formula(row, 11, f"=SUM(L{start_row}:L{row})", wbf['total_float']) 
        
        sheet2.write_formula(row, 12, f"=SUM(M{start_row}:M{row})", wbf['total_float']) 
        sheet2.write_formula(row, 13, f"=SUM(N{start_row}:N{row})", wbf['total_float']) 

        sheet2.write_formula(row, 14, f"=SUM(O{start_row}:O{row})", wbf['total_float']) 
        sheet2.write_formula(row, 15, f"=SUM(P{start_row}:P{row})", wbf['total_float']) 

        sheet2.write_formula(row, 16, f"=SUM(Q{start_row}:Q{row})", wbf['total_float']) 
        sheet2.write_formula(row, 17, f"=SUM(R{start_row}:R{row})", wbf['total_float']) 

        ###### CLOSING KARET ######



        ############################################
        #           CLOSING PISANG                 #
        ############################################
        sheet3.set_column('A:A', 20)
        sheet3.set_column('B:B', 30)
        sheet3.set_column('C:C', 10)
        sheet3.set_column('D:V', 15)

        # Judul Laporan
        sheet3.merge_range('E2:J2', 'REPORT PISANG CLOSING', wbf['title_doc'])
        sheet3.merge_range('E3:J3', f'{date_from} s/d {date_to}', wbf['title_doc'])
        
        def write_table_headers(start_row, section):
            sheet3.merge_range(start_row, 0, start_row + 1, 0, 'Kode', wbf['header'])
            sheet3.merge_range(start_row, 1, start_row + 1, 1, 'Nama Product', wbf['header'])
            sheet3.merge_range(start_row, 2, start_row + 1, 2, 'Satuan', wbf['header'])
            
            if section == "Stock Location":
                sheet3.merge_range(start_row, 3, start_row, 4, 'Beginning', wbf['header'])
                sheet3.merge_range(start_row, 5, start_row, 6, 'Incoming', wbf['header'])
                sheet3.merge_range(start_row, 7, start_row, 8, 'Onhand Qty', wbf['header'])
                sheet3.write(start_row, 9, 'New Cost Price', wbf['header'])
                sheet3.merge_range(start_row, 10, start_row, 11, 'Repening', wbf['header'])
                sheet3.merge_range(start_row, 12, start_row, 13, 'Scrap', wbf['header'])
                sheet3.merge_range(start_row, 14, start_row, 15, 'Devlivery', wbf['header'])
                sheet3.merge_range(start_row, 16, start_row, 17, 'Adjustment', wbf['header'])
                sheet3.merge_range(start_row, 18, start_row, 19, 'Ending', wbf['header'])
                
                # Body value
                # Beginning
                sheet3.write(start_row + 1, 3, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 4, 'Value', wbf['header'])
                # Incoming
                sheet3.write(start_row + 1, 5, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 6, 'Production Cost', wbf['header'])

                # Onhand Qty
                sheet3.write(start_row + 1, 7, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 8, 'Value', wbf['header'])
                # New Cost Price
                sheet3.write(start_row + 1, 9, 'Value', wbf['header'])
                # Repening
                sheet3.write(start_row + 1, 10, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 11, 'Value', wbf['header'])
                # Scrap
                sheet3.write(start_row + 1, 12, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 13, 'Value', wbf['header'])
                # Delivery
                sheet3.write(start_row + 1, 14, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 15, 'Value', wbf['header'])
                # Adjustment
                sheet3.write(start_row + 1, 16, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 17, 'Value', wbf['header'])
                # Ending
                sheet3.write(start_row + 1, 18, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 19, 'Value', wbf['header'])

            else:  # Repening Location
                sheet3.merge_range(start_row, 3, start_row, 4, 'Beginning', wbf['header'])
                sheet3.merge_range(start_row, 5, start_row, 7, 'Incoming', wbf['header'])
                sheet3.merge_range(start_row, 8, start_row, 9, 'Onhand qty', wbf['header'])
                sheet3.write(start_row, 10, 'New Cost Price', wbf['header'])
                sheet3.merge_range(start_row, 11, start_row, 12, 'Delivery', wbf['header'])
                sheet3.merge_range(start_row, 13, start_row, 14, 'Ending', wbf['header'])
                
                # Body value
                sheet3.write(start_row + 1, 3, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 4, 'Value', wbf['header'])

                sheet3.write(start_row + 1, 5, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 6, 'Value', wbf['header'])
                sheet3.write(start_row + 1, 7, 'Repening Cost', wbf['header'])
                
                sheet3.write(start_row + 1, 8, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 9, 'Value', wbf['header'])
                
                sheet3.write(start_row + 1, 10, 'Value', wbf['header'])
                
                sheet3.write(start_row + 1, 11, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 12, 'Value', wbf['header'])
                
                sheet3.write(start_row + 1, 13, 'Qty', wbf['header'])
                sheet3.write(start_row + 1, 14, 'Value', wbf['header'])
            
            return start_row + 2
        
        # Ambil data untuk yang pisang saja
        pisang_fg2_items = obj.closing_production_ids.filtered(lambda r: r.varieties_type == "pisang").fg2_valuation_ids

        # Stock Location
        row = 5
        sheet3.write(row, 0, "Stock Location", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "Stock Location")

        for pisang in pisang_fg2_items:
            sheet3.write(row, 0, pisang.product_id.default_code if pisang.product_id.default_code else '-', wbf['content'])
            sheet3.write(row, 1, pisang.product_id.name, wbf['content'])
            sheet3.write(row, 2, pisang.product_id.uom_id.name, wbf['content'])
            
            sheet3.write(row, 3, pisang.opening_qty, wbf['content_float'])
            sheet3.write(row, 4, pisang.opening_value, wbf['content_float'])
            
            sheet3.write(row, 5, pisang.incoming_qty, wbf['content_float'])
            sheet3.write(row, 6, pisang.plantation_cost, wbf['content_float'])
            
            sheet3.write(row, 7, pisang.onhand_qty, wbf['content_float'])
            sheet3.write(row, 8, pisang.onhand_value, wbf['content_float'])
            
            sheet3.write(row, 9, pisang.new_cost_price, wbf['content_float'])
            
            sheet3.write(row, 10, pisang.ripening_qty, wbf['content_float'])
            sheet3.write(row, 11, pisang.ripening_value, wbf['content_float'])

            sheet3.write(row, 12, pisang.scrap_qty, wbf['content_float'])
            sheet3.write(row, 13, pisang.scrap_value, wbf['content_float'])

            sheet3.write(row, 14, pisang.outgoing_qty, wbf['content_float'])
            sheet3.write(row, 15, pisang.outgoing_value, wbf['content_float'])

            sheet3.write(row, 16, pisang.adjustment_qty, wbf['content_float'])
            sheet3.write(row, 17, pisang.adjustment_value, wbf['content_float'])

            sheet3.write(row, 18, pisang.closing_qty, wbf['content_float'])
            sheet3.write(row, 19, pisang.closing_value, wbf['content_float'])
            
            row += 1
        
        # TOTAL STOCK LOCATION
        start_row = row - len(pisang_fg2_items)
        sheet3.write(row, 0, '', wbf['header'])
        sheet3.write(row, 1, "TOTAL", wbf['header'])
        sheet3.write(row, 2, '', wbf['header'])
        sheet3.write_formula(row, 3, f"=SUM(D{start_row}:D{row})", wbf['total_float'])  
        sheet3.write_formula(row, 4, f"=SUM(E{start_row}:E{row})", wbf['total_float'])  

        sheet3.write_formula(row, 5, f"=SUM(F{start_row}:F{row})", wbf['total_float'])  
        sheet3.write_formula(row, 6, f"=SUM(G{start_row}:G{row})", wbf['total_float'])  

        sheet3.write_formula(row, 7, f"=SUM(H{start_row}:H{row})", wbf['total_float']) 
        sheet3.write_formula(row, 8, f"=SUM(I{start_row}:I{row})", wbf['total_float']) 

        sheet3.write_formula(row, 9, f"=SUM(J{start_row}:J{row})", wbf['total_float'])  

        sheet3.write_formula(row, 10, f"=SUM(K{start_row}:K{row})", wbf['total_float']) 
        sheet3.write_formula(row, 11, f"=SUM(L{start_row}:L{row})", wbf['total_float']) 
        
        sheet3.write_formula(row, 12, f"=SUM(M{start_row}:M{row})", wbf['total_float']) 
        sheet3.write_formula(row, 13, f"=SUM(N{start_row}:N{row})", wbf['total_float']) 

        sheet3.write_formula(row, 14, f"=SUM(O{start_row}:O{row})", wbf['total_float']) 
        sheet3.write_formula(row, 15, f"=SUM(P{start_row}:P{row})", wbf['total_float']) 

        sheet3.write_formula(row, 16, f"=SUM(Q{start_row}:Q{row})", wbf['total_float']) 
        sheet3.write_formula(row, 17, f"=SUM(R{start_row}:R{row})", wbf['total_float']) 

        sheet3.write_formula(row, 18, f"=SUM(S{start_row}:S{row})", wbf['total_float']) 
        sheet3.write_formula(row, 19, f"=SUM(T{start_row}:T{row})", wbf['total_float']) 


        # Repening Location
        row += 2 
        sheet3.write(row, 0, "Repening Location", wbf['title_doc'])
        row += 1
        row = write_table_headers(row, "Repening Location")
        
        for pisang in pisang_fg2_items:
            sheet3.write(row, 0, pisang.product_id.default_code if pisang.product_id.default_code else '-', wbf['content'])
            sheet3.write(row, 1, pisang.product_id.name, wbf['content'])
            sheet3.write(row, 2, pisang.product_id.uom_id.name, wbf['content'])
            
            sheet3.write(row, 3, pisang.ripening_opening_qty, wbf['content_float'])
            sheet3.write(row, 4, pisang.ripening_opening_value, wbf['content_float'])
            
            sheet3.write(row, 5, pisang.ripening_incoming_qty, wbf['content_float'])
            sheet3.write(row, 6, pisang.ripening_incoming_value, wbf['content_float'])
            sheet3.write(row, 7, pisang.ripening_cost, wbf['content_float'])
            
            sheet3.write(row, 8, pisang.ripening_onhand_qty, wbf['content_float'])
            sheet3.write(row, 9, pisang.ripening_onhand_value, wbf['content_float'])
            
            sheet3.write(row, 10, pisang.new_cost_price_ripening, wbf['content_float'])
            
            sheet3.write(row, 11, pisang.ripening_outgoing_qty, wbf['content_float'])
            sheet3.write(row, 12, pisang.ripening_outgoing_value, wbf['content_float'])
            
            sheet3.write(row, 13, pisang.ripening_closing_qty, wbf['content_float'])
            sheet3.write(row, 14, pisang.ripening_closing_value, wbf['content_float'])

            row += 1
        
        # TOTAL REPENING LOCATION
        start_repening_row = row - len(pisang_fg2_items)  
        sheet3.write(row, 0, "", wbf['header'])
        sheet3.write(row, 1, "TOTAL", wbf['header'])
        sheet3.write(row, 2, '', wbf['header'])
        sheet3.write_formula(row, 3, f"=SUM(D{start_repening_row}:D{row})", wbf['total_float'])
        sheet3.write_formula(row, 4, f"=SUM(E{start_repening_row}:E{row})", wbf['total_float'])
        sheet3.write_formula(row, 5, f"=SUM(F{start_repening_row}:F{row})", wbf['total_float'])
        sheet3.write_formula(row, 6, f"=SUM(G{start_repening_row}:G{row})", wbf['total_float'])
        sheet3.write_formula(row, 7, f"=SUM(H{start_repening_row}:H{row})", wbf['total_float'])
        sheet3.write_formula(row, 8, f"=SUM(I{start_repening_row}:I{row})", wbf['total_float'])
        sheet3.write_formula(row, 9, f"=SUM(J{start_repening_row}:J{row})", wbf['total_float'])
        sheet3.write_formula(row, 10, f"=SUM(K{start_repening_row}:K{row})", wbf['total_float'])
        sheet3.write_formula(row, 11, f"=SUM(L{start_repening_row}:L{row})", wbf['total_float'])
        sheet3.write_formula(row, 12, f"=SUM(M{start_repening_row}:M{row})", wbf['total_float'])
        sheet3.write_formula(row, 13, f"=SUM(N{start_repening_row}:N{row})", wbf['total_float'])
        sheet3.write_formula(row, 14, f"=SUM(O{start_repening_row}:O{row})", wbf['total_float'])

        ############## CLOSING PISANG ##############



        # Page Layout Sheet 
        sheet.set_landscape()
        sheet.set_paper(9)  # A4
        sheet.repeat_rows(1, 4)
        sheet.print_area(0, 0, row, 13)
        sheet.set_print_scale(78)
        
        # Page Layout Sheeet2
        sheet.set_landscape()
        sheet.set_paper(9)  # A4
        sheet.repeat_rows(1, 4)
        sheet.print_area(0, 0, row, 13)
        sheet.set_print_scale(78)

        # Page Layout Sheeet3
        sheet.set_landscape()
        sheet.set_paper(9)  # A4
        sheet.repeat_rows(1, 4)
        sheet.print_area(0, 0, row, 13)
        sheet.set_print_scale(78)

