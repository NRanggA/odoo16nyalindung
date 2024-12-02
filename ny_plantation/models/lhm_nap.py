from odoo import api, fields, models

class lhm_nap(models.Model):
    _inherit = 'lhm.nap'

    material_receipt_count = fields.Integer(
        compute='_compute_material_receipt_count',
        string='Material Receipt',
    )

    def _compute_material_receipt_count(self):
        for record in self:
            stock_picking_ids = record.pabrik_line_ids.mapped('stock_picking_id')
            record.material_receipt_count = len(stock_picking_ids)

    def action_open_material_receipt(self):
        stock_picking_ids = self.pabrik_line_ids.mapped('stock_picking_id')
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if len(stock_picking_ids) == 1:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = stock_picking_ids.id
        else:
            action['domain'] = [('id', 'in', stock_picking_ids.ids)]
        return action
