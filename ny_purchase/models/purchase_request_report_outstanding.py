from odoo import models, fields, tools, api
from datetime import datetime, timedelta

class PurchaseRequestReportOutstanding(models.Model):
    _name = 'purchase.request.report.outstanding'
    _description = 'Report Purchase Request Outstanding'
    _auto = False  
    _order = 'date desc'

    date                     = fields.Datetime('As Of Date', default=fields.Datetime.now)
    purchase_request_id      = fields.Many2one('purchase.request', string='Purchase Request')
    purchase_request_date    = fields.Datetime('PR Date') 
    product_id               = fields.Many2one('product.product', string='Product')
    date_required            = fields.Datetime('Date Required')
    days_count               = fields.Integer('Days Count')

    @api.model
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW purchase_request_report_outstanding AS (
                SELECT
                    row_number() OVER() AS id,
                    timezone('Asia/Jakarta', now()) AS date,
                    pr.id AS purchase_request_id,
                    pr.date_start AS purchase_request_date,
                    prl.product_id AS product_id,
                    prl.date_required AS date_required,
                    EXTRACT(DAY FROM (prl.date_required - timezone('Asia/Jakarta', now())))::int AS days_count
                FROM purchase_request_line prl
                JOIN purchase_request pr ON pr.id = prl.request_id
                LEFT JOIN purchase_request_purchase_order_line_rel rel ON rel.purchase_request_line_id = prl.id
                WHERE pr.state = 'approved'
                AND rel.purchase_order_line_id IS NULL
                ORDER BY pr.date_start DESC
            )
        """)
