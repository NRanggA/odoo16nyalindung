from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    advanced_customer_move_ids = fields.Many2many('account.move','advanced_sale_rel','sale_id','move_id', string='Advanced Purchase',compute="_compute_advanced_customer")
    count_advanced_customer = fields.Integer('Count Advanced Purchase',compute="_compute_advanced_customer")


    def _compute_advanced_customer(self):
        for order in self:
            account = order.env['account.move'].search([('advanced_sales_id', '=', order.id)])
            order.advanced_customer_move_ids = [(6,0,account.ids)]
            order.count_advanced_customer = len(account)


    def action_view_advanced_sales(self):
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        result['domain'] = [('id', '=', self.advanced_customer_move_ids.ids)]
        result['name'] = _('Sales Advance')
        if self.count_advanced_customer == 1:
            result['view_mode'] = 'form'
        return result


    def action_create_advanced_payment(self):
        return {
            'name': _('Create Advanced'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            # 'view_id': self.env.ref('account.view_move_form').id,
            'view_id': self.env.ref('c10i_advanced_payment.view_move_form_inherit_account_advanced_vendor').id,
            'context': {'default_move_type': 'out_invoice','default_partner_id':self.partner_id.id,'default_is_advanced': True,'default_advanced_sales_id':self.id,'advanced_sales':True},
            'domain': "[('move_type', '=', 'out_invoice')]",
            'target': 'new'

        }    

    def action_create_customer_invoice(self):
        # sale.advance.payment.inv
        sale_advanced_payment_id = self.env['sale.advance.payment.inv'].with_context(active_ids=[self.id]).create({
            'advance_payment_method': 'delivered'
        })
        sale_advanced_payment_id.create_invoices()

    def _prepare_invoice(self):
        rec = super(SaleOrder,self)._prepare_invoice()
        rec['sale_order_id'] = self.id
        return rec
        