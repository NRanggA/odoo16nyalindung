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

    def generate_xlsx_report(self, workbook, data, obj):
        text_style = workbook.add_format({'font_size': 12,  'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'num_format':'_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)' , 'bold': True})
        num_style = workbook.add_format({'font_size': 11,  'align': 'left', 'valign': 'vright', 'text_wrap': True , 'num_format':'_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)' })
        text_style_heading = workbook.add_format({'font_size': 12,  'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True })
        worksheet = workbook.add_worksheet('Sheet 1')
        date_from = '01-01-%s'%(obj.period_from.year)
        date_to = '31-12-%s'%(obj.period_to.year)
        days = (obj.period_to - obj.period_from).days
        self._cr.execute("""
                select 
                    TO_CHAR(
                        sm.date,
                        'dd-mm-yyyy'
                    ) as date,
                    date_part('month',sm.date) AS month,
                    pt.name as product,
                    sl.name as destination,
                    SUM(product_qty) as total_quantity
                from stock_move sm
                left join product_product pp on pp.id = sm.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join stock_location sl on sl.id = sm.location_dest_id
                where sm.date >= '%s' and sm.date <= '%s' and sm.state in ('done','assigned')
                GROUP BY TO_CHAR(sm.date,'dd-mm-yyyy'),date_part('month',sm.date),pt.name,sl.name
                order by pt.name,TO_CHAR(sm.date,'dd-mm-yyyy')
                """ % (date_from, date_to))
        data3 = self._cr.dictfetchall()
        self._cr.execute("""
                    WITH months AS (
                        -- Generate a list of months (1 to 12)
                        SELECT generate_series(1, 12) AS month
                    )
                    SELECT 
                        m.month AS month,
                        pt.name AS product,
                        COALESCE(SUM(sm.product_qty) FILTER (WHERE sl.name = 'Stock'), 0) AS total_quantity,
                        COALESCE(SUM(sm.product_qty) FILTER (WHERE sl.name != 'Stock'), 0) AS total_quantity_deduction,
                        COALESCE(SUM(SUM(sm.product_qty) FILTER (WHERE sl.name = 'Stock')) OVER (PARTITION BY pt.name ORDER BY m.month), 0) AS total_quantity_acumulative,
                        COALESCE(SUM(SUM(sm.product_qty) FILTER (WHERE sl.name != 'Stock')) OVER (PARTITION BY pt.name ORDER BY m.month), 0) AS total_quantity_deduction_acumulative
                    FROM months m
                    CROSS JOIN product_template pt
                    LEFT JOIN product_product pp ON pp.product_tmpl_id = pt.id
                    LEFT JOIN stock_move sm ON sm.product_id = pp.id AND date_part('month', sm.date) = m.month
                    LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
                    WHERE (sm.date IS NULL OR (sm.date >= '%s' AND sm.date <= '%s')) 
                    AND (sm.state IS NULL OR sm.state IN ('done', 'assigned'))
                    GROUP BY m.month, pt.name
                    ORDER BY pt.name, m.month;
                """ % (date_from, date_to))
        data3 = self._cr.dictfetchall()
        self._cr.execute("""
            SELECT 
                pt.name AS product,
                SUM(CASE WHEN sm.date <= '%s' and sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_from,
                SUM(CASE WHEN sm.date <= '%s' and sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_to,
                SUM(CASE WHEN sm.date >= '%s' and sm.date <= '%s' and sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_cogs,
                SUM(CASE WHEN sm.date <= '%s' and sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_out_date_to
            FROM stock_move sm                                                                                  
            LEFT JOIN product_product pp ON pp.id = sm.product_id
			LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
            WHERE sm.state in ('done','assigned')
            GROUP BY pt.name
            ORDER BY pt.name;
            """ % (obj.period_from.strftime('%d-%m-%Y'), obj.period_to.strftime('%d-%m-%Y'),obj.period_from.strftime('%d-%m-%Y'), obj.period_to.strftime('%d-%m-%Y'), obj.period_to.strftime('%d-%m-%Y')))
        data4 = self._cr.dictfetchall()
        header  = ['Product','Beginning Balance (Qty)','Ending Balance (Qty)',
                    'COGS/Usage (Qty)','DOI (Days)','ITO','Stock Availability (Days)']
        header_month = [
            ['Jan',1],['Feb',2],['Mar',3],['Apr',4],
            ['Jun',5],['Jul',6],['Mei',7],['Aug',8],['Sep',9],
            ['Okt',10],['Nov',11],['Des',12]
        ]


        col = 1
        row = 4
        worksheet.write(0,1,'Inventory Turn Over',text_style)
        worksheet.write(1,1,'Period From :    %s'%(obj.period_from.strftime('%d %B %Y')),text_style)
        worksheet.write(2,1,'Period To   :    %s'%(obj.period_to.strftime('%d %B %Y')),text_style)
        worksheet.set_column('A:A',3)
        worksheet.set_column('B:B',35)
        worksheet.set_column('C:N',25)
        for h in header:
            worksheet.write(row,col,h,text_style)
            col+=1
        col = 1
        row+=1
        for data in data4:
            doi = '= (((%s + %s)/2)/%s) * %s' % (xl_rowcol_to_cell(row,2),xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,4),str(days)) if data['total_cogs'] != 0 else '= (((%s + %s)/2)/1) * %s' % (xl_rowcol_to_cell(row,2),xl_rowcol_to_cell(row,3),str(days))
            ito = '= %s/((%s + %s)/2)' % (xl_rowcol_to_cell(row,4),xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,2)) if (data['total_in_date_from'] + data['total_in_date_to'])/2 != 0 else '= %s/1' % (xl_rowcol_to_cell(row,4))
            sa = '= (%s/((%s + %s)/2))*30' % (xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,3),xl_rowcol_to_cell(row,2)) if (data['total_in_date_from'] + data['total_in_date_to'])/2 != 0 else '= %s/1' % (xl_rowcol_to_cell(row,3))
            _list = [
                data['product'],
                data['total_in_date_from'],
                data['total_in_date_to'],
                data['total_cogs'],
                doi,
                ito,
                sa
            ]


            for l in _list:
                worksheet.write(row,col,l,num_style)
                col+=1
            col = 1
            row+=1
        # row+=1
        # col = 2
        # worksheet.write(row,1,'Product',text_style)
        # for h in header_month:
        #     worksheet.write(row,col,h[0],text_style)
        #     col+=1
        # col = 1
        # row-=4
        # products = []
        # for data in data3:
        #     if data['product'] not in products:
        #         row+=5
        #         products.append(data['product'])
        #         worksheet.write(row,1,data['product'],text_style)
        #         worksheet.write(row+1,1,'Saldo Awal',num_style)
        #         worksheet.write(row+2,1,'Pembelian',num_style)
        #         worksheet.write(row+3,1,'Pemakaian',num_style)
        #         worksheet.write(row+4,1,'Saldo Akhir',num_style)
        #         worksheet.write(row+1,2,0,num_style)
        #         worksheet.write(row+2,2,data['total_quantity'],num_style)
        #         worksheet.write(row+3,2,data['total_quantity_deduction'],num_style)
        #         total = data['total_quantity']-data['total_quantity_deduction']
        #         worksheet.write(row+4,2,total,num_style)
        #         worksheet.write(row,2,'=' + xl_rowcol_to_cell(row+4,2),text_style)
        #     else:
        #         worksheet.write(row+1,int(data['month'])+1,total,num_style)
        #         worksheet.write(row+2,int(data['month'])+1,data['total_quantity'],num_style)
        #         worksheet.write(row+3,int(data['month'])+1,data['total_quantity_deduction'],num_style)
        #         total = data['total_quantity']-data['total_quantity_deduction']
        #         worksheet.write(row+4,int(data['month'])+1,data['total_quantity']-data['total_quantity_deduction'],num_style)
        #         worksheet.write(row,int(data['month'])+1,'=' + xl_rowcol_to_cell(row+4,int(data['month'])+1),text_style)

        

