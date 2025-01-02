from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = 'stock.picking'

    no_kendaraan    = fields.Char('No. Kendaraan')
    no_expedisi     = fields.Char('No. Expedisi')

    def check_vendor_bill_and_return(self):
        vendor_bills = self.env["account.move"].search([
            ("invoice_origin", "=", self.purchase_id.name),
            ("move_type", "=", "in_invoice"),
        ])

        if vendor_bills.filtered(lambda bill: bill.payment_state == "paid"):
            raise UserError(_("Tidak bisa di Return karena Vendor Bill sudah dalam state Paid"))

        action = self.env.ref("stock.act_stock_return_picking")
        result = action.sudo().read()[0]

        result["context"] = {
            "default_picking_id": self.id,
        }
        return result
