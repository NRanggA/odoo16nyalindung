from odoo import models, fields, api, _
from datetime import datetime

class WizardPurchaseOrderOutstanding(models.TransientModel):
    _name           = 'wizard.purchase.order.outstanding'
    _description    = 'Wizard Puchase Order Outstanding'

    date    = fields.Datetime('Tanggal')

    def action_po(self):
        if not self.date:
            raise ValueError(_("Tanggal harus diisi!"))

        purchase_orders = self.env['purchase.order'].search([('date_planned', '>=', self.date)])
        print(f"Purchase Orders ditemukan: {purchase_orders}")

        purchase_requests = self.env['purchase.request'].search([('line_ids.purchase_lines.order_id', 'in', purchase_orders.ids)])
        print(f"Purchase Request ditemukan: {purchase_requests}")

        report_outstanding_model = self.env['purchase.order.report.outstanding']
        report_outstanding_model.search([]).unlink()

        request_mapping = {}
        for pr in purchase_requests:
            for line in pr.line_ids:
                if line.purchase_lines:
                    for po_line in line.purchase_lines:
                        request_mapping[po_line.order_id.id] = pr

        for po in purchase_orders.order_line:
            date_self       = datetime.combine(self.date, datetime.min.time())
            date_planned    = po.date_planned
            
            if date_planned:
                days_count = (date_planned - date_self).days
            else:
                days_count = 0

            purchase_request        = request_mapping.get(po.order_id.id)
            purchase_request_id     = purchase_request.id if purchase_request else False
            purchase_request_date   = purchase_request.date_start if purchase_request else False

            vals = {
                'date'                  : self.date,
                'purchase_request_id'   : purchase_request_id,
                'purchase_request_date' : purchase_request_date,
                'purchase_order_id'     : po.order_id.id,
                'purchase_order_date'   : po.order_id.date_order or False,
                'product_id'            : po.product_id.id or False,
                'date_planned'          : po.date_planned or False,
                'days_count'            : days_count,
            }

            new_record = report_outstanding_model.create(vals)
            print(f"Record yang berhasil dibuat: {new_record}")

        action = self.env.ref('ny_purchase.purchase_order_report_outstanding_action').read()[0]
        return action


