from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    manual_consume_ids = fields.One2many('mrp.manual.consume', 'move_id', string='Manual Consume')
    lock_consume_qty = fields.Boolean(compute='_compute_lock_consume_qty', string='Lock Consume Qty', readonly=True, store=True)

    @api.depends('manual_consume_ids')
    def _compute_lock_consume_qty(self):
        for move in self:
            # If there are manual consumes, lock the consume quantity
            move.lock_consume_qty = bool(move.manual_consume_ids)