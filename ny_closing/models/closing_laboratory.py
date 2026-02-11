from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ClosingLaboratory(models.Model):
    _name = 'closing.laboratory' 
    _description = 'Closing Laboratorium Procedure'
    _rec_name = 'lab_product_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')
    
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    lab_product_id = fields.Many2one('lab.product', string='Product', ondelete='restrict', required=True)
    
    opening_wip_qty = fields.Float()
    opening_wip_value = fields.Float()
    incoming_wip_qty = fields.Float()
    wip_cost_consumed = fields.Float()
    onhand_wip_qty = fields.Float(compute='_compute_onhand_wip', store=True)
    onhand_wip_value = fields.Float(compute='_compute_onhand_wip', store=True)
    new_wip_cost_price = fields.Float(compute='_compute_onhand_wip', store=True)
    outgoing_wip_qty = fields.Float()
    outgoing_wip_value = fields.Float(compute='_compute_closing_wip', store=True)
    closing_wip_qty = fields.Float(compute='_compute_closing_wip', store=True)
    closing_wip_value = fields.Float(compute='_compute_closing_wip', store=True)

    opening_fg_qty = fields.Float()
    opening_fg_value = fields.Float()
    incoming_fg_qty = fields.Float()
    incoming_fg_value = fields.Float(compute='_compute_closing_wip', store=True)
    onhand_fg_qty = fields.Float(compute='_compute_onhand_fg', store=True)
    onhand_fg_value = fields.Float(compute='_compute_onhand_fg', store=True)
    new_fg_cost_price = fields.Float(compute='_compute_onhand_fg', store=True)
    outgoing_fg_qty = fields.Float(compute='_compute_outgoing_fg', store=True)
    outgoing_stock_move_ids = fields.Many2many('stock.move', 'closing_lab_stock_move_rel', string='Outgoing FG Stock Moves')
    outgoing_fg_value = fields.Float(compute='_compute_closing_fg', store=True)
    adjustment_fg_qty = fields.Float(string='Adjustment Qty')
    adjustment_fg_qty_value = fields.Float(compute='_compute_closing_fg', string='Adjustment Value based on Qty', store=True)
    adjustment_fg_only_value = fields.Float(string='Adjustment Cost Price Value', readonly=False)
    adjustment_fg_value = fields.Float(compute='_compute_closing_fg', string='Adjustment Value', store=True)
    closing_fg_qty = fields.Float(compute='_compute_closing_fg', store=True)
    closing_fg_value = fields.Float(compute='_compute_closing_fg', store=True)

    closing_move_id = fields.Many2one('account.move', string='Journal Entry')

    @api.depends('opening_wip_qty', 'opening_wip_value',
        'incoming_wip_qty', 'wip_cost_consumed')
    def _compute_onhand_wip(self):
        for closing in self:
            closing.onhand_wip_qty = closing.opening_wip_qty + closing.incoming_wip_qty
            closing.onhand_wip_value = closing.opening_wip_value + closing.wip_cost_consumed
            closing.new_wip_cost_price = closing.onhand_wip_value/closing.onhand_wip_qty if closing.onhand_wip_qty > 0 else 0.0
    
    @api.depends('onhand_wip_qty', 'onhand_wip_value',  'new_wip_cost_price', 
            'outgoing_wip_qty')
    def _compute_closing_wip(self):
        for closing in self:
            closing.outgoing_wip_value = closing.outgoing_wip_qty * closing.new_wip_cost_price
            closing.incoming_fg_value = closing.outgoing_wip_value
            closing.closing_wip_qty = closing.onhand_wip_qty - closing.outgoing_wip_qty
            closing.closing_wip_value = closing.onhand_wip_value - closing.outgoing_wip_value
    
    @api.depends('opening_fg_qty', 'opening_fg_value',
        'incoming_fg_qty', 'incoming_fg_value')
    def _compute_onhand_fg(self):
        for closing in self:
            closing.onhand_fg_qty = closing.opening_fg_qty + closing.incoming_fg_qty
            closing.onhand_fg_value = closing.opening_fg_value + closing.incoming_fg_value
            closing.new_fg_cost_price = closing.onhand_fg_value/closing.onhand_fg_qty if closing.onhand_fg_qty > 0 else 0.0

    @api.depends('outgoing_stock_move_ids')
    def _compute_outgoing_fg(self):
        for closing in self:
            closing.outgoing_fg_qty = sum(closing.outgoing_stock_move_ids.mapped('product_qty')) if closing.outgoing_stock_move_ids else 0.0

    @api.depends('onhand_fg_qty', 'onhand_fg_value',  'new_fg_cost_price', 
            'outgoing_fg_qty', 'adjustment_fg_qty', 'adjustment_fg_only_value')
    def _compute_closing_fg(self):
        for closing in self:
            closing.outgoing_fg_value = closing.outgoing_fg_qty * closing.new_fg_cost_price
            closing.adjustment_fg_qty_value = closing.adjustment_fg_qty * closing.new_fg_cost_price
            closing.adjustment_fg_value = closing.adjustment_fg_qty_value + closing.adjustment_fg_only_value
            closing.closing_fg_qty = closing.onhand_fg_qty - closing.outgoing_fg_qty + closing.adjustment_fg_qty
            closing.closing_fg_value = closing.onhand_fg_value - closing.outgoing_fg_value + closing.adjustment_fg_value
    
    def _get_domain_source_move_lines(self):
        src_account_ids = self.lab_product_id.location_id.type_id.activity_ids.account_id.ids
        if not src_account_ids:
            raise ValidationError(_(f"Could not find accounts for all related activity inside Location Type {self.lab_product_id.location_id.type_id.code}"))
        domain = [('plantation_location_id','=',self.lab_product_id.location_id.id),
                ('parent_state','=','posted')]
        if len(src_account_ids)==1:
            domain.append(('account_id','=',src_account_ids[0]))
        else:
            domain.append(('account_id','in',src_account_ids))
        return domain

    def _get_domain_source_move_lines_fg(self):
        if not self.lab_product_id.account_id.id:
            raise ValidationError(_(f"Could not find accounts for Product {self.lab_product_id.product_id.name}"))
        domain = [('plantation_location_id','=',self.lab_product_id.location_id.id),
                ('parent_state','=','posted')]
        domain.append(('account_id','=',self.lab_product_id.account_id.id))
        return domain

    def compute_initial_and_cost_value(self):
        for closing in self:
            StockMove = self.env['stock.move']
            # Get Initial Value
            prev_closing = self.search([('lab_product_id','=',closing.lab_product_id.id),('date_to','<',closing.date_from)], order='date_to desc', limit=1)

            # Beginning WIP
            open_prod_orders = self.env['lab.production.order'].search([('lab_product_id','=',closing.lab_product_id.id),
                                                            ('date_start','<',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                            '|',
                                                                ('date_end','=',False),
                                                                ('date_end','>',closing.date_from.strftime('%Y-%m-%d 00:00:00'))])
            closing.opening_wip_qty = sum(open_prod_orders.mapped('product_qty')) if open_prod_orders else 0.0

            # domain_op_wip = closing._get_domain_source_move_lines()
            # domain_op_wip.extend([('date','<',closing.date_from)])
            # begining_moves_wip = self.env['account.move.line'].search(domain_op_wip)
            closing.opening_wip_value = prev_closing.closing_wip_value if prev_closing else 0.0
            # closing.opening_wip_value = sum(begining_moves_wip.mapped('balance')) if begining_moves_wip else 0.0
            
            # Receiving WIP
            new_prod_ordres = self.env['lab.production.order'].search([('lab_product_id','=',closing.lab_product_id.id),
                                                            ('date_start','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00'))])
            closing.incoming_wip_qty = sum(new_prod_ordres.mapped('product_qty')) if new_prod_ordres else 0.0

            domain_in_wip = closing._get_domain_source_move_lines()
            domain_in_wip.extend([('date','>=',closing.date_from),('date','<=',closing.date_to)])
            cost_addition_moves = self.env['account.move.line'].search(domain_in_wip)
            # print(">>>>>>>>>>>>>>>>>>>>> wip_cost_consumed", cost_addition_moves)
            closing.wip_cost_consumed = sum(cost_addition_moves.mapped('balance')) if cost_addition_moves else 0.0
            # print(">>>>>>>>>>>>>>>>>>>>> wip_cost_consumed", closing.wip_cost_consumed)

            # Outgoing WIP
            out_prod_ordres = self.env['lab.production.order'].search([('lab_product_id','=',closing.lab_product_id.id),
                                                            ('date_end','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                            ('date_end','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            closing.outgoing_wip_qty = sum(out_prod_ordres.mapped('product_qty')) if out_prod_ordres else 0.0

            # Opening FG
            all_in_moves = self.env['stock.move'].search([('product_id','=',closing.lab_product_id.product_id.id),
                                                          ('location_dest_id.usage','=','internal'),
                                                          ('location_id.usage','!=','internal'),
                                                          ('date','<',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                          ('state','=','done')])
            all_out_moves = self.env['stock.move'].search([('product_id','=',closing.lab_product_id.product_id.id),
                                                          ('location_id.usage','=','internal'),
                                                          ('location_dest_id.usage','!=','internal'),
                                                          ('date','<',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                          ('state','=','done')])
            closing.opening_fg_qty = (sum(all_in_moves.mapped('product_uom_qty')) if all_in_moves else 0.0) - (sum(all_out_moves.mapped('product_uom_qty')) if all_out_moves else 0.0)

            # domain_op = closing._get_domain_source_move_lines_fg()
            # domain_op.extend([('date','<',closing.date_from)])
            # begining_moves = self.env['account.move.line'].search(domain_op)
            # closing.opening_fg_value = sum(begining_moves.mapped('balance')) if begining_moves else 0.0
            closing.opening_fg_value = prev_closing.closing_fg_value

            # Receiving FG
            in_moves = self.env['stock.move'].search([('product_id','=',closing.lab_product_id.product_id.id),
                                                          ('location_dest_id.usage','=','internal'),
                                                          ('location_id.usage','!=','internal'),
                                                          ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                          ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                                          ('state','=','done')])
            closing.incoming_fg_qty = sum(in_moves.mapped('product_qty')) if in_moves else 0.0

            # Outgoing FG
            out_moves = self.env['stock.move'].search([('product_id','=',closing.lab_product_id.product_id.id),
                                                          ('location_id.usage','=','internal'),
                                                          ('location_dest_id.usage','!=','internal'),
                                                          ('picking_type_id.code','=','issue'),
                                                          ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                          ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                                          ('state','=','done')])
            closing.outgoing_stock_move_ids = [(6, 0, out_moves.ids)]
            # closing.outgoing_fg_qty = sum(out_moves.mapped('product_qty')) if out_moves else 0.0
            
            # Adjustment
            adj_in_moves = self.env['stock.move'].search([('product_id','=',closing.lab_product_id.product_id.id),
                                                          ('location_dest_id.usage','=','internal'),
                                                          ('location_id.usage','=','inventory'),
                                                          ('picking_type_id','=',False),
                                                          ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                          ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                                          ('state','=','done')])
            adj_out_moves = self.env['stock.move'].search([('product_id','=',closing.lab_product_id.product_id.id),
                                                          ('location_id.usage','=','internal'),
                                                          ('location_dest_id.usage','=','inventory'),
                                                          ('picking_type_id','=',False),
                                                          ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                                          ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                                                          ('state','=','done')])
            closing.adjustment_fg_qty = (sum(adj_in_moves.mapped('product_qty')) if adj_in_moves else 0.0) \
                            - sum(adj_out_moves.mapped('product_qty')) if adj_out_moves else 0.0
            
            closing.adjustment_fg_only_value = 0.0

    def create_account_move(self):
        lab_journal = self.env.ref('ny_closing.plantation_closing_laboratory_journal')
        for closing in self:
            if not closing.lab_product_id.account_id:
                raise ValidationError(f"Inventory Account pada Lab Product Kosong. Silahkan diisi terlebih dahulu pada Lab Product {closing.lab_product_id.product_id.name}")
            if not closing.lab_product_id.location_id.type_id.account_id:
                raise ValidationError(f"Default Counterpart Account pada Tipe Lokasi Kosong. Silahkan diisi terlebih dahulu pada Tipe Lokasi {closing.lab_product_id.location_id.type_id.code}")
            
            if closing.closing_move_id:
                if closing.closing_move_id.state in ('posted','cancel'):
                    closing.closing_move_id.button_draft()
            move_lines = []
            # print("........closing journal", closing.incoming_fg_qty)
            if closing.incoming_fg_value or closing.incoming_fg_value:
                vals_dest = {
                    'name': 'Lab Cost to Inventory',
                    'plantation_location_type_id': closing.lab_product_id.location_id.type_id.id,
                    'plantation_location_id': closing.lab_product_id.location_id.id,
                    'account_id': closing.lab_product_id.account_id.id,
                    'debit': closing.incoming_fg_value if closing.incoming_fg_value > 0 else 0.0,
                    'credit': abs(closing.incoming_fg_value) if closing.incoming_fg_value < 0 else 0.0,
                }
                move_lines.append((0,0,vals_dest))
                vals_src = vals_dest.copy()
                vals_src.update({
                    'account_id': closing.lab_product_id.location_id.type_id.account_id.id,
                    'debit': vals_dest['credit'],
                    'credit': vals_dest['debit'],
                })
                move_lines.append((0,0,vals_src))
            
            # Create Jurnal Consumption
            if closing.outgoing_stock_move_ids:
                for move in closing.outgoing_stock_move_ids:
                    account_out = False
                    # if not move.plantation_activity_id:
                    #     raise ValidationError(f"Aktifitas pada Material Request Kosong. Silahkan diisi terlebih dahulu pada MR no {move.sudo().mr_line_id.mr_id.name}")
                    # if not move.plantation_activity_id.cost_account_id:
                    #     raise ValidationError(f"Plantation Cost Account pada Aktifitas Kosong. Silahkan diisi terlebih dahulu pada Aktifitas {move.plantation_activity_id.code} {move.plantation_activity_id.name}")
                    # account_out = move.plantation_activity_id.cost_account_id
                    account_out = move.plantation_activity_id.account_id
                    if not account_out:
                        account_out = closing.lab_product_id.location_id.type_id.account_id # Sementara buat testing
                        # print(">>>>>>>>>>>>>>>> INI", closing.lab_product_id.product_id.name)
                        # print(">>>>>>>>>>>>>>>> INI", account_out.name)
                    vals_dest2 = {
                        'name': move.product_id.name,
                        'plantation_varieties_id': move.plantation_varieties_id.id,
                        'plantation_location_type_id': move.plantation_location_type_id.id,
                        'plantation_location_id': move.plantation_location_id.id,
                        'plantation_activity_id': move.plantation_activity_id.id,
                        # 'plantation_src_journal_id': False,
                        'account_id': account_out.id,
                        'debit': move.product_qty * closing.new_fg_cost_price,
                        'credit': 0.0,
                    }
                    move_lines.append((0,0,vals_dest2))
                    vals_src2 = vals_dest2.copy()
                    vals_src2.update({
                        'account_id': closing.lab_product_id.account_id.id,
                        'debit': vals_dest2['credit'],
                        'credit': vals_dest2['debit'],
                    })
                    move_lines.append((0,0,vals_src2))

            if not move_lines:
                continue
            
            move_values1 = {
                'date': closing.date_to,
                'journal_id': lab_journal.id,
                'move_type': 'entry',
                'line_ids': ([(2, x.id) for x in closing.closing_move_id.line_ids] if closing.closing_move_id else []) + move_lines,
            }
            # print("........closing journal", move_values1)
            if closing.closing_move_id:
                closing.closing_move_id.write(move_values1)
            else:
                new_move = self.env['account.move'].create(move_values1)
                closing.closing_move_id = new_move.id
            # closing.closing_move_id._post(soft=False)
            # print("........closing journal", closing.closing_move_id)
            

        return True

    def action_cancel(self):
        for closing in self:
            closing.closing_move_id.button_cancel()

    # def action_view_src_move_lines(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
    #     action['domain'] = self._get_domain_source_move_lines()
    #     return action

    # def action_view_seed_out_move_lines(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
    #     action['domain'] = [('id','in',self.closing_out_move_ids.line_ids.ids)]
    #     return action

    # def action_view_seed_move(self):
    #     # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
    #     pass

    # def action_view_seed_in_move(self):
    #     # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
    #     pass

    # def action_view_seed_out_move(self):
    #     # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
    #     pass

    # def action_view_seed_adj_move(self):
    #     # TODO : nnti kalau modul seednya udah kelar baru kita tambahin
    #     pass