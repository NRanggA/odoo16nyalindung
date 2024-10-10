from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    non_credit = fields.Boolean('Non Credit')

    def button_confirm(self):
        if any(line.price_unit == 0.0 for line in self.order_line):
            return {
                'name': 'Peringatan!',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.confirm.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_purchase_order_id': self.id},
            }
        return super(PurchaseOrder, self).button_confirm()
