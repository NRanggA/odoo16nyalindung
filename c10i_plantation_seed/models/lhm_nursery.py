from odoo import models, fields, api, _

class lhm_nursery(models.Model):
    _inherit     = 'lhm.nursery'

    qty                 = fields.Float("Jumlah", compute="_compute_nursery_qty", store=True)
    seed_move_line_ids  = fields.One2many('seed.move.line', 'nursery_id', string='Seed Move Line')

    def action_show_transaction_bibitan(self):
        for rec in self:
            seed_move_line_ids = []
            seed_move_line_ids.extend(rec.seed_move_line_ids.ids)  

            return {
                'type': 'ir.actions.act_window',
                'name': 'Seed Move Line',
                'view_mode': 'tree',
                'view_id': self.env.ref('c10i_plantation_seed.seed_move_line_nursery_view_tree').id,
                'target': 'current',
                'domain': [('id', 'in', seed_move_line_ids)],
                'res_model': 'seed.move.line', 
            }

    @api.depends('seed_move_line_ids.qty', 'seed_move_line_ids.mutation_type_id')
    def _compute_nursery_qty(self):
        for rec in self:
            total_awal = 0.0 
            for line in rec.seed_move_line_ids:
                if line.mutation_type_id.type == 'transfer':
                    if line.location_dest_id and not line.location_src_id:
                        total_awal += line.qty
                    if line.location_src_id and not line.location_dest_id:
                        total_awal -= line.qty
                elif line.mutation_type_id.type in ['incoming', 'adj_in']:
                    total_awal += line.qty
                elif line.mutation_type_id.type in ['outgoing', 'adj_out']:
                    total_awal -= line.qty
            rec.qty = max(total_awal, 0.0)