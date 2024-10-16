from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ClosingProject(models.Model):
    _name = 'closing.project' 
    _description = 'Closing Project Procedure'

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    # domain="[('state','=', ['in_progress','done'])]"
    project_id = fields.Many2one('lhm.project', string='Project', ondelete='restrict', required=True)
    closing_account_id = fields.Many2one('account.account', string='Closing Account')
    dest_account_id = fields.Many2one('account.account', compute='_compute_dest_account', readonly=False, string='Dest. Account')
    total_cost = fields.Float()

    closing_move_id = fields.Many2one('account.move', string='Journal Entry')

    @api.depends('project_id')
    def _compute_dest_account(self):
        for closing in self:
            closing.dest_account_id = closing.project_id.categ_id.account_id.id

    def _get_domain_source_move_lines(self):
        src_account_ids = self.project_id.location_id.type_id.activity_ids.account_id.ids
        if not src_account_ids:
            raise ValidationError(_(f"Could not find accounts for all related activity inside Location Type {self.project_id.location_id.type_id.code}"))
        domain = [('plantation_location_id','=',self.project_id.location_id.id),
                ('parent_state','=','posted'),('date','>=',self.date_from),('date','<=',self.date_to)]
        if len(src_account_ids)==1:
            domain.append(('account_id','=',src_account_ids[0]))
        else:
            domain.append(('account_id','in',src_account_ids))
        return domain

    def summarize_move_line(self):
        for closing in self:
            source_moves = self.env['account.move.line'].search(self._get_domain_source_move_lines())
            closing.total_cost = sum(source_moves.mapped('balance')) if source_moves else 0.0

    def create_account_move(self):
        for closing in self:
            move_lines = []
            vals = {
                'name': 'Distribute Cost from Project Closing',
                'plantation_location_type_id': closing.project_id.location_type_id.id,
                'plantation_location_id': closing.project_id.location_id.id,
                # 'plantation_activity_id': False,
                'account_id': closing.dest_account_id.id,
                'debit': closing.total_cost if closing.total_cost > 0 else 0.0,
                'credit': abs(closing.total_cost) if closing.total_cost < 0 else 0.0,
            }
            move_lines.append((0,0,vals))
            vals = {
                'name': 'Distribute Cost from Running Machine',
                'plantation_location_type_id': closing.project_id.location_type_id.id,
                'plantation_location_id': closing.project_id.location_id.id,
                # 'plantation_activity_id': False,
                'account_id': closing.closing_account_id.id,
                'debit': abs(closing.total_cost) if closing.total_cost < 0 else 0.0,
                'credit': closing.total_cost if closing.total_cost > 0 else 0.0,
            }
            move_lines.append((0,0,vals))
            values = {
                'date': closing.date_to,
                'journal_id': self.env['account.journal'].search([('type','=','general')], limit=1).id,
                'move_type': 'entry',
                'line_ids': move_lines,
            }
            new_move = self.env['account.move'].create(values)
            
            closing.closing_move_id = new_move.id
        
        return True

    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_source_move_lines()
        return action
