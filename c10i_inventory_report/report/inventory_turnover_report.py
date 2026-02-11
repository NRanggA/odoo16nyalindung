from xlsxwriter.utility import xl_cell_to_rowcol
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.utility import xl_range
from odoo import fields, models, api, _
from odoo import _, api, fields, models
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta



class ReportSalaryDepartment(models.Model):

    _name = 'report.c10i_inventory_report.inventory_turnover_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Inventory Turnover Report'

    # fungsi lama mas bili
    # def generate_xlsx_report(self, workbook, data, obj):
    #     text_style = workbook.add_format({'font_size': 12,  'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'num_format':'_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)' , 'bold': True})
    #     num_style = workbook.add_format({'font_size': 11,  'align': 'left', 'valign': 'vright', 'text_wrap': True , 'num_format':'_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)' })
    #     text_style_heading = workbook.add_format({'font_size': 12,  'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True })
    #     worksheet = workbook.add_worksheet('Sheet 1')
    #     date_from = '%s-01-01'%(obj.period_from.year)
    #     date_to = '%s-12-31'%(obj.period_to.year)
    #     days = (obj.period_to - obj.period_from).days
    #     self._cr.execute("""
    #             select 
    #                 TO_CHAR(
    #                     sm.date,
    #                     'dd-mm-yyyy'
    #                 ) as date,
    #                 date_part('month',sm.date) AS month,
    #                 pt.name as product,
    #                 sl.name as destination,
    #                 SUM(product_qty) as total_quantity
    #             from stock_move sm
    #             left join product_product pp on pp.id = sm.product_id
    #             left join product_template pt on pt.id = pp.product_tmpl_id
    #             left join stock_location sl on sl.id = sm.location_dest_id
    #             where sm.date >= '%s' and sm.date <= '%s' and sm.state in ('done','assigned')
    #             GROUP BY TO_CHAR(sm.date,'dd-mm-yyyy'),date_part('month',sm.date),pt.name,sl.name
    #             order by pt.name,TO_CHAR(sm.date,'dd-mm-yyyy')
    #             """ % (date_from, date_to))
    #     data3 = self._cr.dictfetchall()
    #     self._cr.execute("""
    #                 WITH months AS (
    #                     -- Generate a list of months (1 to 12)
    #                     SELECT generate_series(1, 12) AS month
    #                 )
    #                 SELECT 
    #                     m.month AS month,
    #                     pt.name AS product,
    #                     COALESCE(SUM(sm.product_qty) FILTER (WHERE sl.name = 'Stock'), 0) AS total_quantity,
    #                     COALESCE(SUM(sm.product_qty) FILTER (WHERE sl.name != 'Stock'), 0) AS total_quantity_deduction,
    #                     COALESCE(SUM(SUM(sm.product_qty) FILTER (WHERE sl.name = 'Stock')) OVER (PARTITION BY pt.name ORDER BY m.month), 0) AS total_quantity_acumulative,
    #                     COALESCE(SUM(SUM(sm.product_qty) FILTER (WHERE sl.name != 'Stock')) OVER (PARTITION BY pt.name ORDER BY m.month), 0) AS total_quantity_deduction_acumulative
    #                 FROM months m
    #                 CROSS JOIN product_template pt
    #                 LEFT JOIN product_product pp ON pp.product_tmpl_id = pt.id
    #                 LEFT JOIN stock_move sm ON sm.product_id = pp.id AND date_part('month', sm.date) = m.month
    #                 LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
    #                 WHERE (sm.date IS NULL OR (sm.date >= '%s' AND sm.date <= '%s')) 
    #                 AND (sm.state IS NULL OR sm.state IN ('done', 'assigned'))
    #                 GROUP BY m.month, pt.name
    #                 ORDER BY pt.name, m.month;
    #             """ % (date_from, date_to))
    #     data3 = self._cr.dictfetchall()
    #     self._cr.execute("""
    #         SELECT 
    #             pt.name AS product,
    #             SUM(CASE WHEN sm.date <= '%s' and sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_from,
    #             SUM(CASE WHEN sm.date <= '%s' and sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_to,
    #             SUM(CASE WHEN sm.date >= '%s' and sm.date <= '%s' and sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_cogs,
    #             SUM(CASE WHEN sm.date <= '%s' and sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_out_date_to
    #         FROM stock_move sm                                                                                  
    #         LEFT JOIN product_product pp ON pp.id = sm.product_id
	# 		LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
    #         LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
    #         WHERE sm.state in ('done','assigned')
    #         GROUP BY pt.name
    #         ORDER BY pt.name;
    #         """ % (obj.period_from.strftime('%Y-%m-%d'), obj.period_to.strftime('%Y-%m-%d'),obj.period_from.strftime('%Y-%m-%d'), obj.period_to.strftime('%Y-%m-%d'), obj.period_to.strftime('%Y-%m-%d')))
    #     data4 = self._cr.dictfetchall()
    #     header  = ['Product','Beginning Balance (Qty)','Ending Balance (Qty)',
    #                 'COGS/Usage (Qty)','DOI (Days)','ITO','Stock Availability (Days)']
    #     header_month = [
    #         ['Jan',1],['Feb',2],['Mar',3],['Apr',4],
    #         ['Jun',5],['Jul',6],['Mei',7],['Aug',8],['Sep',9],
    #         ['Okt',10],['Nov',11],['Des',12]
    #     ]


    #     col = 1
    #     row = 4
    #     worksheet.write(0,1,'Inventory Turn Over',text_style)
    #     worksheet.write(1,1,'Period From :    %s'%(obj.period_from.strftime('%d %B %Y')),text_style)
    #     worksheet.write(2,1,'Period To   :    %s'%(obj.period_to.strftime('%d %B %Y')),text_style)
    #     worksheet.set_column('A:A',3)
    #     worksheet.set_column('B:B',35)
    #     worksheet.set_column('C:N',25)
    #     for h in header:
    #         worksheet.write(row,col,h,text_style)
    #         col+=1
    #     col = 1
    #     row+=1
    #     for data in data4:
    #         doi = '= (((%s + %s)/2)/%s) * %s' % (xl_rowcol_to_cell(row,2),xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,4),str(days)) if data['total_cogs'] != 0 else '= (((%s + %s)/2)/1) * %s' % (xl_rowcol_to_cell(row,2),xl_rowcol_to_cell(row,3),str(days))
    #         ito = '= %s/((%s + %s)/2)' % (xl_rowcol_to_cell(row,4),xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,2)) if (data['total_in_date_from'] + data['total_in_date_to'])/2 != 0 else '= %s/1' % (xl_rowcol_to_cell(row,4))
    #         sa = '= (%s/((%s + %s)/2))*30' % (xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,2)) if (data['total_in_date_from'] + data['total_in_date_to'])/2 != 0 else '= %s/1' % (xl_rowcol_to_cell(row,3))
            
    #         product = data.get('product') or ''
    #         if isinstance(product, dict):
    #             product = product.get('en_US', '')

    #         _list = [
    #             product,
    #             data['total_in_date_from'],
    #             data['total_in_date_to'],
    #             data['total_cogs'],
    #             doi,
    #             ito,
    #             sa
    #         ]


    #         for l in _list:
    #             worksheet.write(row,col,l,num_style)
    #             col+=1
    #         col = 1
    #         row+=1
    #     row+=1
    #     col = 2
    #     worksheet.write(row,1,'Product',text_style)
    #     for h in header_month:
    #         worksheet.write(row,col,h[0],text_style)
    #         col+=1
    #     col = 1
    #     row-=4
    #     products = []
    #     for data in data3:
    #         product1 = data.get('product') or ''
    #         if isinstance(product1, dict):
    #             product1 = product1.get('en_US', '')

    #         if product1 not in products:
    #             row+=5
    #             products.append(product1)
    #             worksheet.write(row,1,product1,text_style)
    #             worksheet.write(row+1,1,'Saldo Awal',num_style)
    #             worksheet.write(row+2,1,'Pembelian',num_style)
    #             worksheet.write(row+3,1,'Pemakaian',num_style)
    #             worksheet.write(row+4,1,'Saldo Akhir',num_style)
    #             worksheet.write(row+1,2,0,num_style)
    #             worksheet.write(row+2,2,data['total_quantity'],num_style)
    #             worksheet.write(row+3,2,data['total_quantity_deduction'],num_style)
    #             total = data['total_quantity']-data['total_quantity_deduction']
    #             worksheet.write(row+4,2,total,num_style)
    #             worksheet.write(row,2,'=' + xl_rowcol_to_cell(row+4,2),text_style)
    #         else:
    #             worksheet.write(row+1,int(data['month'])+1,total,num_style)
    #             worksheet.write(row+2,int(data['month'])+1,data['total_quantity'],num_style)
    #             worksheet.write(row+3,int(data['month'])+1,data['total_quantity_deduction'],num_style)
    #             total = data['total_quantity']-data['total_quantity_deduction']
    #             worksheet.write(row+4,int(data['month'])+1,data['total_quantity']-data['total_quantity_deduction'],num_style)
    #             worksheet.write(row,int(data['month'])+1,'=' + xl_rowcol_to_cell(row+4,int(data['month'])+1),text_style)


    # def generate_xlsx_report(self, workbook, data, obj):
    #     text_style = workbook.add_format({'font_size': 12, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'num_format': '#,##0.00'})
    #     num_style = workbook.add_format({'font_size': 11,  'align': 'left', 'valign': 'vright', 'text_wrap': True , 'num_format':'_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)' })
    #     text_style_heading = workbook.add_format({'font_size': 12, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True})

    #     # Worksheet
    #     worksheet = workbook.add_worksheet('Inventory Turnover')
    #     worksheet.set_column('A:A', 5)
    #     worksheet.set_column('B:B', 35)
    #     worksheet.set_column('C:J', 25)

    #     # Header
    #     row, col = 0, 1
    #     worksheet.write(row, col, 'Inventory Turn Over', text_style)
    #     worksheet.write(row + 1, col, 'Period From: %s' % obj.period_from.strftime('%d %B %Y'), text_style)
    #     worksheet.write(row + 2, col, 'Period To:   %s' % obj.period_to.strftime('%d %B %Y'), text_style)

    #     # Table Header
    #     headers = [
    #         'Product Category',
    #         'Product',
    #         'UoM',
    #         'Beginning Balance (Qty)',
    #         'Ending Balance (Qty)',
    #         'COGS/Usage (Qty)',
    #         'DOI (Days)',
    #         'ITO',
    #         'Stock Availability (Days)'
    #     ]
    #     row += 4
    #     for i, header in enumerate(headers, start=1):
    #         worksheet.write(row, i, header, text_style_heading)

    #     # Filter product category
    #     category_filter = ""
    #     params = [obj.period_from, obj.period_to, obj.period_from, obj.period_to]
    #     if obj.product_category_ids:
    #         if len(obj.product_category_ids) == 1:
    #             category_filter = "AND pt.categ_id = %s"
    #             params.append(obj.product_category_ids.id)
    #         else:
    #             category_filter = "AND pt.categ_id IN %s"
    #             params.append(tuple(obj.product_category_ids.ids))

    #     query = f"""
    #         SELECT 
    #             pt.id AS product_tmpl_id,
    #             pc.name AS category,
    #             uom.name AS uom_name,
    #             SUM(CASE WHEN sm.date < %s AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_from,
    #             SUM(CASE WHEN sm.date <= %s AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_to,
    #             SUM(CASE WHEN sm.date >= %s AND sm.date <= %s AND sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_cogs
    #         FROM stock_move sm                                                                                  
    #         LEFT JOIN product_product pp ON pp.id = sm.product_id
    #         LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
    #         LEFT JOIN product_category pc ON pc.id = pt.categ_id
    #         LEFT JOIN uom_uom uom ON uom.id = pt.uom_id
    #         LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
    #         WHERE sm.state IN ('done', 'assigned')
    #         {category_filter}
    #         GROUP BY pt.id, pc.name, uom.name
    #         ORDER BY pc.name, pt.id
    #     """

    #     self._cr.execute(query, tuple(params))
    #     result = self._cr.dictfetchall()
    #     days = (obj.period_to - obj.period_from).days or 1

    #     row += 1
    #     for data in result:
    #         tmpl_id = data.get('product_tmpl_id')
    #         product = ''
    #         if tmpl_id:
    #             product = self.env['product.template'].browse(tmpl_id).name or ''

    #         category = data.get('category') or ''
            
    #         uom_name = data.get('uom_name') or ''
    #         if isinstance(uom_name, dict):
    #             uom_name = uom_name.get('en_US', '')
            
    #         start = data.get('total_in_date_from') or 0
    #         end = data.get('total_in_date_to') or 0
    #         cogs = data.get('total_cogs') or 0

    #         cogs_for_calc = cogs if cogs != 0 else 1
    #         qty_mean = ((start + end) / 2) if ((start + end) / 2) != 0 else 1

    #         doi = ((start + end) / 2) / cogs_for_calc
    #         # doi = (((start + end) / 2) / cogs_for_calc) * days
    #         ito = cogs / qty_mean
    #         sa = (end * 30) / qty_mean

    #         values = [
    #             category,
    #             product,
    #             uom_name,
    #             start,
    #             end,
    #             cogs,
    #             doi,
    #             ito,
    #             sa
    #         ]

    #         for i, val in enumerate(values, start=1):
    #             style = text_style if i in (1, 2, 3) else num_style
    #             worksheet.write(row, i, val, style)

    #         row += 1



    def generate_xlsx_report(self, workbook, data, obj):
        text_style = workbook.add_format({'font_size': 12, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
        num_style = workbook.add_format({
            'font_size': 11,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'
        })
        text_style_heading = workbook.add_format({
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'bold': True
        })

        # Worksheet
        worksheet = workbook.add_worksheet('Inventory Turnover')
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 35)
        worksheet.set_column('C:K', 25)

        # Header
        row, col = 0, 1
        worksheet.write(row, col, 'Inventory Turn Over', text_style)
        worksheet.write(row + 1, col, 'Period From: %s' % obj.period_from.strftime('%d %B %Y'), text_style)
        worksheet.write(row + 2, col, 'Period To:   %s' % obj.period_to.strftime('%d %B %Y'), text_style)

        # Table Header
        headers = [
            'Product Category',
            'Product',
            'UoM',
            'Beginning Balance (Qty)',
            'Incoming (Qty)',
            'Outgoing (Qty)',
            'Ending Balance (Qty)',
            'COGS/Usage (Qty)',
            'Avg Consumption (Per Day)',
            'ITO',
            'Stock Availability (Days)',
        ]
        row += 4
        for i, header in enumerate(headers, start=1):
            worksheet.write(row, i, header, text_style_heading)

        # category filter
        category_filter = ""
        if obj.product_category_ids:
            category_ids = tuple(obj.product_category_ids.ids)
            if len(category_ids) == 1:
                category_filter = "AND pt.categ_id = %s" % category_ids[0]
            else:
                category_filter = "AND pt.categ_id IN %s" % str(category_ids)

        query = """
            WITH moves AS (
                SELECT
                    sm.id AS move_id,
                    sm.product_id,
                    pt.id AS template_id,
                    pt.name AS product_name,
                    pc.name AS category_name,
                    uom.name AS uom_name,
                    sm.date,
                    sl_src.usage AS src_usage,
                    sl_dest.usage AS dest_usage,
                    sp.picking_type_id,
                    sm.product_qty
                FROM stock_move sm
                JOIN product_product pp ON pp.id = sm.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                JOIN product_category pc ON pc.id = pt.categ_id
                JOIN uom_uom uom ON uom.id = pt.uom_id
                LEFT JOIN stock_location sl_src ON sl_src.id = sm.location_id
                LEFT JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
                WHERE sm.state in ('done','assigned')
                {category_filter}
            )
            SELECT
                m.product_name AS product,
                m.category_name AS category,
                m.uom_name AS uom_name,
                -- Beginning balance: all incoming - outgoing before period_from
                COALESCE(SUM(
                    CASE 
                        WHEN m.date < %(date_from)s AND m.dest_usage = 'internal' THEN m.product_qty
                        WHEN m.date < %(date_from)s AND m.src_usage = 'internal' THEN -m.product_qty
                        ELSE 0 END
                ),0) AS start_balance,
                -- Incoming during the period
                COALESCE(SUM(
                    CASE 
                        WHEN m.date >= %(date_from)s AND m.date <= %(date_to)s 
                            AND m.dest_usage = 'internal' THEN m.product_qty
                        ELSE 0 END
                ),0) AS incoming,
                -- COGS (Penggunaan selama 3 bulan terakhir)
                COALESCE(SUM(
                    CASE
                        WHEN m.date >= (%(date_to)s::timestamp - interval '3 month') 
                            AND m.date <= %(date_to)s
                            AND m.src_usage = 'internal' 
                        THEN m.product_qty
                        ELSE 0 END
                ),0) AS cogs,

                -- Outgoing during the period
                COALESCE(SUM(
                    CASE 
                        WHEN m.date >= %(date_from)s AND m.date <= %(date_to)s 
                            AND m.src_usage = 'internal' THEN m.product_qty
                        ELSE 0 END
                ),0) AS outgoing,
                -- Ending balance = start + incoming - outgoing
                COALESCE(SUM(
                    CASE 
                        WHEN m.date <= %(date_to)s AND m.dest_usage = 'internal' THEN m.product_qty
                        WHEN m.date <= %(date_to)s AND m.src_usage = 'internal' THEN -m.product_qty
                        ELSE 0 END
                ),0) AS end_balance
            FROM moves m
            GROUP BY m.product_name, m.category_name, m.uom_name
            ORDER BY m.category_name, m.product_name
        """.format(category_filter=category_filter)

        self._cr.execute(query, {
            'date_from': obj.period_from.strftime('%Y-%m-%d 00:00:00'),
            'date_to': obj.period_to.strftime('%Y-%m-%d 23:59:59'),
        })
        result = self._cr.dictfetchall()

        # hitung hari 3 bulan kebelakang dari period_to
        date_from_hits = obj.period_to - relativedelta(months=3)
        total_days = (obj.period_to - date_from_hits).days or 1

        row += 1
        for data in result:
            start_balance = data.get('start_balance') or 0
            incoming = data.get('incoming') or 0
            outgoing = data.get('outgoing') or 0
            end_balance = data.get('end_balance') or 0

            # Perhitungan
            cogs = data.get('cogs') or 0
            avg_consumption = cogs / total_days if total_days != 0 else 0
            # avg_inventory = (start_balance + end_balance) / 2 if (start_balance + end_balance) != 0 else 1
            # Jika stock (ending) nya ada, tapi stock consumption nya 0 selama 3 bulan terakhir, maka stock availability dianggap maksimum forcast
            if end_balance > 0 and avg_consumption == 0:
                avg_consumption = end_balance / total_days
            
            ito = end_balance / avg_consumption if avg_consumption != 0 else 0
            # stock_avail = end_balance / avg_consumption if avg_consumption != 0 else 0
            stock_avail = round(end_balance / avg_consumption, 0) if avg_consumption != 0 else 0

            

            product = data.get('product')
            if isinstance(product, dict):
                product = product.get('en_US', '')

            category = data.get('category') or ''
            
            uom_name = data.get('uom_name') or ''
            if isinstance(uom_name, dict):
                uom_name = uom_name.get('en_US', '')

            values = [
                category,
                product,
                uom_name,
                start_balance,
                incoming,
                outgoing,
                end_balance,
                cogs,
                avg_consumption,
                ito,
                stock_avail,
            ]

            for i, val in enumerate(values, start=1):
                style = text_style if i in (1, 2, 3) else num_style
                worksheet.write(row, i, val, style)

            row += 1
