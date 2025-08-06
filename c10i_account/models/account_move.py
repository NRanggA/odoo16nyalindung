# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import re

class AccountMove(models.Model):
    _inherit = 'account.move'

    period_id               = fields.Many2one('account.period', string='Period', compute="_get_account_period", store=True)
    closing_period          = fields.Boolean(string="Closing Period", default=False)
    closing_period_journal  = fields.Boolean(string="Closing Period Journal", default=False)

    # Menambahkan default tanggal hari ini
    invoice_date            = fields.Date(string='Invoice/Bill Date', readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False, default=fields.Date.today)

    is_payment = fields.Boolean('Is Payment', default=False)

    # invoice_advance_allocate_ids = fields.One2many('account.invoice.advance.allocated', 'move_id', string='Advance Allocated')
    # invoice_advance_allocate_ids = fields.One2many('account.move.line', 'move_id', string='Advance Allocated',
    #     copy=False, readonly=True,
    #     domain=[('exclude_from_advance_tab', '=', False)],
    #     states={'draft': [('readonly', False)]})
    # add_advance_to_move_line = fields.Boolean(string='Add advance to line', compute='_compute_flag_add_advance', store=True)

    # inherit fungsi sequence
    # def _get_last_sequence_domain(self, relaxed=False):
    #     where_string, param = super(AccountMove, self)._get_last_sequence_domain(relaxed)

    #     is_payment = self.payment_id or self._context.get('is_payment') or self.is_payment

    #     if self.journal_id.payment_sequence:
    #         if is_payment:
    #             where_string += " AND (is_payment = 'true' OR payment_id IS NOT NULL)"
    #         else:
    #             where_string += " AND (payment_id IS NULL AND is_payment = 'false')"
        
    #     return where_string, param

    def _get_last_sequence_domain(self, relaxed=False):
        # EXTENDS account sequence.mixin
        self.ensure_one()
        if not self.date or not self.journal_id:
            return "WHERE FALSE", {}
        where_string = "WHERE journal_id = %(journal_id)s AND name != '/'"
        param = {'journal_id': self.journal_id.id}
        # is_payment = self.payment_id or self._context.get('is_payment')
        is_payment = self.payment_id or self._context.get('is_payment') or self.is_payment

        # print(f"===== is_payment: {is_payment}")
        # print(f"===== self: {self.is_payment}")

        if not relaxed:
            domain = [('journal_id', '=', self.journal_id.id), ('id', '!=', self.id or self._origin.id), ('name', 'not in', ('/', '', False))]
            if self.journal_id.refund_sequence:
                refund_types = ('out_refund', 'in_refund')
                domain += [('move_type', 'in' if self.move_type in refund_types else 'not in', refund_types)]
            if self.journal_id.payment_sequence:
                domain += [('payment_id', '!=' if is_payment else '=', False)]
            reference_move_name = self.search(domain + [('date', '<=', self.date)], order='date desc', limit=1).name
            if not reference_move_name:
                reference_move_name = self.search(domain, order='date asc', limit=1).name
            sequence_number_reset = self._deduce_sequence_number_reset(reference_move_name)
            date_start, date_end = self._get_sequence_date_range(sequence_number_reset)
            where_string += """ AND date BETWEEN %(date_start)s AND %(date_end)s"""
            param['date_start'] = date_start
            param['date_end'] = date_end
            if sequence_number_reset in ('year', 'year_range'):
                param['anti_regex'] = re.sub(r"\?P<\w+>", "?:", self._sequence_monthly_regex.split('(?P<seq>')[0]) + '$'
            elif sequence_number_reset == 'never':
                param['anti_regex'] = re.sub(r"\?P<\w+>", "?:", self._sequence_yearly_regex.split('(?P<seq>')[0]) + '$'

            if param.get('anti_regex') and not self.journal_id.sequence_override_regex:
                where_string += " AND sequence_prefix !~ %(anti_regex)s "

        if self.journal_id.refund_sequence:
            if self.move_type in ('out_refund', 'in_refund'):
                where_string += " AND move_type IN ('out_refund', 'in_refund') "
            else:
                where_string += " AND move_type NOT IN ('out_refund', 'in_refund') "
        elif self.journal_id.payment_sequence:
            if is_payment:
                # where_string += " AND payment_id IS NOT NULL "
                where_string += " AND (is_payment = 'true' OR payment_id is NOT NULL) "
            else:
                # where_string += " AND payment_id IS NULL "
                where_string += " AND (payment_id IS NULL AND is_payment = 'false') "

        # print(f"==== string: {where_string%param}")

        return where_string, param


    ########################################
    #           HELPER METHOD              #
    ########################################
    @api.depends('date', 'closing_period', 'closing_period_journal')
    def _get_account_period(self):
        for move in self:
            if move.closing_period_journal:
                period = self.env['account.period'].search([('date_start','<=',move.date),('date_stop','>=',move.date),('special','=',True)], limit=1)
                move.period_id=period.id
            else:
                period = self.env['account.period'].search([('date_start','<=',move.date),('date_stop','>=',move.date),('special','=',False)], limit=1)
                if period.state!='done':
                    move.period_id=period.id
                else:
                    if move.closing_period:
                        move.period_id=period.id
                    else:
                        raise UserError(_("You cannot create a transaction in a Closed Period."))

    # @api.depends(
    #     'invoice_advance_allocate_ids',
    #     'invoice_advance_allocate_ids.update_to_line'
    #     )
    # def _compute_flag_add_advance(self):
    #     for move in self:
    #         if move.invoice_advance_allocate_ids:
    #             # move.add_advance_to_move_line = any(al.update_to_line for al in move.invoice_advance_allocate_ids)
    #             move.add_advance_to_move_line = False

    # def _prepare_advance_move_line_vals(self, advance_line):
    #     balance = self.currency_id._convert(advance_line.amount, self.company_id.currency_id, self.company_id, self.date)
    #     amount_currency = advance_line.amount
    #     res = {
    #         'exclude_from_invoice_tab': True,
    #         'source_advance_id': advance_line.advance_id.id,

    #         'name': _('Advance Allocation %s', advance_line.advance_id.name),
    #         'account_id': advance_line.advance_id.advance_account_id.id,
    #         # 'tax_repartition_line_id': biggest_tax_line.tax_repartition_line_id.id,
    #         # 'tax_exigible': biggest_tax_line.tax_exigible,
    #         # 'exclude_from_invoice_tab': True,

    #         'debit': balance > 0.0 and balance or 0.0,
    #         'credit': balance < 0.0 and -balance or 0.0,
    #         'quantity': 1.0,
    #         'amount_currency': amount_currency,
    #         'partner_id': self.partner_id.id,
    #         'move_id': self.id,
    #         'currency_id': self.currency_id.id,
    #         'company_id': self.company_id.id,
    #         'company_currency_id': self.company_id.currency_id.id,
    #         # 'sequence': 9999,
    #     }
    #     return res

    ###########################################
    #           LOW-LEVEL METHOD              #
    ###########################################
    # @api.model_create_multi
    # def create(self, vals_list):
    #     # PERIOD VALIDATION
    #     for vals in vals_list:
    #         if 'date' in vals:
    #             if 'period_id' not in vals:
    #                 period_id = self._get_account_period(vals['date'])
    #                 vals.update({'period_id': period_id})
    #     res = super().create(vals_list)
    #     return res

    def write(self, vals):
        for move in self:
            if 'state' in vals and move.period_id and move.period_id.state=='done' and not self._context.get('closing', False):
                raise UserError(_("You cannot modify a transaction in a Closed Period."))
            # if (move.period_id and move.period_id.special) and 'date' in vals and move.date != vals['date']:
            #     period_id = self.with_context(self._context)._get_account_period(vals['date'])
            #     vals.update({'period_id': period_id})

            # handling account.invoice.advance
            # print("...............",move.invoice_advance_allocate_ids)
            # if move.invoice_advance_allocate_ids:
            #     # print("aaaaaaaaastop", asd)
            #     move.do_add_advance_to_move_line()
            # print("aaaaaaaaastop", asd)
        res = super(AccountMove, self).write(vals)
        return res

    ##########################################
    #           BUSINESS METHOD              #
    ##########################################
    def action_post(self, soft=True):
        res = super(AccountMove, self).action_post()
        # for move in self.filtered(lambda m: not m.period_id):
        #     period_id = move._get_account_period(move.date)
        #     move.period_id = period_id

        # handling account.invoice.advance
        for move in self:
            # if move.invoice_advance_allocate_ids:
            #     move.do_add_advance_to_move_line(delete_unallocated_line=True)
            for adv_moveline in move.line_ids.filtered(lambda line: line.source_advance_id):
                to_reconcile = adv_moveline
                to_recompute |= adv_moveline.source_advance_id.move_id.line_ids.filtered(lambda al: al.account_id==adv_moveline.account_id)
                to_recompute.reconcile()
        return res

    # def get_outstanding_advance(self):
    #     if self.move_type not in ('in_invoice', 'out_invoice'):
    #         raise UserError(_("This function is only work for Customer Invoice or Vendor Bill"))
    #     if self.state!='draft':
    #         raise UserError(_("This function is only work in Draft State"))

    #     current_advances = self.env['account.invoice.advance']
    #     for l in self.invoice_advance_allocate_ids:
    #         if l.advance_id.partner_id.id!=self.partner_id.id or l.advance_id.advance_state in ('closed','draft'):
    #             l.unlink()
    #         current_advances |= l.advance_id

    #     advance_type = 'in_advance' if self.move_type=='in_invoice' else 'out_advance'
    #     advances = self.env['account.invoice.advance'].search([
    #         ('partner_id','=',self.partner_id.id),\
    #         ('advance_type','=',advance_type),
    #         ('advance_state','in',('open','partial')),
    #         ])
    #     print(">>>>>>>>>>>>>>>>>>>>>>", advances)
    #     to_write = []
    #     for adv in advances:
    #         if current_advances and adv.id in current_advances.ids:
    #             continue
    #         if self.currency_id.id!=adv.currency_id.id:
    #             residual = adv.currency_id._convert(aml.advance_residual_amount, self.currency_id, self.company_id, self.date)
    #         else:
    #             residual = adv.advance_residual_amount
    #         vals = {
    #             'exclude_from_invoice_tab': True,
    #             # 'invoice_line_type': line_type,
    #             # 'advance_id': adv.id,
    #             'source_advance_id': adv.id,
    #             # 'name': adv.name,
    #             'quantity': 1.0,
    #             'account_id': adv.advance_account_id.id,
    #             'name': 'Allocted advance %s'%adv.name,
    #             'currency_id': self.currency_id.id,
    #             'advance_residual_amount': residual if residual>0 else -residual,
    #             # 'amount': residual if residual>0 else -residual,
    #         }
    #         print(">>>>>>>>>>>>>>>>>>>>>>", vals)
    #         # to_write.append((0, 0, vals))
    #     # if to_write:
    #         # self.invoice_advance_allocate_ids = to_write
    #     return True

    # def do_add_advance_to_move_line(self, delete_unallocated_line=False):
    #     self.ensure_one()
    #     to_write = []
    #     to_recompute = False
    #     for al in self.invoice_advance_allocate_ids:
    #         # handle unallocated amount
    #         print("111111111111", al.amount, al.allocated)
    #         if (not al.amount or al.amount<=0.0):
    #             # handle previously allocated amount
    #             if al.allocated:
    #                 line_to_del = self.line_ids.filtered(lambda x: x.source_advance_id==al.advance_id)
    #                 line_to_del.unlink()
    #                 to_recompute = True

    #             # remove from invoice_advance_allocate_ids
    #             if delete_unallocated_line:
    #                 al.unlink()
    #         else:
    #             # handle previously allocated amount by update its account.move.line record
    #             # or do add a new record to line_ids (account.move.line)
    #             if al.allocated:
    #                 line_to_update = self.line_ids.filtered(lambda x: x.source_advance_id==al.advance_id)
    #                 print("444444444444", line_to_update)
    #                 if line_to_update:
    #                     advance_line_vals = self._prepare_advance_move_line_vals(al)
    #                     # to_write.append((line_to_update.id, advance_line_vals))
    #                 else:
    #                     advance_line_vals = self._prepare_advance_move_line_vals(al)
    #                     # to_write.append((0, 0, advance_line_vals))
    #                 print("5555555555551", advance_line_vals)
    #                 self.env['account.move.line'].create(advance_line_vals)
    #             else:
    #                 advance_line_vals = self._prepare_advance_move_line_vals(al)
    #                 print("55555555555552", advance_line_vals)
    #                 self.env['account.move.line'].create(advance_line_vals)
    #                 # to_write.append((0, 0, advance_line_vals))
    #             # al.update_to_line = False
    #             to_recompute = True
    #     # trigger function _compute_flag_add_advance
    #     # self.invoice_advance_allocate_ids = []
        
    #     # update line_ids
    #     # print(">>>>>>>>>>>>>>>>>>>>>>>>>>", to_write)
    #     # print("aaaaaaaaastop", asd)
    #     # if to_write:
    #     #     self.line_ids = to_write

    #     # # recompute all amount
    #     # if to_recompute:
    #     #     self._recompute_dynamic_lines()
    #     return True

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    period_id = fields.Many2one('account.period', related='move_id.period_id', string='Period', store=True)
    source_advance_id = fields.Many2one('account.invoice.advance', string='Source Advance')
    dest_recon_move_line_id = fields.Many2one('account.move.line', 'Dest. Move Line to Reconcile')
    advance_residual_amount = fields.Monetary(string='Advance Residual Amount', currency_field='currency_id')
    # exclude_from_advance_tab = fields.Boolean(help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")

    def _check_constrains_account_id_journal_id(self):
        super()._check_constrains_account_id_journal_id()

        for line in self.filtered(lambda x: x.display_type not in ('line_section', 'line_note')):
            journal = line.move_id.journal_id
            account = line.account_id
            if account in journal.account_disallowed_ids:
                raise UserError(_("You cannot use this account (%s) in this journal, because it is marked as disallowed.", account.display_name))

class AccountInvoiceAdvanceAllocated(models.Model):
    _name = 'account.invoice.advance.allocated'
    _description = 'Advance Outstanding Allocated'

    move_id = fields.Many2one('account.move', string='Allocated Invoice Move', readonly=True)
    advance_id = fields.Many2one('account.invoice.advance', string='Advance Source Document')
    # advance_move_line_id = fields.Many2one('account.move.line', compute='_get_advance_move_line', string='Advance Move Line')
    currency_id = fields.Many2one('res.currency', related='move_id.currency_id', string='Currency', store=True)
    residual_amount = fields.Monetary(string='Residual Amount', currency_field='currency_id')
    amount = fields.Monetary(string='Set-off Amount', currency_field='currency_id')
    update_to_line = fields.Boolean(string='Update to Line', default=True)
    allocated = fields.Boolean(string='Allocated')

    @api.onchange('amount')
    def onchange_amount(self):
        if self.amount:
            self.update_to_line = True