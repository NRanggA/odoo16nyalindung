from odoo import models, fields, api

class MrpAlternatifFinished(models.Model):
    _inherit = 'mrp.production'

    alt_finished_ids = fields.One2many('mrp.alt.finished.line', 'production_id', string='Alternative Finished Lines')
    move_finished_ids = fields.One2many('stock.move', 'production_id', string='Finished Moves', compute='_compute_move_finished_ids')

    @api.depends('alt_finished_ids')
    def _compute_move_finished_ids(self):
        for production in self:
            moves = []
            for alt_line in production.alt_finished_ids:
                moves.append((0, 0, {
                    'product_id': alt_line.product_id.id,
                    'product_uom_qty': alt_line.product_qty,
                    'product_uom': alt_line.uom_id.id,
                    'production_id': production.id,
                    'location_id': production.location_src_id.id,
                    'location_dest_id': production.location_dest_id.id,
                }))
            production.move_finished_ids = moves


class MrpAltFinishedLine(models.Model):
    _name = 'mrp.alt.finished.line'
    _description = 'Alternative Finished Line'

    production_id = fields.Many2one('mrp.production', string='Production')
    product_id = fields.Many2one('product.product', string='Product')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    product_qty = fields.Float(string='Quantity')
    quantity_done = fields.Float(string='Quantity Done')
