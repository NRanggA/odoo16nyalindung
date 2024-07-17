# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from dateutil.relativedelta import relativedelta
from datetime import datetime

class AccountFiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"
    _order = "date_start, id"

    name = fields.Char('Fiscal Year', required=True)
    code = fields.Char('Code', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    date_start = fields.Date('Start Date', required=True)
    date_stop = fields.Date('End Date', required=True)
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')
    state = fields.Selection([('draft', 'Open'), ('done', 'Closed')], 'Status', readonly=True, copy=False,
                             default='draft')
    interval = 1

    journal_id = fields.Many2one('account.journal', string='Closing Journal', readonly=True, states={'draft': [('readonly',False)]})
    move_id = fields.Many2one('account.move', string='Closing Journal Entry', readonly=True)

    def create_period3(self):
        self.interval = 3
        return self.create_period()

    def create_period(self):
        period = self.env['account.period']
        for fy in self:
            ds = fy.date_start
            while ds < fy.date_stop:
                de = ds + relativedelta(months=self.interval, days=-1)

                if de > fy.date_stop:
                    de = fy.date_stop

                period.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                    'state': 'draft',
                })
                ds = ds + relativedelta(months=self.interval)

            period.create({
                    'name':  "%s %s" % (_('Closing Period'), ds.strftime('%Y')),
                    'code': fy.date_stop.strftime('13/%Y'),
                    'date_start': fy.date_stop,
                    'date_stop': fy.date_stop,
                    'special': True,
                    'fiscalyear_id': fy.id,
                    'state': 'draft',
                })
        return True

    def action_close(self):
        for fy in self:
            fy.create_closing_entry()
            fy.state = 'done'
        return True

    def reopen_fiscalyear(self):
        for fy in self:
            if fy.move_id:
                fy.with_context(closing=True).move_id.button_cancel()
                fy.with_context(closing=True).move_id.name = '/'
                # period.with_context(closing=True).move_id.unlink()
            fy.state = 'draft'

    def create_closing_entry(self):
        AccountPeriod = self.env['account.period']
        check_period_open = self.period_ids.filtered(lambda x: x.state=='draft')
        if check_period_open:
            raise UserError(_('Cannot Create Closing!\nPlease close all periods in this Fiscal Year.'))
        AccountMoveLine = self.env['account.move.line'].with_company(self.company_id)
        AccountMove = self.env['account.move'].with_company(self.company_id)
        if self.company_id.create_monthly_earning_accrual:
            if not self.company_id.current_year_earning_account_id:
                raise UserError(_('Cannot Create Closing!\nPlease input Current Year Earning Account in Configuration.'))
            search_domain = [('account_id','=',self.company_id.current_year_earning_account_id.id),
                    # ('journal_id.type','!=','closing'),
                    ('date', '>=', self.date_start),
                    ('date', '<=', self.date_stop)]
            if self.move_id:
                search_domain.append(('id','!=',self.move_id.id))
            profit_loss_moves = AccountMoveLine.search(search_domain)
        else:
            pl_accounts = self.env['account.account'].search([('include_initial_balance','=',False)]) #('user_type_id.include_initial_balance','=',False)
            search_domain = [('account_id','in',pl_accounts.ids),
                    # ('journal_id.type','!=','closing'),
                    ('date', '>=', self.date_start),
                    ('date', '<=', self.date_stop)]
            if self.move_id:
                search_domain.append(('id','!=',self.move_id.id))
            profit_loss_moves = AccountMoveLine.search(search_domain)
        
        #create journal closing
        if not self.journal_id:
            raise UserError(_('Cannot Close!\nPlease input Closing Journal.'))
        earning_amount = sum(profit_loss_moves.mapped('balance'))

        earning_account = self.company_id.earning_account_id
        if not earning_account:
            raise UserError(_('Earning Account not Found in this Company!\nPlease Input Earning Account in Configuration.'))

        if self.company_id.create_monthly_earning_accrual:
            if not self.company_id.current_year_earning_account_id:
                raise UserError(_('Counter-part Earning Account not Found in this Company!\nPlease Input Counter-part Earning Account in Configuration.'))
            counterpart_earning_account = self.company_id.current_year_earning_account_id
        else:
            if not self.company_id.counterpart_earning_account_id:
                raise UserError(_('Counter-part Earning Account not Found in this Company!\nPlease Input Counter-part Earning Account in Configuration.'))
            counterpart_earning_account = self.company_id.counterpart_earning_account_id

        closing_period = self.period_ids.filtered(lambda x: x.special)
        if not closing_period:
            raise UserError(_('Could not find closing period in your fiscal year. Please inform Administrator'))

        move_line_dict = {
            'date': self.date_stop,
            'journal_id': self.journal_id.id,
            'name': 'Retained Earning of Year %s'%self.code,
            'account_id': earning_account.id,
            'debit': earning_amount if earning_amount>0 else 0.0,
            'credit': -earning_amount if earning_amount<0 else 0.0,
        }
        ct_move_line_dict = {
            'date': self.date_stop,
            'journal_id': self.journal_id.id,
            'name': 'Closing of Fiscal Year %s'%self.code,
            'account_id': counterpart_earning_account.id,
            'debit': -earning_amount if earning_amount<0 else 0.0,
            'credit': earning_amount if earning_amount>0 else 0.0,
        }
        
        if not self.move_id:
            move_lines = [(0,0,move_line_dict),(0,0,ct_move_line_dict)]
            
            closing_move = AccountMove.with_context(closing=True).create({
                'date': self.date_stop,
                'name': '/',
                'journal_id': self.journal_id.id,
                'state': 'draft',
                'period_id': closing_period.id,
                'line_ids': move_lines,
            })
            
            self.move_id = closing_move.id
        else:
            line_to_add = []
            line1 = self.move_id.line_ids.filtered(lambda l1: l1.account_id.id==move_line_dict['account_id'])
            if line1:
                line1.write({'debit': move_line_dict['debit'], 'credit': move_line_dict['credit']})
            else:
                line_to_add.append((0,0,move_line_dict))

            line2 = self.move_id.line_ids.filtered(lambda l2: l2.account_id.id==ct_move_line_dict['account_id'])
            if line2:
                line2.write({'debit': ct_move_line_dict['debit'], 'credit': ct_move_line_dict['credit']})
            else:
                line_to_add.append((0,0,ct_move_line_dict))


            if line_to_add:
                self.move_id.with_context(closing=True).line_ids = line_to_add

            closing_move = self.move_id
        closing_move.with_context(closing=True)._post(soft=False)
        return True