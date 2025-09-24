from odoo import _, api, fields, models
from datetime import datetime
from dateutil import relativedelta


class WizardInventoryTurnover(models.TransientModel):
    _name = 'wizard.inventory.turnover'
    _description = 'Inventory Turnover Wizard'

    period_from = fields.Date(string='Period From', default=datetime.now().strftime('%Y-%m-01'))
    period_to = fields.Date(string='Period To', default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1)))
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id.id)

    product_category_ids = fields.Many2many('product.category', string='Product Categories')

    def action_download_report(self):
        return self.env.ref('c10i_inventory_report.inventory_turnover_xlsx').report_action(self)
    
    def view_tree(self):        
        action = self.env.ref('c10i_inventory_report.inventory_turnover_line_action').sudo().read()[0]
        
        return action
    
    def generate_line(self):
        self.env['inventory.turnover.line'].search([]).unlink()

        category_filter = ""
        if self.product_category_ids:
            category_ids = tuple(self.product_category_ids.ids)
            if len(category_ids) == 1:
                category_filter = "AND pt.categ_id = %s" % category_ids[0]
            else:
                category_filter = "AND pt.categ_id IN %s" % str(category_ids)

        query = """
            SELECT 
                pt.name AS product,
                pc.name AS category,
                uom.name as uom_name,
                SUM(CASE WHEN sm.date < '%s' AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_from,
                SUM(CASE WHEN sm.date <= '%s' AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_to,
                SUM(CASE WHEN sm.date >= '%s' and sm.date <= '%s' and sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_cogs
            FROM stock_move sm                                                                                  
            LEFT JOIN product_product pp ON pp.id = sm.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc ON pc.id = pt.categ_id
            LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
            LEFT JOIN uom_uom uom ON uom.id = pt.uom_id
            WHERE sm.state in ('done','assigned')
            %s
            GROUP BY pt.name, pc.name, uom.name
            ORDER BY pc.name, pt.name;
        """ % (
            self.period_from.strftime('%Y-%m-%d'),
            self.period_to.strftime('%Y-%m-%d'),
            self.period_from.strftime('%Y-%m-%d'),
            self.period_to.strftime('%Y-%m-%d'),
            category_filter
        )

        self._cr.execute(query)
        data4 = self._cr.dictfetchall()
        model = self.env['inventory.turnover.line']

        for data in data4:
            cogs = data['total_cogs'] if data['total_cogs'] != 0 else 1
            qty_mean = ((data['total_in_date_from'] + data['total_in_date_to']) / 2) if ((data['total_in_date_from'] + data['total_in_date_to']) / 2) != 0 else 1
            model.create({
                'category': data['category'],
                'name': data['product'],
                'uom': data['uom_name'],
                'start_balance': data['total_in_date_from'],
                'end_balance': data['total_in_date_to'],
                'cogs': data['total_cogs'],
                'doi': ((data['total_in_date_from'] + data['total_in_date_to']) / 2) / cogs,
                'ito': data['total_cogs'] / qty_mean,
                'stock_availability': data['total_in_date_to'] * 30 / qty_mean,
            })
        return self.view_tree()


    # def generate_line(self):

    #     self.env['inventory.turnover.line'].search([]).unlink()
    #     self._cr.execute("""
    #         SELECT 
    #             pt.name AS product,
    #             SUM(CASE WHEN sm.date < '%s' AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_from,
    #             SUM(CASE WHEN sm.date <= '%s' AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_to,
    #             SUM(CASE WHEN sm.date >= '%s' and sm.date <= '%s' and sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_cogs
    #         FROM stock_move sm                                                                                  
    #         LEFT JOIN product_product pp ON pp.id = sm.product_id
	# 		LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
    #         LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
    #         WHERE sm.state in ('done','assigned')
    #         GROUP BY pt.name
    #         ORDER BY pt.name;
    #         """ % (self.period_from.strftime('%Y-%m-%d'), self.period_to.strftime('%Y-%m-%d'),self.period_from.strftime('%Y-%m-%d'), self.period_to.strftime('%Y-%m-%d')))
    #     data4 = self._cr.dictfetchall()
    #     model = self.env['inventory.turnover.line']

    #     for data in data4:
    #         cogs = data['total_cogs'] if data['total_cogs'] != 0 else 1
    #         qty_mean = ((data['total_in_date_from']+data['total_in_date_to'])/2) if ((data['total_in_date_from']+data['total_in_date_to'])/2) != 0 else 1
    #         model.create({
    #             'name' : data['product'],
    #             'start_balance' : data['total_in_date_from'],
    #             'end_balance' : data['total_in_date_to'],
    #             'cogs' : data['total_cogs'],
    #             'doi' : ((data['total_in_date_from']+data['total_in_date_to'])/2)/cogs,
    #             'ito' : data['total_cogs']/qty_mean,
    #             'stock_availability' : data['total_in_date_to']*30/qty_mean,
    #         })
    #     return self.view_tree()
    
class InventoryTurnoverLine(models.TransientModel):
    _name = 'inventory.turnover.line'
    _description = 'Inventory Turnover Wizard'

    name = fields.Char(string='Product')
    category = fields.Char(string='Product Category')
    uom = fields.Char(string='Product Uom')
    start_balance = fields.Float(string='Beginning Balance (Qty)')
    end_balance = fields.Float(string='Ending Balance (Qty)')
    cogs = fields.Float(string='COGS/Usage (Qty)')
    doi = fields.Integer(string='DOI (Days)')
    ito = fields.Integer(string='ITO')
    stock_availability = fields.Integer(string='Stock Availability (Days)')
    

    

