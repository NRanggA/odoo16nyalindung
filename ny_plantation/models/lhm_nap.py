from odoo import api, fields, models

class lhm_nap(models.Model):
    _inherit = 'lhm.nap'

    material_receipt_count = fields.Integer(compute='_compute_material_receipt_count', string='Material Receipt',)

    def _compute_material_receipt_count(self):
        for record in self:
            stock_move_ids = record.pabrik_line_ids.mapped('stock_move_ids.picking_id')
            record.material_receipt_count = len(stock_move_ids)

    def action_open_material_receipt(self):
        stock_move_ids = self.pabrik_line_ids.mapped('stock_move_ids.picking_id')
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if len(stock_move_ids) == 1:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = stock_move_ids.id
        else:
            action['domain'] = [('id', 'in', stock_move_ids.ids)]
        return action

    unique_lhm_transaction_ids = fields.Many2many('lhm.transaction', string="Laporan Harian Mandor", compute='_compute_unique_lhm_transactions')

    @api.depends('line_ids.lhm_transaction_nap_id.lhm_id')
    def _compute_unique_lhm_transactions(self):
        for nap in self:
            lhm_transactions = nap.line_ids.mapped('lhm_transaction_nap_id.lhm_id')
            unique_ids = list(set(lhm_transactions.ids))
            nap.unique_lhm_transaction_ids = [(6, 0, unique_ids)]

    def action_open_related_lhm_transactions(self):
        self.ensure_one()
        action = self.env.ref('c10i_lhm_v16.action_lhm_transaction_button_box').read()[0]
        action['domain'] = [('id', 'in', self.unique_lhm_transaction_ids.ids)]
        return action
