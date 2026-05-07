from odoo import api, models, fields, _
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name
# from odoo.exceptions import Warning
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta

class RekapBukuKontraktor(models.AbstractModel):
    _name = 'report.nyalindung_report.stock_report_production_xlsx'
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
        worksheet = workbook.add_worksheet("Mutasi Stok")
        
        grand_total_rows = []
        rekap_contractors = {}
        rekap_contractors2 = {}
        rekap2_sumifs_rcond_col = [0,0,0]
        rekap2_sumifs_rsum_col = []

        product_latex = self.env['product.product'].search([('name','=','Lateks')], limit=1)
        product_lump = self.env['product.product'].search([('name','=','Lump')], limit=1)
        product_asamsemut = self.env['product.product'].search([('name','=','Asam Semut')], limit=1)
        sheet_product = self.env['product.product'].search([('name','=','Sheet')], limit=1)
        compound_product = self.env['product.product'].search([('name','=','Compo')], limit=1)
        compound_product2 = self.env['product.product'].search([('name','=','WIP Compo')], limit=1)

        next_row = 2
        col = 1
        worksheet.write(next_row, col, 'Product' , wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, 'Saldo Awal' , wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Penerimaan", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.merge_range(next_row-1, col, next_row-1, col+1, "Pengeluaran", wbf['header'])
        
        worksheet.write(next_row, col, "Proses", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Penjualan", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Penyesuaian", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        worksheet.write(next_row, col, "Saldo Akhir", wbf['header'])
        worksheet.set_column(col,col,10)
        col += 1
        next_row += 1
        
        for c in range(1,col):
            worksheet.write(next_row, c, c, wbf['header_filter'])
        next_row += 1
        worksheet.freeze_panes(next_row, 3)

        datas = []

        last_closing = self.env['closing.production'].search([
            ('date_to','<',obj.from_date),
            ('state','=','done'),
            ('varieties_type','=','karet'),
        ], order='date_to desc', limit=1)
        
        ############################################
        #            Start: Lateks                 #
        ############################################
        # Saldo Awal dr Closing Sebelumnya dari tanggal from_date 
        #               + Penerimaan antara date_to Closing s.d from_date 
        #               + Produksi antara date_to Closing s.d from_date
        #               + DO antara date_to Closing s.d from_date
        #               + Adjustment antara date_to Closing s.d from_date
        if last_closing:
            opening_qty = last_closing.latex_closing_qty
            # Penerimaan antara Tanggal setelah Closing s.d to_date
            prev_latex_in = self.env['timbangan.pabrik'].search([('product_id','=',product_latex.id),
                            ('lhm_nap_id.date_nap','>',last_closing.date_to),
                            ('lhm_nap_id.date_nap','<',obj.from_date),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            opening_qty += sum(prev_latex_in.mapped('qty_received')) if prev_latex_in else 0.0
            # Produksi yang start_date-nya antara Tanggal setelah Closing s.d to_date
            prev_production_sheet = self.env['mrp.production'].search([('product_id','=',sheet_product.id),('state','in',['progress','done']),
                ('date_start','>', last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),('date_start','<', obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            prev_rm_moves = prev_production_sheet.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
            opening_qty -= sum(prev_rm_moves.mapped('product_qty')) if prev_rm_moves else 0.0
            # DO antara Tanggal setelah Closing s.d to_date
            prev_latex_delivery_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            opening_qty -= sum(prev_latex_delivery_moves.mapped('qty_done')) if prev_latex_delivery_moves else 0.0
            # Adjustment antara Tanggal setelah Closing s.d to_date
            prev_latex_adjustment_out_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            prev_latex_adjustment_in_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            opening_qty += (sum(prev_latex_adjustment_in_moves.mapped('qty_done')) if prev_latex_adjustment_in_moves else 0.0) - (sum(prev_latex_adjustment_out_moves.mapped('qty_done')) if prev_latex_adjustment_out_moves else 0.0)
        else:
            opening_qty = 0.0 # TODO: hrsnya dari saldo awal
        
        # IN
        latex_in = self.env['timbangan.pabrik'].search([('product_id','=',product_latex.id),
                        ('lhm_nap_id.date_nap','>=',obj.from_date),
                        ('lhm_nap_id.date_nap','<=',obj.to_date),
                        ('lhm_nap_id.state','in',['confirmed','done'])])
        receiving_qty = sum(latex_in.mapped('qty_received')) if latex_in else 0.0

        # WIP
        production_qty = 0.0
        # production_sheet = self.env['mrp.production'].search([('product_id','=',sheet_product.id),
        #                         ('state','in',['progress','done']),
        #                         ('date_start','>=', obj.from_date.strftime('%Y-%m-%d 00:00:00')),
        #                         ('date_start','<=', obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        production_sheet = self.env['mrp.production'].search([('product_id','=',sheet_product.id),
                                ('state','=','done'),
                                ('date_start','=', False),
                                ('date_finished','>=', obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                ('date_finished','<=', obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        rm_moves = production_sheet.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
        for m in rm_moves:
            # if m.state == 'done':
            #     production_qty += m.quantity_done
            # else:
            #     production_qty += m.product_qty
            production_qty += m.quantity_done
        
        # Unbuild
        unbuild_sheet = self.env['mrp.unbuild'].search([('product_id','=',sheet_product.id),
                ('state','=','done'),
                ('mo_id','in',production_sheet.ids)])
        rm_moves_unbuild = unbuild_sheet.produce_line_ids.filtered(lambda s: s.product_id.id==product_latex.id)
        for m in rm_moves_unbuild:
            # production_qty += m.quantity_done
            production_qty -= m.quantity_done
            # closing.latex_wip_incoming_qty -= sum(rm_moves_unbuild.mapped('product_qty')) if rm_moves_unbuild else 0.0
        
        # OUT
        latex_delivery_moves_out = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        latex_delivery_moves_in = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_id.usage','=','customer'),('location_dest_id.usage','=','internal'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        delivery_qty = (sum(latex_delivery_moves_out.mapped('qty_done')) if latex_delivery_moves_out else 0.0) - (sum(latex_delivery_moves_in.mapped('qty_done')) if latex_delivery_moves_in else 0.0)

        # ADJUSTMENT
        latex_adjustment_out_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        latex_adjustment_in_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        adjustment_qty = (sum(latex_adjustment_in_moves.mapped('qty_done')) if latex_adjustment_in_moves else 0.0) - (sum(latex_adjustment_out_moves.mapped('qty_done')) if latex_adjustment_out_moves else 0.0)
        
        closing_qty = opening_qty + receiving_qty - production_qty - delivery_qty + adjustment_qty
        ### End: Lateks
        ############################################
        
        datas.append({
            'product_id': product_latex.id,
            'product_name': product_latex.name,
            'opening_qty': opening_qty,
            'receiving_qty': receiving_qty,
            'production_qty': production_qty,
            'delivery_qty': delivery_qty,
            'adjustment_qty': adjustment_qty,
            'closing_qty': closing_qty
        })

        ############################################
        #             Start : Lump                 #
        ############################################
        # Saldo Awal dr Closing Sebelumnya dari tanggal from_date 
        #               + Penerimaan antara date_to Closing s.d from_date 
        #               + Produksi antara date_to Closing s.d from_date
        #               + DO antara date_to Closing s.d from_date
        #               + Adjustment antara date_to Closing s.d from_date
        if last_closing:
            opening_qty = last_closing.lump_closing_qty
            # Penerimaan antara Tanggal setelah Closing s.d to_date
            prev_lump_in = self.env['timbangan.pabrik'].search([('product_id','=',product_lump.id),
                            ('lhm_nap_id.date_nap','>',last_closing.date_to),
                            ('lhm_nap_id.date_nap','<',obj.from_date),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            opening_qty += sum(prev_lump_in.mapped('qty_received')) if prev_lump_in else 0.0
            # Produksi yang start_date-nya antara Tanggal setelah Closing s.d to_date
            prev_production_compo = self.env['mrp.production'].search([('product_id','=',compound_product.id),('state','in',['progress','done']),
                ('date_start','>', last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),('date_start','<', obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            prev_rm_moves = prev_production_compo.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
            opening_qty -= sum(prev_rm_moves.mapped('product_qty')) if prev_rm_moves else 0.0
            # DO antara Tanggal setelah Closing s.d to_date
            prev_lump_delivery_moves = self.env['stock.move.line'].search([('product_id','=',product_lump.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            opening_qty -= sum(prev_lump_delivery_moves.mapped('qty_done')) if prev_lump_delivery_moves else 0.0
            # Adjustment antara Tanggal setelah Closing s.d to_date
            prev_lump_adjustment_out_moves = self.env['stock.move.line'].search([('product_id','=',product_lump.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            prev_lump_adjustment_in_moves = self.env['stock.move.line'].search([('product_id','=',product_lump.id),
                                    ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            opening_qty += (sum(prev_lump_adjustment_in_moves.mapped('qty_done')) if prev_lump_adjustment_in_moves else 0.0) - (sum(prev_lump_adjustment_out_moves.mapped('qty_done')) if prev_lump_adjustment_out_moves else 0.0)
        else:
            opening_qty = 0.0 # TODO: hrsnya dari saldo awal
        
        # IN
        lump_in = self.env['timbangan.pabrik'].search([('product_id','=',product_lump.id),
                        ('lhm_nap_id.date_nap','>=',obj.from_date),
                        ('lhm_nap_id.date_nap','<=',obj.to_date),
                        ('lhm_nap_id.state','in',['confirmed','done'])])
        receiving_qty = sum(lump_in.mapped('qty_received')) if lump_in else 0.0

        # WIP
        production_qty = 0.0
        # production_compo = self.env['mrp.production'].search([('product_id','=',compound_product.id),
        #                         ('state','in',['progress','done']),
        #                         ('date_start','>=', obj.from_date.strftime('%Y-%m-%d 00:00:00')),
        #                         ('date_start','<=', obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        production_compo = self.env['mrp.production'].search([('product_id','=',compound_product2.id),
                ('state','=','done'),
                ('date_start','=', False),
                ('date_finished','>=', obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                ('date_finished','<=', obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        rm_moves = production_compo.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
        # production_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
        for m in rm_moves:
            # if m.state == 'done':
            #     production_qty += m.quantity_done
            # else:
            #     production_qty += m.product_qty
            production_qty += m.quantity_done
        
        # Unbuild
        unbuild_compo = self.env['mrp.unbuild'].search([('product_id','=',compound_product2.id),
                ('state','=','done'),
                ('mo_id','in',production_compo.ids)])
        rm_moves_unbuild2 = unbuild_compo.produce_line_ids.filtered(lambda s: s.product_id.id==product_lump.id)
        for m in rm_moves_unbuild2:
            # production_qty += m.quantity_done
            production_qty -= m.quantity_done
            # closing.latex_wip_incoming_qty -= sum(rm_moves_unbuild2.mapped('product_qty')) if rm_moves_unbuild else 0.0

        # OUT
        lump_delivery_moves_out = self.env['stock.move.line'].search([('product_id','=',product_lump.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        lump_delivery_moves_in = self.env['stock.move.line'].search([('product_id','=',product_lump.id),
                                    ('location_id.usage','=','customer'),('location_dest_id.usage','=','internal'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        delivery_qty = (sum(lump_delivery_moves_out.mapped('qty_done')) if lump_delivery_moves_out else 0.0) - (sum(lump_delivery_moves_in.mapped('qty_done')) if lump_delivery_moves_in else 0.0)  

        # ADJUSTMENT
        lump_adjustment_out_moves = self.env['stock.move.line'].search([('product_id','=',product_lump.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        lump_adjustment_in_moves = self.env['stock.move.line'].search([('product_id','=',product_lump.id),
                                ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        adjustment_qty = (sum(lump_adjustment_in_moves.mapped('qty_done')) if lump_adjustment_in_moves else 0.0) - (sum(lump_adjustment_out_moves.mapped('qty_done')) if lump_adjustment_out_moves else 0.0)
        
        closing_qty = opening_qty + receiving_qty - production_qty - delivery_qty + adjustment_qty
        ### End : Lump
        ############################################
        datas.append({
            'product_id': product_lump.id,
            'product_name': product_lump.name,
            'opening_qty': opening_qty,
            'receiving_qty': receiving_qty,
            'production_qty': production_qty,
            'delivery_qty': delivery_qty,
            'adjustment_qty': adjustment_qty,
            'closing_qty': closing_qty
        })

        ############################################
        #            Start : Asam Semut            #
        ############################################
        # Saldo Awal dr Closing Sebelumnya dari tanggal from_date 
        #               + Penerimaan antara date_to Closing s.d from_date 
        #               + Produksi antara date_to Closing s.d from_date
        #               + DO antara date_to Closing s.d from_date
        #               + Adjustment antara date_to Closing s.d from_date
        if last_closing:
            opening_qty = last_closing.sheet_rm_closing_qty
            # Penerimaan antara Tanggal setelah Closing s.d to_date
            prev_receving_asam_semuts = self.env['stock.move.line'].search([('product_id','=',product_asamsemut.id),
                                    ('location_id.usage','in',('supplier','customer','production')),('location_dest_id.usage','=','internal'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            opening_qty += sum(prev_receving_asam_semuts.mapped('qty_done')) if prev_receving_asam_semuts else 0.0
            # Produksi yang start_date-nya antara Tanggal setelah Closing s.d to_date
            prev_out_asam_semut = self.env['mrp.manual.consume'].search([('product_id','=',product_asamsemut.id),
                                    ('date','>',last_closing.date_to),('date','<',obj.from_date),
                                    ('is_confirmed','=',True)])
            opening_qty -= sum(prev_out_asam_semut.mapped('consumed_qty')) if prev_out_asam_semut else 0.0
            # DO antara Tanggal setelah Closing s.d to_date
            # prev_asamsemut_delivery_moves = self.env['stock.move.line'].search([('product_id','=',product_asamsemut.id),
            #                         ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
            #                         ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
            #                         ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            # opening_qty -= sum(prev_asamsemut_delivery_moves.mapped('qty_done')) if prev_asamsemut_delivery_moves else 0.0
            # Adjustment antara Tanggal setelah Closing s.d to_date
            prev_asammsemut_adjustment_out_moves = self.env['stock.move.line'].search([('product_id','=',product_asamsemut.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            prev_asammsemut_adjustment_in_moves = self.env['stock.move.line'].search([('product_id','=',product_asamsemut.id),
                                    ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>',last_closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                    ('date','<',obj.from_date.strftime('%Y-%m-%d 00:00:00'))])
            opening_qty += (sum(prev_asammsemut_adjustment_in_moves.mapped('qty_done')) if prev_asammsemut_adjustment_in_moves else 0.0) - (sum(prev_asammsemut_adjustment_out_moves.mapped('qty_done')) if prev_asammsemut_adjustment_out_moves else 0.0)
        else:
            opening_qty = 0.0 # TODO: hrsnya dari saldo awal
        
        # IN
        receving_asam_semuts = self.env['stock.move.line'].search([('product_id','=',product_asamsemut.id),
                                    ('location_id.usage','in',['supplier','customer','production']),('location_dest_id.usage','=','internal'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        receiving_qty = sum(receving_asam_semuts.mapped('qty_done')) if receving_asam_semuts else 0.0

        # WIP
        # out_asam_semut = self.env['mrp.manual.consume'].search([('product_id','=',product_asamsemut.id),
        #                             ('date','>=',obj.from_date),('date','<=',obj.to_date),
        #                             ('is_confirmed','=',True)])
        # production_qty = sum(out_asam_semut.mapped('consumed_qty')) if out_asam_semut else 0.0
        production_qty = 0.0
        production_all = self.env['mrp.production'].search([('product_id','in',[sheet_product.id, compound_product2.id]),
                ('state','=','done'),
                ('date_start','=', False),
                ('date_finished','>=', obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                ('date_finished','<=', obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        rm_moves = production_all.move_raw_ids.filtered(lambda s: s.product_id.id==product_asamsemut.id)
        # production_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
        for m in rm_moves:
            # if m.state == 'done':
            #     production_qty += m.quantity_done
            # else:
            #     production_qty += m.product_qty
            production_qty += m.quantity_done
        
        # Unbuild
        unbuild_all = self.env['mrp.unbuild'].search([('product_id','in',[sheet_product.id, compound_product2.id]),
                ('state','=','done'),
                ('mo_id','in',production_all.ids)])
        rm_moves_unbuild3 = unbuild_all.produce_line_ids.filtered(lambda s: s.product_id.id==product_asamsemut.id)
        for m in rm_moves_unbuild3:
            # production_qty += m.quantity_done
            production_qty -= m.quantity_done
            # closing.latex_wip_incoming_qty -= sum(rm_moves_unbuild3.mapped('product_qty')) if rm_moves_unbuild else 0.0

        delivery_qty = 0.0

        adjustment_out_moves = self.env['stock.move.line'].search([('product_id','=',product_asamsemut.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        adjustment_in_moves = self.env['stock.move.line'].search([('product_id','=',product_asamsemut.id),
                                ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                ('state','=','done'),('date','>=',obj.from_date.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',obj.to_date.strftime('%Y-%m-%d 23:59:59'))])
        adjustment_qty = (sum(adjustment_in_moves.mapped('qty_done')) if adjustment_in_moves else 0.0) - (sum(adjustment_out_moves.mapped('qty_done')) if adjustment_out_moves else 0.0)

        closing_qty = opening_qty + receiving_qty - production_qty - delivery_qty + adjustment_qty
        ### End : Asam Semut
        ############################################
        datas.append({
            'product_id': product_asamsemut.id,
            'product_name': product_asamsemut.name,
            'opening_qty': opening_qty,
            'receiving_qty': receiving_qty,
            'production_qty': production_qty,
            'delivery_qty': delivery_qty,
            'adjustment_qty': adjustment_qty,
            'closing_qty': closing_qty
        })

        for line in datas:
            col = 1
            worksheet.write(next_row, col, line.get('product_name', ''), wbf['content'])
            col += 1
            worksheet.write(next_row, col, line.get('opening_qty',0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('receiving_qty',0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('production_qty',0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('delivery_qty',0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('adjustment_qty',0), wbf['content_float'])
            col += 1
            worksheet.write(next_row, col, line.get('closing_qty',0), wbf['content_float'])
            col += 1
            next_row += 1

        worksheet.set_landscape()
        worksheet.set_paper(9)
        worksheet.repeat_rows(1, 2) 
        worksheet.print_area(0, 0, next_row, col+1)
        worksheet.set_print_scale(50)