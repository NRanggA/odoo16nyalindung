from odoo import _, api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    advanced_vendor_move_ids = fields.Many2many('account.move','advanced_purchase_rel','purchase_id','move_id', string='Advanced Purchase',compute="_compute_advanced_purchase")
    count_advanced_purchase = fields.Integer('Count Advanced Purchase',compute="_compute_advanced_purchase")


    def _compute_advanced_purchase(self):
        for order in self:
            account = order.env['account.move'].search([('advanced_purchase_id', '=', order.id)])
            order.advanced_vendor_move_ids = [(6,0,account.ids)]
            order.count_advanced_purchase = len(account)
    
    def action_view_advanced_purchase(self):
        result = self.env['ir.actions.act_window']._for_xml_id('c10i_advanced_payment.action_vendor_bill_advanced')
        result['domain'] = [('id', '=', self.advanced_vendor_move_ids.ids)]
        result['name'] = _('Purchase Advanced')
        if self.count_advanced_purchase == 1:
            result['view_mode'] = 'form'
        return result

    def action_create_advanced_payment(self):
        if hasattr(self, 'button_done') and callable(getattr(self, 'button_done')):
            self.button_done()
        return {
            'name': _('Create Advanced'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.advance.payment.inv',
            # 'view_id': self.env.ref('account.view_move_form').id,
            'view_id': self.env.ref('c10i_advanced_payment.view_purchase_order_advance_payment_inv').id,
            # 'context': {'default_move_type': 'in_invoice',
            #             'default_partner_id':self.partner_id.id,
            #             'default_is_advanced': True,
            #             'default_advanced_purchase_id':self.id,
            #             'advanced_purchase':True,
            #             },
            # 'domain': "[('move_type', '=', 'in_invoice')]",
            'target': 'new'
        }
