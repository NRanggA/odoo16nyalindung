from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class LabOrder(models.Model):
    _name = 'lab.production.order'
    _description = 'Lab Production Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Order No.')
    lab_product_id = fields.Many2one('lab.product', string='Product', required=True, ondelete='restrict')
    lab_product_satuan_id = fields.Many2one('uom.uom',string='Satuan', related='lab_product_id.product_id.uom_id', store=True, readonly=True)
    product_qty = fields.Float('Quantity to Produce', tracking=True)
    qty_done = fields.Float('Finished Qty', tracking=True)
    
    date_start = fields.Datetime('Start Date')
    date_end = fields.Datetime('Finished Date')

    picking_ids = fields.Many2many('stock.picking', 'lab_prod_order_picking_rel', string='Production')
    
    state = fields.Selection([('draft','New'),('inprogress','InProgress'),('done','Done'),('cancel','Cancelled')], 
                    string='Status', default='draft', tracking=True)

    def unlink(self):
        for order in self:
            if order.state != 'cancel':
                raise ValidationError(_('You cannot delete an order if not in cancel state'))
            if order.name: 
                raise ValidationError(_('You cannot delete an order if the name is filled'))
        return super(LabOrder, self).unlink()
    
    def action_confirm(self):
        for order in self:
            if order.product_qty == 0:
                raise ValidationError(_('Product Quantity cannot be 0.'))
            if not order.name:
                order.name = self.env['ir.sequence'].next_by_code(self._name)
            order.state = 'inprogress'
            order.date_start = fields.Datetime.now()
    
    def action_done(self):
        for order in self:
            order.state = 'done'
            order.date_end = fields.Datetime.now()
            order.create_picking()

    def action_cancel(self):
        for order in self:
            order.state = 'cancel'
            order.date_start = False
            order.date_end = False
    
    def action_set_draft(self):
        for order in self:
            if order.state != 'cancel':
                raise ValidationError(_('You cannot set draft if not in cancel state'))
            order.state = 'draft'

    def _prepare_move_lines(self):
        return {
            'name': self.lab_product_id.product_id.name,
            'product_id': self.lab_product_id.product_id.id,
            'product_uom': self.lab_product_id.product_id.uom_id.id,
            'product_uom_qty': self.qty_done,
            'location_id': self.env.ref('c10i_plantation_lab.loc_virtual_kebun_lab_loc_1').id,
            'location_dest_id': self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id,
        }
    
    def create_picking(self):
        self.ensure_one()
        picking_type = self.env.ref('c10i_plantation_lab.picking_type_lab_1')
        int_picking_vals = {
            'picking_type_id': picking_type.id,
            'move_ids': [(0,0,self._prepare_move_lines())],
        } 
        picking = self.env['stock.picking'].create(int_picking_vals)
        picking.action_confirm()
        picking.action_assign()
        # if picking.state=='assigned':
        #     # picking.move_ids.action_done()
        #     picking.action_set_quantities_to_reservation()
        #     picking.button_validate()
        self.picking_ids = [(6,0,picking.ids)]

    def action_view_moves(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['domain'] = [('picking_id','=',self.picking_ids.id)]
        return action
        