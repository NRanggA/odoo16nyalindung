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
    
    # Old
    # def generate_line(self):
    #     self.env['inventory.turnover.line'].search([]).unlink()

    #     category_filter = ""
    #     if self.product_category_ids:
    #         category_ids = tuple(self.product_category_ids.ids)
    #         if len(category_ids) == 1:
    #             category_filter = "AND pt.categ_id = %s" % category_ids[0]
    #         else:
    #             category_filter = "AND pt.categ_id IN %s" % str(category_ids)

    #     query = """
    #         SELECT 
    #             pt.name AS product,
    #             pc.name AS category,
    #             uom.name as uom_name,
    #             SUM(CASE WHEN sm.date < '%s' AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_from,
    #             SUM(CASE WHEN sm.date <= '%s' AND sl.name = 'Stock' THEN product_qty ELSE 0 END) AS total_in_date_to,
    #             SUM(CASE WHEN sm.date >= '%s' and sm.date <= '%s' and sl.name != 'Stock' THEN product_qty ELSE 0 END) AS total_cogs
    #         FROM stock_move sm                                                                                  
    #         LEFT JOIN product_product pp ON pp.id = sm.product_id
    #         LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
    #         LEFT JOIN product_category pc ON pc.id = pt.categ_id
    #         LEFT JOIN stock_location sl ON sl.id = sm.location_dest_id
    #         LEFT JOIN uom_uom uom ON uom.id = pt.uom_id
    #         WHERE sm.state in ('done','assigned')
    #         %s
    #         GROUP BY pt.name, pc.name, uom.name
    #         ORDER BY pc.name, pt.name;
    #     """ % (
    #         self.period_from.strftime('%Y-%m-%d'),
    #         self.period_to.strftime('%Y-%m-%d'),
    #         self.period_from.strftime('%Y-%m-%d'),
    #         self.period_to.strftime('%Y-%m-%d'),
    #         category_filter
    #     )

    #     self._cr.execute(query)
    #     data4 = self._cr.dictfetchall()
    #     model = self.env['inventory.turnover.line']

    #     for data in data4:
    #         cogs = data['total_cogs'] if data['total_cogs'] != 0 else 1
    #         qty_mean = ((data['total_in_date_from'] + data['total_in_date_to']) / 2) if ((data['total_in_date_from'] + data['total_in_date_to']) / 2) != 0 else 1
    #         model.create({
    #             'category': data['category'],
    #             'name': data['product'],
    #             'uom': data['uom_name'],
    #             'start_balance': data['total_in_date_from'],
    #             'end_balance': data['total_in_date_to'],
    #             'cogs': data['total_cogs'],
    #             'doi': ((data['total_in_date_from'] + data['total_in_date_to']) / 2) / cogs,
    #             'ito': data['total_cogs'] / qty_mean,
    #             'stock_availability': data['total_in_date_to'] * 30 / qty_mean,
    #         })
    #     return self.view_tree()


    # New
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
            'date_from': self.period_from.strftime('%Y-%m-%d 00:00:00'),
            'date_to': self.period_to.strftime('%Y-%m-%d 23:59:59'),
        })
        data = self._cr.dictfetchall()

        model = self.env['inventory.turnover.line']
        for row in data:
            start_balance = row['start_balance']
            incoming = row['incoming']
            outgoing = row['outgoing']
            end_balance = row['end_balance']
            cogs = outgoing if outgoing != 0 else 1
            qty_mean = ((start_balance + end_balance) / 2) if ((start_balance + end_balance) / 2) != 0 else 1

            # mengambil total hari 3 bulan kebelakang
            date_from_hits = self.period_to - relativedelta.relativedelta(months=3)
            total_days = (self.period_to - date_from_hits).days

            avg_consumption = cogs / total_days if total_days != 0 else 0

            model.create({
                'category': row['category'],
                'name': row['product'],
                'uom': row['uom_name'],
                'start_balance': start_balance,
                'incoming': incoming,
                'outgoing': outgoing,
                'end_balance': end_balance,
                'cogs': cogs,
                'avg_consumption': avg_consumption,
                # 'doi': ((start_balance + end_balance) / 2) / cogs,
                'ito': end_balance / avg_consumption if avg_consumption != 0 else 0,
                # 'stock_availability':  end_balance / avg_consumption if avg_consumption != 0 else 0,
                'stock_availability': round(end_balance / avg_consumption, 0) if avg_consumption != 0 else 0,

                # 'stock_availability': end_balance * 30 / qty_mean,
            })
        return self.view_tree()

    
    
class InventoryTurnoverLine(models.TransientModel):
    _name = 'inventory.turnover.line'
    _description = 'Inventory Turnover Wizard'

    name = fields.Char(string='Product')
    category = fields.Char(string='Product Category')
    uom = fields.Char(string='Product Uom')
    start_balance = fields.Float(string='Beginning Balance (Qty)')
    end_balance = fields.Float(string='Ending Balance (Qty)')
    cogs = fields.Float(string='COGS/Usage (Qty)')
    # doi = fields.Integer(string='DOI (Days)')
    ito = fields.Integer(string='ITO')
    stock_availability = fields.Integer(string='Stock Availability (Days)')

    # Penambahan fields untuk incoming dan outgoing
    incoming = fields.Float(string='Incoming (Qty)')
    outgoing = fields.Float(string='Outgoing (Qty)')
    avg_consumption = fields.Float(string='Avg Consumption (Qty/Day)')
    

    

