from odoo import models, fields, tools, api

class PurchaseOrderMonitoring(models.Model):
    _name = 'purchase.order.monitoring'
    _description = 'Purchase Order Monitoring'
    _auto = False  
    _order = 'po_minus_pr_days desc'

    product_id               = fields.Many2one('product.product', string='Product')
    purchase_request_id      = fields.Many2one('purchase.request', string='Purchase Request')
    purchase_order_id        = fields.Many2one('purchase.order', string='Purchase Order')
    grn_id                   = fields.Many2one('stock.picking', string='Goods Receipt Note (GRN)')
    vb_id                    = fields.Many2one('account.move', string='Vendor Bill')
    po_minus_pr_days         = fields.Integer('PR > PO (Days)')
    grn_minus_po_days        = fields.Integer('PO > GRN (Days)')
    vb_minus_grn_days        = fields.Integer('GRN > VB (Days)')
    vb_minus_po_days         = fields.Integer('VB > PO (Days)')

    @api.model
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW purchase_order_monitoring AS (
                SELECT 
                    row_number() OVER() AS id,
                    pp.id AS product_id,
                    pr.id AS purchase_request_id,
                    po.id AS purchase_order_id,
                    sp.id AS grn_id,
                    am.id AS vb_id,
                    CASE 
                        WHEN pt.type = 'service' THEN (po.date_approve::date - pr.date_start::date)
                        ELSE (po.date_approve::date - pr.date_start::date)
                    END AS po_minus_pr_days,
                    CASE 
                        WHEN pt.type = 'service' THEN NULL
                        ELSE (sp.date_done::date - po.date_approve::date)
                    END AS grn_minus_po_days,
                    CASE 
                        WHEN pt.type = 'service' THEN NULL
                        ELSE (am.date::date - sp.date_done::date)
                    END AS vb_minus_grn_days,
                    CASE 
                        WHEN pt.type = 'service' THEN (am.date::date - po.date_approve::date)
                        ELSE NULL
                    END AS vb_minus_po_days
                FROM 
                    stock_picking sp
                LEFT JOIN 
                    purchase_order po ON sp.origin = po.name
                LEFT JOIN 
                    purchase_order_line pol ON pol.order_id = po.id
                LEFT JOIN 
                    purchase_request_purchase_order_line_rel rel ON rel.purchase_order_line_id = pol.id
                LEFT JOIN 
                    purchase_request_line prl ON prl.id = rel.purchase_request_line_id
                LEFT JOIN 
                    purchase_request pr ON pr.id = prl.request_id
                LEFT JOIN 
                    product_product pp ON pol.product_id = pp.id
                LEFT JOIN 
                    product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN 
                    account_move am ON am.invoice_origin = po.name
                WHERE 
                    sp.state IN ('done', 'assigned')
                    AND po.state = 'purchase'
                    AND am.state = 'posted'
                ORDER BY 
                    sp.date_done DESC
            )
        """)
