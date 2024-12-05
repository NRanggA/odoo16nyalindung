from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    po_status = fields.Char(string="PO Status",compute="_compute_po_status",store=True)

    @api.depends('line_ids.purchase_lines')
    def _compute_po_status(self):
        for record in self:
            if any(line.purchase_lines for line in record.line_ids):
                record.po_status = "Purchase Order"
            else:
                record.po_status = "Not Yet"
