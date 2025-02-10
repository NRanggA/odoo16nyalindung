from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ClosingNursery(models.Model):
    _name = 'closing.nursery' 
    _description = 'Running Vehicle Procedure'
    _rec_name = 'nursery_id'

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    nursery_id = fields.Many2one('lhm.nursery', string='Blok Bibit', ondelete='restrict', required=True)
    dest_account_id = fields.Many2one(related='nursery_id.account_id', store=True, required=False)
    closing_account_id = fields.Many2one('account.account', string='Closing Account')

    opening_qty = fields.Float()
    opening_value = fields.Float()
    old_cost_price = fields.Float(compute='_compute_cost_price')

    incoming_qty = fields.Float()
    adjustment_qty = fields.Float()
    total_cost = fields.Float()

    onhand_value = fields.Float(compute='_compute_onhand')
    onhand_qty = fields.Float(compute='_compute_onhand')
    new_cost_price = fields.Float(compute='_compute_onhand')

    outgoing_move_ids = fields.Many2many('seed.move.line', 'closing_seed_move_line_rel', 'closing_nursery_id', 'move_line_id', string='Outgoing Moves')
    outgoing_qty = fields.Float(compute='_compute_outgoing')
    outgoing_value = fields.Float(compute='_compute_closing')

    closing_qty = fields.Float(compute='_compute_closing')
    closing_value = fields.Float(compute='_compute_closing')

    closing_move_id = fields.Many2one('account.move', string='Journal Entry')
    closing_out_move_ids = fields.Many2many('account.move', 'closing_out_account_move_rel', 'closing_id', 'move_d', string='Seed Out Journal Entries')

    @api.depends('opening_qty', 'opening_value')
    def _compute_cost_price(self):
        for closing in self:
            closing.old_cost_price = closing.opening_value / closing.opening_qty if closing.opening_qty else 0.0

    @api.depends('opening_qty', 'opening_value',
        'incoming_qty', 'adjustment_qty', 'total_cost')
    def _compute_onhand(self):
        for closing in self:
            closing.onhand_qty = closing.opening_qty + closing.incoming_qty + closing.adjustment_qty
            closing.onhand_value = closing.opening_value + closing.total_cost
            closing.new_cost_price = closing.onhand_value/closing.onhand_qty if closing.onhand_qty > 0 else 0.0

    @api.depends('outgoing_move_ids','outgoing_move_ids.qty')
    def _compute_outgoing(self):
        for closing in self:
            closing.outgoing_qty = sum(closing.outgoing_move_ids.mapped('qty')) if closing.outgoing_move_ids else 0.0
    
    @api.depends('onhand_qty', 'onhand_value',  'new_cost_price', 
            'outgoing_qty', 'closing_qty')
    def _compute_closing(self):
        for closing in self:
            closing.outgoing_value = closing.outgoing_qty * closing.new_cost_price
            closing.closing_qty = closing.onhand_qty - closing.outgoing_qty
            closing.closing_value = closing.onhand_value - closing.outgoing_value

    def _get_domain_source_move_lines(self):
        src_account_ids = self.nursery_id.location_id.type_id.activity_ids.account_id.ids
        if not src_account_ids:
            raise ValidationError(_(f"Could not find accounts for all related activity inside Location Type {self.nursery_id.location_id.type_id.code}"))
        domain = [('plantation_location_id','=',self.nursery_id.location_id.id),
                ('parent_state','=','posted'),('date','>=',self.date_from),('date','<=',self.date_to)]
        if len(src_account_ids)==1:
            domain.append(('account_id','=',src_account_ids[0]))
        else:
            domain.append(('account_id','in',src_account_ids))
        return domain

    def compute_initial_and_cost_value(self):
        for closing in self:
            # Get Initial Value
            SeedMoveLine = self.env['seed.move.line']
            # TODO: belom ada statusnya, perlu diupdate kalo sdh ada
            all_in_moves = SeedMoveLine.search([('nursery_id','=',closing.nursery_id.id),
                            ('location_dest_id','=',closing.nursery_id.location_id.id),
                            ('mutation_type_id.type','in',['incoming','adj_in','transfer']),
                            ('date','<',closing.date_from)])
            # TODO: belom ada statusnya, perlu diupdate kalo sdh ada
            all_out_moves = SeedMoveLine.search([('nursery_id','=',closing.nursery_id.id),
                            ('location_src_id','=',closing.nursery_id.location_id.id),
                            ('mutation_type_id.type','in',['outgoing','adj_out','transfer']),
                            ('date','<',closing.date_from)])
            closing.opening_qty = closing.nursery_id.qty + (sum(all_in_moves.mapped('qty')) if all_in_moves else 0.0) - (sum(all_out_moves.mapped('qty')) if all_out_moves else 0.0)
            domain_op = [('plantation_location_id','=',closing.nursery_id.location_id.id),
                ('parent_state','=','posted'),
                ('account_id','=',closing.dest_account_id.id),
                ('date','<',closing.date_from)]
            op_move_lines = self.env['account.move.line'].search(domain_op)
            closing.opening_value = sum(op_move_lines.mapped('balance')) if op_move_lines else 0.0
            # TODO: belom ada statusnya, perlu diupdate kalo sdh ada
            in_moves = SeedMoveLine.search([('nursery_id','=',closing.nursery_id.id),
                            ('location_dest_id','=',closing.nursery_id.location_id.id),
                            ('mutation_type_id.type','in',['incoming','transfer']),
                            ('date','>=',closing.date_from),('date','<=',closing.date_to)])
            closing.incoming_qty = sum(in_moves.mapped('qty')) if in_moves else 0.0
            # TODO: belom ada statusnya, perlu diupdate kalo sdh ada
            adj_in_moves = SeedMoveLine.search([('nursery_id','=',closing.nursery_id.id),
                            ('location_dest_id','=',closing.nursery_id.location_id.id),
                            ('mutation_type_id.type','=','adj_in'),
                            ('date','>=',closing.date_from),('date','<=',closing.date_to)])
            # TODO: belom ada statusnya, perlu diupdate kalo sdh ada
            adj_out_moves = SeedMoveLine.search([('nursery_id','=',closing.nursery_id.id),
                            ('location_src_id','=',closing.nursery_id.location_id.id),
                            ('mutation_type_id.type','=','adj_out'),
                            ('date','>=',closing.date_from),('date','<=',closing.date_to)])
            closing.adjustment_qty = (sum(adj_in_moves.mapped('qty')) if adj_in_moves else 0.0) - sum(adj_out_moves.mapped('qty')) if adj_out_moves else 0.0
            # Summerize Cost 
            source_moves = self.env['account.move.line'].search(closing._get_domain_source_move_lines())
            closing.total_cost = sum(source_moves.mapped('balance')) if source_moves else 0.0

            # Find outgoing
            out_moves = SeedMoveLine.search([('nursery_id','=',closing.nursery_id.id),
                            ('location_src_id','=',closing.nursery_id.location_id.id),
                            ('mutation_type_id.type','=','outgoing'),
                            ('date','>=',closing.date_from),('date','<=',closing.date_to)])
            if out_moves:
                closing.outgoing_move_ids = [(6,0,out_moves.ids)]
            
    def create_account_move(self):
        nursery_journal = self.env.ref('ny_closing.plantation_closing_nursery_journal')
        for closing in self:
            if closing.closing_move_id:
                if closing.closing_move_id.state=='posted':
                    closing.closing_move_id.button_draft()
            # Create Jurnal Closing Bibit
            if closing.total_cost:
                move_lines1 = []
                vals1 = {
                    'name': 'Move Cost Driver to Account Nursery',
                    'plantation_location_type_id': closing.nursery_id.location_type_id.id,
                    'plantation_location_id': closing.nursery_id.location_id.id,
                    # 'plantation_activity_id': False,
                    # 'plantation_src_journal_id': False,
                    'account_id': closing.dest_account_id.id,
                    'debit': closing.total_cost if closing.total_cost > 0 else 0.0,
                    'credit': abs(closing.total_cost) if closing.total_cost < 0 else 0.0,
                }
                move_lines1.append((0,0,vals1))
                vals2 = {
                    'name': 'Move Cost Driver to Account Nursery',
                    'plantation_location_type_id': closing.nursery_id.location_type_id.id,
                    'plantation_location_id': closing.nursery_id.location_id.id,
                    # 'plantation_activity_id': False,
                    'account_id': closing.closing_account_id.id,
                    'debit': abs(closing.total_cost) if closing.total_cost < 0 else 0.0,
                    'credit': closing.total_cost if closing.total_cost > 0 else 0.0,
                }
                move_lines1.append((0,0,vals2))

                move_values1 = {
                    'date': closing.date_to,
                    'journal_id': nursery_journal.id,
                    'move_type': 'entry',
                    'line_ids': move_lines1,
                }
                if closing.closing_move_id:
                    closing.closing_move_id.write(move_values1)
                else:
                    new_move = self.env['account.move'].create(move_values1)
                    closing.closing_move_id = new_move.id
                
            if closing.closing_out_move_ids:
                for xmove in closing.closing_out_move_ids:
                    if xmove.state=='posted':
                        xmove.button_draft()
                        xmove.write({'name': ''})
                    xmove.unlink()
                
                out_move_ids = [] # Journal Outoging Costing
                for sml in closing.outgoing_move_ids:
                    if not sml.qty:
                        continue
                    if not sml.activity_id.account_id:
                        continue

                    move_lines2 = []
                    cost_value = sml.qty * closing.new_cost_price
                    vals3 = {
                        'name': 'Transfer Seed Value to Project',
                        'plantation_location_type_id': sml.location_type_id.id,
                        'plantation_location_id': sml.location_id.id,
                        'plantation_activity_id': sml.activity_id.id,
                        'plantation_src_journal_id': nursery_journal.id,
                        'account_id': sml.activity_id.account_id.id,
                        'debit': cost_value if cost_value > 0 else 0.0,
                        'credit': abs(cost_value) if cost_value < 0 else 0.0,
                    }
                    move_lines2.append((0,0,vals3))
                    vals4 = {
                        'name': 'Transfer Seed Value to Project',
                        'plantation_location_type_id': closing.nursery_id.location_type_id.id,
                        'plantation_location_id': closing.nursery_id.location_id.id,
                        # 'plantation_activity_id': False,
                        'account_id': closing.dest_account_id.id,
                        'debit': abs(cost_value) if cost_value < 0 else 0.0,
                        'credit': cost_value if cost_value > 0 else 0.0,
                    }
                    move_lines2.append((0,0,vals4))

                    move_values2 = {
                        'date': closing.date_to,
                        'journal_id': nursery_journal.id,
                        'move_type': 'entry',
                        'line_ids': move_lines2,
                    }
                    new_out_move = self.env['account.move'].create(move_values2)
                    out_move_ids.append(new_out_move.id)
                if out_move_ids:
                    closing.closing_out_move_ids = [(6,0,out_move_ids)]
        return True

    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_source_move_lines()
        return action

    def action_view_seed_out_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = [('id','in',self.closing_out_move_ids.line_ids.ids)]
        return action

    def action_view_seed_move(self):
        # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
        pass

    def action_view_seed_in_move(self):
        # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
        pass

    def action_view_seed_out_move(self):
        # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
        pass

    def action_view_seed_adj_move(self):
        # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
        pass