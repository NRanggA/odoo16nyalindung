from odoo import api, models, fields, _
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name


class ReportProductionOrderXlsx(models.AbstractModel):
    _name = 'report.ny_mrp.report_production_order_xlsx'
    _description = "Rekap Production Order"
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

        self.wbf['content_percent'] = workbook.add_format({
            **align_right,
            **pct_format,
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
        
        self.wbf['total_percent'] = workbook.add_format({
            **bold,
            **bg_color_grandtotal,
            **align_right,
            **font_color_grandtotal,
            **pct_format,
            **border_all
        })
        return workbook
 
    def generate_xlsx_report(self, workbook, data, obj):
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf

        # Determine which MOs to fetch based on report type
        mrp_datas = self.env['mrp.production']
        
        if obj.report_type == 'raw_material':
            # Laporan Olah Bahan Baku - based on raw material processing date
            # Get MOs that used raw materials (Lateks/Lump) in the period
            domain = [
                ('state', '=', 'done'),
                ('date_finished', '>=', obj.date_from),
                ('date_finished', '<=', obj.date_to),
                ('product_id.name', 'in', ['Sheet', 'WIP Compo'])
            ]
            mrp_datas = self.env['mrp.production'].search(domain, order='date_finished asc')
        else:
            # Laporan Barang Jadi - based on finished product date
            # Get MOs where the finish_mo_ids were completed in the period
            finish_mos = self.env['mrp.production'].search([
                ('state', '=', 'done'),
                ('date_finished', '>=', obj.date_from),
                ('date_finished', '<=', obj.date_to),
                ('product_id.name', 'in', ['RSS I', 'RSS III', 'Cutting', 'Compo'])
            ])
            # Get the source MOs
            mrp_datas = finish_mos.mapped('source_mo_id').filtered(lambda x: x)

        # WORKSHEET 1: Olahan Lateks (Lateks/Lump → Sheet → RSS I/II/III/Cutting)
        worksheet = workbook.add_worksheet("Olahan Lateks")
        
        next_row = 1
        col = 1
        worksheet.write(next_row, col, 'Tgl Olah', wbf['header'])
        worksheet.set_column(col, col, 12)
        col += 1
        worksheet.write(next_row, col, 'Nomor MO', wbf['header'])
        worksheet.set_column(col, col, 25)
        col += 1
        worksheet.write(next_row, col, "Lateks", wbf['header'])
        worksheet.set_column(col, col, 10)
        col += 1
        worksheet.write(next_row, col, "Asam Semut", wbf['header'])
        worksheet.set_column(col, col, 10)
        col += 1
        worksheet.write(next_row, col, "Status", wbf['header'])
        worksheet.set_column(col, col, 12)
        col += 1
        worksheet.write(next_row, col, "Tgl Selesai", wbf['header'])
        worksheet.set_column(col, col, 12)
        col += 1
        worksheet.write(next_row, col, "RSS I", wbf['header'])
        worksheet.set_column(col, col, 10)
        col += 1
        worksheet.write(next_row, col, "RSS III", wbf['header'])
        worksheet.set_column(col, col, 10)
        col += 1
        worksheet.write(next_row, col, "Cutting", wbf['header'])
        worksheet.set_column(col, col, 10)
        col += 1
        worksheet.write(next_row, col, "DRC (%)", wbf['header'])
        worksheet.set_column(col, col, 10)
        col += 1
        worksheet.write(next_row, col, "Durasi (Hari)", wbf['header'])
        worksheet.set_column(col, col, 12)
        next_row += 1
        
        for c in range(1, col + 1):
            worksheet.write(next_row, c, c, wbf['header_filter'])
        next_row += 1
        first_row = next_row
        worksheet.freeze_panes(next_row, 3)

        # Filter for Lateks-based MOs only
        lateks_mos = mrp_datas.filtered(lambda x: x.product_id.name == 'Sheet')
        
        for mo in lateks_mos:
            col = 1
            # Tanggal Olah
            worksheet.write(next_row, col, mo.date_finished.date() if mo.date_finished else '', wbf['content_date'])
            col += 1
            # Nomor MO
            worksheet.write(next_row, col, mo.name or '', wbf['content'])
            col += 1
            # Lateks qty
            lateks_line = mo.move_raw_ids.filtered(lambda x: x.product_id.name == 'Lateks')
            lateks_qty = sum(lateks_line.mapped('quantity_done')) if lateks_line else 0
            worksheet.write(next_row, col, lateks_qty, wbf['content_float'])
            col += 1
            # Asam Semut qty
            asam_line = mo.move_raw_ids.filtered(lambda x: x.product_id.name == 'Asam Semut')
            asam_qty = sum(asam_line.mapped('quantity_done')) if asam_line else 0
            worksheet.write(next_row, col, asam_qty, wbf['content_float'])
            col += 1
            # Status
            mo_final = mo.finish_mo_ids.filtered(lambda x: x.state == 'done')
            if mo_final:
                status = 'Selesai'
            elif mo.finish_mo_ids:
                status = 'Dalam Proses'
            else:
                status = 'Belum Diproses'
            worksheet.write(next_row, col, status, wbf['content_center'])
            col += 1
            # Tanggal Selesai
            if mo_final:
                finish_date = max(mo_final.mapped('date_finished')).date() if mo_final else ''
                worksheet.write(next_row, col, finish_date, wbf['content_date'])
            else:
                worksheet.write(next_row, col, '', wbf['content'])
            col += 1
            # RSS I qty
            rss1_mo = mo_final.filtered(lambda x: x.product_id.name == 'RSS I')
            rss1_qty = sum(rss1_mo.mapped('product_qty')) if rss1_mo else 0
            worksheet.write(next_row, col, rss1_qty, wbf['content_float'])
            col += 1
            # RSS III qty
            rss3_mo = mo_final.filtered(lambda x: x.product_id.name == 'RSS III')
            rss3_qty = sum(rss3_mo.mapped('product_qty')) if rss3_mo else 0
            worksheet.write(next_row, col, rss3_qty, wbf['content_float'])
            col += 1
            # Cutting qty
            cutting_mo = mo_final.filtered(lambda x: x.product_id.name == 'Cutting')
            cutting_qty = sum(cutting_mo.mapped('product_qty')) if cutting_mo else 0
            worksheet.write(next_row, col, cutting_qty, wbf['content_float'])
            col += 1
            # DRC (%) - Using formula
            worksheet.write_formula(next_row, col, 
                f"=({xl_rowcol_to_cell(next_row, 7)}+{xl_rowcol_to_cell(next_row, 8)}+{xl_rowcol_to_cell(next_row, 9)})/{xl_rowcol_to_cell(next_row, 3)}", 
                wbf['content_percent'])
            col += 1
            # Durasi (Hari) - only if finished
            if mo_final and mo.date_finished:
                finish_date = max(mo_final.mapped('date_finished'))
                duration = (finish_date.date() - mo.date_finished.date()).days
                worksheet.write(next_row, col, duration, wbf['content_float'])
            else:
                worksheet.write(next_row, col, '', wbf['content'])
            next_row += 1
        
        # Write grandtotal for Lateks sheet
        if first_row < next_row:
            col = 1
            worksheet.write(next_row, col, "TOTAL", wbf['total'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            # Sum Lateks
            worksheet.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            # Sum Asam Semut
            worksheet.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet.write(next_row, col, "", wbf['total'])
            col += 1
            # Sum RSS I
            worksheet.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            # Sum RSS III
            worksheet.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            # Sum Cutting
            worksheet.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            # Average DRC (%)
            worksheet.write_formula(next_row, col, 
                f"=({xl_rowcol_to_cell(next_row, 7)}+{xl_rowcol_to_cell(next_row, 8)}+{xl_rowcol_to_cell(next_row, 9)})/{xl_rowcol_to_cell(next_row, 3)}", 
                wbf['total_percent'])
            col += 1
            # Average Durasi
            worksheet.write_formula(next_row, col, 
                f"=AVERAGE({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            next_row += 1

        worksheet.set_landscape()
        worksheet.set_paper(9)
        worksheet.repeat_rows(1, 2) 
        worksheet.print_area(0, 0, next_row, col)
        worksheet.set_print_scale(80)

        ########################################################### 
        # WORKSHEET 2: Olahan Lump (Lump → Compo)
        worksheet2 = workbook.add_worksheet("Olahan Lump")
        
        next_row = 1
        col = 1
        worksheet2.write(next_row, col, 'Tgl Olah', wbf['header'])
        worksheet2.set_column(col, col, 12)
        col += 1
        worksheet2.write(next_row, col, 'Nomor MO', wbf['header'])
        worksheet2.set_column(col, col, 25)
        col += 1
        worksheet2.write(next_row, col, "Lump", wbf['header'])
        worksheet2.set_column(col, col, 10)
        col += 1
        worksheet2.write(next_row, col, "Asam Semut", wbf['header'])
        worksheet2.set_column(col, col, 10)
        col += 1
        worksheet2.write(next_row, col, "Status", wbf['header'])
        worksheet2.set_column(col, col, 12)
        col += 1
        worksheet2.write(next_row, col, "Tgl Selesai", wbf['header'])
        worksheet2.set_column(col, col, 12)
        col += 1
        worksheet2.write(next_row, col, "Compo", wbf['header'])
        worksheet2.set_column(col, col, 10)
        col += 1
        worksheet2.write(next_row, col, "DRC (%)", wbf['header'])
        worksheet2.set_column(col, col, 10)
        col += 1
        worksheet2.write(next_row, col, "Durasi (Hari)", wbf['header'])
        worksheet2.set_column(col, col, 12)
        next_row += 1
        
        for c in range(1, col + 1):
            worksheet2.write(next_row, c, c, wbf['header_filter'])
        next_row += 1
        first_row = next_row
        worksheet2.freeze_panes(next_row, 3)

        # Filter for Lump-based MOs (Compo product)
        lump_mos = mrp_datas.filtered(lambda x: x.product_id.name == 'WIP Compo')
        
        for mo in lump_mos:
            col = 1
            # Tanggal Olah
            worksheet2.write(next_row, col, mo.date_finished.date() if mo.date_finished else '', wbf['content_date'])
            col += 1
            # Nomor MO
            worksheet2.write(next_row, col, mo.name or '', wbf['content'])
            col += 1
            # Lump qty
            lump_line = mo.move_raw_ids.filtered(lambda x: x.product_id.name == 'Lump')
            lump_qty = sum(lump_line.mapped('quantity_done')) if lump_line else 0
            worksheet2.write(next_row, col, lump_qty, wbf['content_float'])
            col += 1
            # Asam Semut qty
            asam_line = mo.move_raw_ids.filtered(lambda x: x.product_id.name == 'Asam Semut')
            asam_qty = sum(asam_line.mapped('quantity_done')) if asam_line else 0
            worksheet2.write(next_row, col, asam_qty, wbf['content_float'])
            col += 1
            # Status
            status = 'Selesai' if mo.state == 'done' else mo.state.title()
            worksheet2.write(next_row, col, status, wbf['content_center'])
            col += 1
            # Tanggal Selesai
            finish_date = mo.date_finished.date() if mo.date_finished else ''
            worksheet2.write(next_row, col, finish_date, wbf['content_date'])
            col += 1
            # Compo qty (the finished product)
            compo_qty = mo.product_qty
            worksheet2.write(next_row, col, compo_qty, wbf['content_float'])
            col += 1
            # DRC (%) - Using formula: Compo / Lump
            worksheet2.write_formula(next_row, col, 
                f"={xl_rowcol_to_cell(next_row, 7)}/{xl_rowcol_to_cell(next_row, 3)}", 
                wbf['content_percent'])
            col += 1
            # Durasi (Hari) - For Compo (single-stage), leave empty as there's no two-stage process
            worksheet2.write(next_row, col, '', wbf['content'])
            next_row += 1
        
        # Write grandtotal for Lump sheet
        if first_row < next_row:
            col = 1
            worksheet2.write(next_row, col, "TOTAL", wbf['total'])
            col += 1
            worksheet2.write(next_row, col, "", wbf['total'])
            col += 1
            # Sum Lump
            worksheet2.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            # Sum Asam Semut
            worksheet2.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            worksheet2.write(next_row, col, "", wbf['total'])
            col += 1
            worksheet2.write(next_row, col, "", wbf['total'])
            col += 1
            # Sum Compo
            worksheet2.write_formula(next_row, col, 
                f"=SUM({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            col += 1
            # Average DRC (%)
            worksheet2.write_formula(next_row, col, 
                f"={xl_rowcol_to_cell(next_row, 7)}/{xl_rowcol_to_cell(next_row, 3)}", 
                wbf['total_percent'])
            col += 1
            # Average Durasi
            worksheet2.write_formula(next_row, col, 
                f"=AVERAGE({xl_rowcol_to_cell(first_row, col)}:{xl_rowcol_to_cell(next_row - 1, col)})", 
                wbf['total_float'])
            next_row += 1

        worksheet2.set_landscape()
        worksheet2.set_paper(9)
        worksheet2.repeat_rows(1, 2) 
        worksheet2.print_area(0, 0, next_row, col)
        worksheet2.set_print_scale(80)
