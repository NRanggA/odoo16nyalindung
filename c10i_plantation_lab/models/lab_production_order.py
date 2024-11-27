from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class LabOrder(models.Model):
    _name = 'lab.production.order'
    _description = 'Lab Production Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Order No.')
    lab_product_id = fields.Many2one('lab.product', string='Product', required=True, ondelete='restrict')
    product_qty = fields.Float('Quantity to Produce')
    qty_done = fields.Float('Finished Qty')
    
    date_start = fields.Datetime('Start Date')
    date_end = fields.Datetime('Finished Date')
    
    state = fields.Selection([('draft','New'),('inprogress','InProgress'),('done','Done'),('cancel','Cancelled')], 
                    string='Status', default='draft')

    def unlink(self):
        for order in self:
            if order.state != 'cancel':
                raise ValidationError(_('You cannot delete an order if not in cancel state'))
        return super(LabOrder, self).unlink()
    
    def action_confirm(self):
        for order in self:
            if not order.name:
                order.name = self.env['ir.sequence'].next_by_code(self._name)
            order.state = 'inprogress'
            order.date_start = fields.Datetime.now()
    
    def action_done(self):
        for order in self:
            order.state = 'done'
            order.date_end = fields.Datetime.now()

    def action_cancel(self):
        for order in self:
            order.state = 'cancel'
    
    def action_set_draft(self):
        for order in self:
            if order.state != 'cancel':
                raise ValidationError(_('You cannot set draft if not in cancel state'))
            order.state = 'draft'

    def action_view_moves(self):
        pass