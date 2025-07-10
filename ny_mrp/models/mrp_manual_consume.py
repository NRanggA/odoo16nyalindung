from odoo import models, fields, api, _

class MrpMoveConsume(models.Model):
    _name = 'mrp.manual.consume'
    _description = 'MRP Manual Consume'
    _order = 'date desc, id asc'

    component_consume_production_id = fields.Many2one('mrp.production', string='Production Order for components', 
        check_company=True, index='btree_not_null', required=True)
    workorder_id = fields.Many2one('mrp.workorder', string='Work Order To Consume', 
        check_company=True)
    bom_id = fields.Many2one(related='component_consume_production_id.bom_id', store=True)
    bom_line_id = fields.Many2one('mrp.bom.line', 'BoM Line', domain="[('bom_id','=',bom_id)]")
    product_id = fields.Many2one('product.product', string='Product Consumed', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    consumed_qty = fields.Float('Quantity Consumed')
    date = fields.Date('Date')
    is_confirmed = fields.Boolean('Confirmed')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    
    move_id = fields.Many2one('stock.move', compute='_set_stock_move', store=True, ondelete='restrict')

    @api.depends(
        'product_id',
        'consumed_qty',
        'component_consume_production_id.move_raw_ids',
        'component_consume_production_id.move_raw_ids.product_id')
    def _set_stock_move(self):
        for line in self:
            comp_line_found = line.component_consume_production_id.move_raw_ids.filtered(lambda x: x.product_id.id==line.product_id.id)
            if comp_line_found:
                line.move_id = comp_line_found.id if len(comp_line_found.ids)==1 else comp_line_found[0].id
                line.move_id.quantity_done = line.consumed_qty
            else:
                line.move_id = False

    @api.onchange('bom_line_id')
    def onchange_bom_line(self):
        if self.bom_line_id:
            self.product_id = self.bom_line_id.product_id.id
            self.product_uom = self.bom_line_id.product_uom_id.id
    
    def action_confirm(self):
        self.is_confirmed = True
        self.date = fields.Date.today()