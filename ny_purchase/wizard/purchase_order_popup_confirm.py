from odoo import models, fields

class PurchaseConfirmWizard(models.TransientModel):
    _name = 'purchase.confirm.wizard'
    _description = 'Purchase Confirmation Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')

    # def action_confirm(self):
    #     if self.purchase_order_id:
    #         self.purchase_order_id.button_confirm()
    #     return {'type': 'ir.actions.act_window_close'}
    
    def action_edit(self):
        return {'type': 'ir.actions.act_window_close'}
