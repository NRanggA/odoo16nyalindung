from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero

import logging
_logger = logging.getLogger(__name__)

class ClosingGae(models.Model):
    _name = 'closing.gae'
    _description = 'Closing GAE'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')
    parent_state = fields.Selection(related='closing_process_id.state', string='Parent State', store=True)
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
            if closing.closing_process_id and closing.parent_state!='closing_gae':
                raise ValidationError(f"Tidak dapat mengubah data Closing GAE yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            
            closing.line_ids.unlink()
            move_lines = self.env['account.move.line'].search([
                ('date', '>=', closing.date_from),
                ('date', '<=', closing.date_to),
                ('gae_distribution_id', '=', closing.gae_distribution_id.id),
                ('parent_state', '=', 'posted'),
            ])
            to_create = []
            total_amount = sum(move_lines.mapped('balance'))
            for account in move_lines.mapped('account_id'):
                account_lines = move_lines.filtered(lambda l: l.account_id == account)
                amount = sum(account_lines.mapped('balance'))
                to_create.append((0, 0, {
                    # 'plantation_varieties_id': False,
                    'account_id': account.id,
                    'amount': amount,
                }))
            closing.line_ids = to_create
            closing.amount = total_amount
    
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
            source_move_lines = self.env['account.move.line'].search([
                ('date', '>=', closing.date_from),
                ('date', '<=', closing.date_to),
                ('gae_distribution_id', '=', closing.gae_distribution_id.id),
                ('parent_state', '=', 'posted'),
            ])
            
            # for source_move in source_move_lines.move_id:
            # for source_line in source_move.line_ids.filtered(lambda l: l.gae_distribution_id.id==closing.gae_distribution_id.id):
            for source_line in source_move_lines:
                company_currency = source_line.company_id.currency_id
                current_currency = source_line.currency_id
                prec = company_currency.decimal_places
                # prec = source_line.currency_id.decimal_places
                prec = 2
                remaining_amount = source_line.balance
                last_line = len(source_line.gae_distribution_id.line_ids) - 1
                for dist_plan in source_line.gae_distribution_id.line_ids:
                    if not last_line:
                        dist_amount = remaining_amount
                    else:
                        dist_amount = round(source_line.balance * dist_plan.distribution_percentage / 100, 2)
                    if not dist_amount:
                        last_line -= 1
                        continue
                    move_line_2 = {
                        'name': 'Closing GAE from ' + source_line.move_id.name,
                        'plantation_varieties_id': dist_plan.varieties_id.id,
                        # 'account_id': category_id.account_depreciation_expense_id.id,
                        'account_id': source_line.account_id.id,
                        'debit': dist_amount if float_compare(dist_amount, 0.0, precision_digits=2) > 0 else 0.0,
                        'credit': 0.0 if float_compare(dist_amount, 0.0, precision_digits=2) > 0 else -dist_amount,
                        # 'partner_id': line.asset_id.partner_id.id,
                        # 'analytic_distribution': analytic_distribution,
                        'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                        'amount_currency': dist_amount,
                    }
                    move_lines.append((0,0, move_line_2))
                    last_line -= 1
                    remaining_amount -= dist_amount
                move_line_1 = {
                    'name': 'Closing GAE from ' + source_move.name,
                    'account_id': source_line.account_id.id,
                    'debit': 0.0 if float_compare(source_line.balance, 0.0, precision_digits=prec) > 0 else -source_line.balance,
                    'credit': source_line.balance if float_compare(source_line.balance, 0.0, precision_digits=prec) > 0 else 0.0,
                    # 'partner_id': line.asset_id.partner_id.id,
                    # 'analytic_distribution': analytic_distribution,
                    'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                    'amount_currency': - 1.0 * source_line.balance,
                }
                move_lines.append((0,0, move_line_1))
            move_vals['line_ids'] = move_lines
            if closing.closing_move_id:
                closing.closing_move_id.button_draft()
                closing.closing_move_id.write(move_vals)
                move = closing.closing_move_id
            else:
                move = self.env['account.move'].create(move_vals)

            closing.write({'closing_move_id': move.id})
            move._post(soft=False)

    def action_cancel(self):
        for closing in self:
            if closing.closing_move_id:
                closing.closing_move_id.button_cancel()

class ClosingGaeLine(models.Model):
    _name = 'closing.gae.line'
    _description = 'Closing GAE Line'

    closing_gae_id = fields.Many2one('closing.gae', string='Closing GAE', ondelete='cascade')
    # plantation_varieties_id = fields.Many2one('plant.varieties', string='Varieties', required=True)
    account_id = fields.Many2one('account.account', string='Account', required=True)
    amount = fields.Float('Total Amount')

    def action_view_move_lines(self):
        domain = [
            ('date', '>=', self.closing_gae_id.date_from),
            ('date', '<=', self.closing_gae_id.date_to),
            ('gae_distribution_id', '=', self.closing_gae_id.gae_distribution_id.id),
            ('account_id', '=', self.account_id.id),
            ('parent_state', '=', 'posted'),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = domain
        return action