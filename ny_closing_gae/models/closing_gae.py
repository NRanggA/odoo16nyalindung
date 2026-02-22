from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class ClosingGae(models.Model):
    _name = 'closing.gae'
    _description = 'Closing GAE'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution')
    line_ids = fields.One2many('closing.gae.line', 'closing_gae_id', string='Closing GAE Lines')
    amount = fields.Float('Total Amount', compute='_compute_total_amount', store=True)
    closing_move_id = fields.Many2one('account.move', string='Journal Entry')

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.amount = sum(record.line_ids.mapped('amount'))

    def action_view_move_lines(self):
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('gae_distribution_id', '=', self.gae_distribution_id.id),
            ('parent_state', '=', 'posted'),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = domain
        return action

    def summarize_move_line(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_plantation':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            
            closing.line_ids.unlink()
            move_lines = self.env['account.move.line'].search([
                ('date', '>=', closing.date_from),
                ('date', '<=', closing.date_to),
                ('gae_distribution_id', '=', closing.gae_distribution_id.id),
                ('parent_state', '=', 'posted'),
            ])
            to_create = []
            for account in move_lines.mapped('account_id'):
                account_lines = move_lines.filtered(lambda l: l.account_id == account)
                total_amount = sum(account_lines.mapped('balance'))
                remaining_amount = total_amount
                last_line = len(closing.gae_distribution_id.line_ids)
                for dist_plan in closing.gae_distribution_id.line_ids:
                    if not last_line:
                        dist_amount = remaining_amount
                    else:
                        dist_amount = total_amount * dist_plan.distribution_percentage / 100
                    to_create.append((0, 0, {
                        'plantation_varieties_id': dist_plan.varieties_id.id,
                        'account_id': account.id,
                        'amount': dist_amount,
                    }))
                    last_line -= 1
                    remaining_amount -= dist_amount
            closing.line_ids = to_create
    
    def create_account_move(self):
        closing_journal = self.env.ref('ny_closing_gae.plantation_closing_gae_journal')
        for closing in self:
            move_vals = {
                'move_type': 'entry',
                'journal_id': closing_journal.id,
                'date': closing.date_to,
                # 'ref': f'Closing GAE {closing.name}',
            }
            move_lines = []
            for line in closing.line_ids:
                move_lines.append((0, 0, {
                    'name': 'Move to GAE Distribution',
                    'plantation_varieties_id': line.plantation_varieties_id.id,
                    'account_id': line.account_id.id,
                    'debit': line.amount if line.amount > 0 else 0.0,
                    'credit': -line.amount if line.amount < 0 else 0.0,
                    # 'partner_id': False,
                    # 'analytic_distribution': False,
                }))
                move_lines.append((0, 0, {
                    'name': 'Move to GAE Distribution',
                    'plantation_varieties_id': False,
                    'account_id': line.account_id.id,
                    'debit': -line.amount if line.amount < 0 else 0.0,
                    'credit': line.amount if line.amount > 0 else 0.0,
                    'gae_distribution_id': closing.gae_distribution_id.id,
                    # 'partner_id': False,
                    # 'analytic_distribution': False,
                }))
            move_vals['line_ids'] = move_lines
            move = self.env['account.move'].create(move_vals)

            closing.write({'closing_move_id': move.id})
    
    def action_cancel(self):
        for closing in self:
            if closing.closing_move_id:
                closing.closing_move_id.button_cancel()

class ClosingGaeLine(models.Model):
    _name = 'closing.gae.line'
    _description = 'Closing GAE Line'

    closing_gae_id = fields.Many2one('closing.gae', string='Closing GAE', ondelete='cascade')
    plantation_varieties_id = fields.Many2one('plant.varieties', string='Varieties', required=True)
    account_id = fields.Many2one('account.account', string='Account', required=True)
    amount = fields.Float('Total Amount')

    def action_view_move_lines(self):
        domain = [
            ('account_id', '=', self.account_id.id),
            ('date', '>=', self.closing_gae_id.date_from),
            ('date', '<=', self.closing_gae_id.date_to),
            ('gae_distribution_id', '=', self.closing_gae_id.gae_distribution_id.id),
            ('parent_state', '=', 'posted'),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = domain
        return action