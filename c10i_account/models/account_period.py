# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date

class AccountPeriod(models.Model):
    _name = 'account.period'

    name = fields.Char('Period Name', required=True)
    code = fields.Char('Code')
    special = fields.Boolean('Opening/Closing Period', help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True, states={'done': [('readonly', True)]})
    date_stop = fields.Date('End of Period', required=True, states={'done': [('readonly', True)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True,
                                    states={'done': [('readonly', True)]}, index=True)
    state = fields.Selection([('draft', 'Open'), ('done', 'Closed')], 'Status', readonly=True, copy=False,
                             default='draft',
                             help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    company_id = fields.Many2one('res.company', related='fiscalyear_id.company_id', string='Company', store=True,
                                 readonly=True)
    move_ids = fields.One2many('account.move', 'period_id', string='Journal Entries')
    journal_entries_count = fields.Integer(string='# Journal Entry', compute='_compute_stat_button')

    create_monthly_earning_accrual = fields.Boolean(related='company_id.create_monthly_earning_accrual', string="Create Current Year Earning", store=True)
    earning_account_id = fields.Many2one('account.account', related='company_id.current_year_earning_account_id', string='Current Year Earning Account', store=True, readonly=True, states={'draft': [('readonly',False)]})
    counterpart_earning_account_id = fields.Many2one('account.account', related='company_id.counterpart_earning_account_id', string='Counter-part Earning Account', store=True, readonly=True, states={'draft': [('readonly',False)]})
    move_id = fields.Many2one('account.move', string='Current Year Eearning', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True, states={'draft': [('readonly',False)]})

    @api.depends('move_ids')
    def _compute_stat_button(self):
        for period in self:
            period.journal_entries_count = len(period.move_ids.ids) if period.move_ids else 0

    def close_period(self):
        AccountMove = self.env['account.move']
        for period in self:
            search_domain = [('state','=','draft'),('period_id','=',period.id)]
            if period.move_id:
                search_domain.append(('id','!=',period.move_id.id))
            unposted_moves = AccountMove.search(search_domain)
            if unposted_moves:
                raise UserError(_('Closing Period Failed!\nIn order to close a period, you must Post Journal Entries in this period.'))
            if period.company_id.create_monthly_earning_accrual:
                period.current_year_profit()
            period.state = 'done'

    def reopen_period(self):
        for period in self:
            if period.fiscalyear_id.state=='done':
                raise UserError(_('ReOpen Period Failed!\nYou cannot re-open Period in Closed Fiscal Year'))
            if period.move_id:
                period.with_context(closing=True).move_id.button_cancel()
                period.with_context(closing=True).move_id.name = '/'
                # period.with_context(closing=True).move_id.unlink()
            period.state = 'draft'

    def periodical_post_entries(self):
        AccountMove = self.env['account.move']
        # for period in self:
        #     unposted_moves = AccountMove.search(
        #         [('state', '=', 'draft'), ('period_id','=',period.id)])
        #     if unposted_moves:
        #         unposted_moves.action_post()
        search_domain = [('state', '=', 'draft')]
        if len(self.ids)>1:
            search_domain.append(('period_id','in',self.ids))
        else:
            search_domain.append(('period_id','=',self.id))
        closing_moves = self.mapped('move_id')
        if closing_moves:
            if len(closing_moves.ids)>1:
                search_domain.append(('id','not in',closing_moves.ids))
            else:
                search_domain.append(('id','!=',self.id))
        unposted_moves = AccountMove.search(search_domain)

        action = {
            'name': _("Journal Entries"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(unposted_moves) == 1:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', '=', unposted_moves.id)],
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', unposted_moves.ids)],
            })
        return action

    def button_open_entries(self):
        ''' Redirect the user to the invoice(s) paid by this payment.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name': _("Journal Entries"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(self.move_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.move_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.move_ids.ids)],
            })
        return action

    def current_year_profit(self):
        self.ensure_one()
        AccountMove = self.env['account.move']
        AccountMoveLine = self.env['account.move.line']
        pl_accounts = self.env['account.account'].search([('include_initial_balance','=',False)])
        domain = [('account_id','in',pl_accounts.ids),
                ('parent_state', '=', 'posted'),
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_stop),
                ('company_id','=',self.company_id.id)]
        if self.special:
            domain.append(('journal_id.type','=','closing'))
        else:
            domain.append(('journal_id.type','!=','closing'))
                
        profit_loss_moves = AccountMoveLine.search(domain)
        if not self.journal_id:
            raise UserError(_('Cannot Create Entry!\nPlease input the Journal.'))
        pl_amount = sum(profit_loss_moves.mapped('balance'))
        
        earning_account = self.earning_account_id
        if not earning_account:
            raise UserError(_('Earning Account not Found in this Company!\nPlease Input Earning Account in Configuration.'))
        counterpart_earning_account = self.counterpart_earning_account_id
        if not counterpart_earning_account:
            raise UserError(_('Counter-part Earning Account not Found in this Company!\nPlease Input Counter-part Earning Account in Configuration.'))

        move_line_dict = {
            'date': self.date_stop,
            'journal_id': self.journal_id.id,
            'name': 'Current Year Earning period %s'%self.code,
            'account_id': earning_account.id,
            'debit': pl_amount if pl_amount>0 else 0.0,
            'credit': -pl_amount if pl_amount<0 else 0.0,
        }
        
        ct_move_line_dict = {
            'date': self.date_stop,
            'journal_id': self.journal_id.id,
            'name': 'Closing period %s'%self.code,
            'account_id': counterpart_earning_account.id,
            'debit': -pl_amount if pl_amount<0 else 0.0,
            'credit': pl_amount if pl_amount>0 else 0.0,
        }
        
        if not self.move_id:
            move_lines = [(0,0,move_line_dict), (0,0,ct_move_line_dict)]
            closing_move = AccountMove.with_context(closing=True).create({
                'date': self.date_stop,
                'name': '/',
                'journal_id': self.journal_id.id,
                'period_id': self.id,
                'state': 'draft',
                'closing_period': True,
                'line_ids': move_lines,
            })

            self.move_id = closing_move.id
        else:
            line_to_add = []
            self.move_id.line_ids.unlink()
            line_to_add.append((0,0,move_line_dict))
            line_to_add.append((0,0,ct_move_line_dict))

            if line_to_add:
                self.move_id.with_context(closing=True).line_ids = line_to_add

            closing_move = self.move_id
        closing_move.with_context(closing=True)._post(soft=False)

    @api.model
    def _cron_close_past_periods(self):
        today = date.today()
        periods = self.search([
            ('date_stop', '<', today),
            ('state', '=', 'draft')
        ])
        for period in periods:
            period.write({'state': 'done'})