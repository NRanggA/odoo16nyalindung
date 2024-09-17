from odoo import models, fields, tools, api

class PurchaseOrderReportOutstanding(models.Model):
    _name = 'purchase.order.report.outstanding'
    _description = 'Report Purchase Order Outstanding'
    _auto = False  
    _order = 'date desc'

    date                    = fields.Datetime('As Of Date', default=fields.Datetime.now)
    purchase_request_id     = fields.Many2one('purchase.request', string='Purchase Request')
    purchase_request_date   = fields.Datetime('PR Date') 
    purchase_order_id       = fields.Many2one('purchase.order', string='Purchase Order')
    purchase_order_date     = fields.Datetime('PO Date')
    product_id              = fields.Many2one('product.product', string='Product')
    date_planned            = fields.Datetime('Expected Arrival')
    days_count              = fields.Integer('Days Count')

    @api.model
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW purchase_order_report_outstanding AS (
                SELECT
                    row_number() OVER() AS id,
                    (CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'Asia/Jakarta' AS date,
                    po.id AS purchase_order_id,
                    po.date_order AS purchase_order_date,
                    pol.product_id AS product_id,
                    pol.date_planned AS date_planned,
                    EXTRACT(DAY FROM (pol.date_planned - (CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'Asia/Jakarta'))::int AS days_count,
                    pr.id AS purchase_request_id,
                    pr.date_start AS purchase_request_date,
                    'service' AS product_type
                FROM purchase_order_line pol
                JOIN purchase_order po ON po.id = pol.order_id
                LEFT JOIN purchase_request_purchase_order_line_rel rel ON rel.purchase_order_line_id = pol.id
                LEFT JOIN purchase_request_line prl ON prl.id = rel.purchase_request_line_id
                LEFT JOIN purchase_request pr ON pr.id = prl.request_id
                LEFT JOIN product_product pp ON pol.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id 
                WHERE pt.type = 'service'
                AND (pol.product_qty - pol.qty_invoiced) != 0
                
                UNION
                
                SELECT
                    row_number() OVER() AS id,
                    (CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'Asia/Jakarta' AS date,
                    po.id AS purchase_order_id,
                    po.date_order AS purchase_order_date,
                    pol.product_id AS product_id,
                    pol.date_planned AS date_planned,
                    EXTRACT(DAY FROM (pol.date_planned - (CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'Asia/Jakarta'))::int AS days_count,
                    pr.id AS purchase_request_id,
                    pr.date_start AS purchase_request_date,
                    'consu_or_product' AS product_type
                FROM purchase_order_line pol
                JOIN purchase_order po ON po.id = pol.order_id
                LEFT JOIN purchase_request_purchase_order_line_rel rel ON rel.purchase_order_line_id = pol.id
                LEFT JOIN purchase_request_line prl ON prl.id = rel.purchase_request_line_id
                LEFT JOIN purchase_request pr ON pr.id = prl.request_id
                LEFT JOIN product_product pp ON pol.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE pt.type IN ('consu', 'product')
                AND (pol.product_qty - pol.qty_received) != 0
                            
                ORDER BY purchase_order_date DESC
            )
        """)

