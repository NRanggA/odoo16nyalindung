# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class DirectPayment(models.Model):
    _name = "account.direct.payment"
    _description = "Direct Payment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search([('type', 'in', ('bank', 'cash')), ('company_id', '=', default_company_id)], limit=1)
        return journal.id

    name = fields.Char(string="Number", default="New")
    date = fields.Date('Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Partner', copy=False, ondelete='restrict')
    # payment_request_type = fields.Selection([
    #     ('direct_inbound', 'Direct Inbound Payment'), 
    #     ('direct_outbound', 'Direct Outbound Payment')])
    description = fields.Text(string="Description")
    currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda s: s.env.company.currency_id.id,
        required=True, ondelete='restrict')
    journal_id = fields.Many2one('account.journal', string='Expense Journal', 
        check_company=True, domain="[('type', '=', ['bank','cash'])]",
        default=_default_journal_id, help="The journal used when the expense is done.")
    
    line_ids = fields.One2many("account.direct.payment.line", "payment_id", string="Lines")
    amount_total = fields.Monetary(compute='_amount_total', string='Total Amount', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('posted', 'Posted'), 
        ('done', 'Closed'), 
        ('cancel', 'Cancel')], default="draft", tracking=True)
    
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', 
        copy=False, readonly=True)    
    
    amount_residual = fields.Monetary(compute='_payment_state', string='Amount to Pay', store=True, compute_sudo=True)
    payment_state = fields.Selection([('no', 'Nothing To Pay'), 
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        # ('partial', 'Partially Paid'),
        ('paid', 'Paid')], compute='_payment_state', compute_sudo=True, 
        string='Payment Status', store=True)
    company_id = fields.Many2one("res.company", string="Company", 
        default=lambda s: s.env.company.id, tracking=True,
    )
    requested_by = fields.Many2one("res.users", string="Requested by", 
        default=lambda s: s.env.uid, tracking=True, index=True,
    )

    @api.depends('line_ids', 'line_ids.amount')
    def _amount_total(self):
        for payment in self:
            payment.write({
                    'amount_total': sum(payment.line_ids.mapped('amount')),
                })

    @api.depends(
        'amount_total',
        'account_move_id', 
        'account_move_id.line_ids',
        'account_move_id.line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'account_move_id.line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'account_move_id.line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'account_move_id.line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'account_move_id.line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'account_move_id.line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'account_move_id.line_ids.debit',
        'account_move_id.line_ids.credit',
        'account_move_id.line_ids.currency_id',
        'account_move_id.line_ids.amount_currency',
        'account_move_id.line_ids.amount_residual',
        'account_move_id.line_ids.amount_residual_currency',
        'account_move_id.line_ids.payment_id.state',
        'account_move_id.line_ids.full_reconcile_id'
        )
    def _payment_state(self):
        for payment in self:
            new_payment_state = 'no'
            currency = payment.currency_id
            amount_residual = 0.0
            if payment.account_move_id and payment.account_move_id.state=='posted':
                new_payment_state = 'not_paid'
                for line in payment.account_move_id.line_ids.filtered(lambda l : l.account_type in ('receivable', 'payable')):
                    amount_residual += line.amount_residual
                    if not line.full_reconcile_id:
                        continue
                    
                    if currency.is_zero(line.amount_residual):
                        reconciled_payments = payment.account_move_id._get_reconciled_payments()
                        if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                            new_payment_state = 'paid'
                        else:
                            new_payment_state = 'in_payment'
            
            payment.write({
                'payment_state': new_payment_state,
                'amount_residual': amount_residual,
                })

    def unlink(self):
        for payment in self:
            if not payment.state == 'cancel':
                raise UserError(_('In order to delete a Direct Payment, you must cancel it first.'))
        return super(DirectPayment, self).unlink()

    ##########################
    #      HELPER METHOD     #
    ##########################
    def _prepare_move(self):
        journal = self.journal_id
        # account_date = self.date or fields.Datetime.now()
        account_date = self.date or fields.Date.context_today.strftime(DF)
        return {
            # 'direct_payment_id' : self.id,
            'move_type' : 'entry',
            'name': '/',
            'date': account_date,
            'journal_id' : journal.id,
            'ref': self.name,
            'company_id': self.company_id.id,
        }

    def _prepare_payable_move_line(self, amount):
        partner =  self.partner_id or self.requested_by.partner_id or False
        return {
            'partner_id': partner.id if partner else False,
            'name': _("Request of Direct Payment"),
            # 'account_id': self.company_id.partner_id.property_account_payable_id.id,
            'account_id': partner.property_account_payable_id.id if partner else self.company_id.partner_id.property_account_payable_id.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            # 'product_id': self.product_id.id,
            'debit': amount if amount > 0 else 0.0,
            'credit': abs(amount) if amount < 0 else 0.0,
        }

    def _prepare_rounding_move_line(self, amount):
        partner =  self.partner_id or self.requested_by.partner_id or False
        return {
            'partner_id': partner.id if partner else False,
            'name': _("Unrealized Rounding of Direct Payment"),
            'account_id': partner.property_account_payable_id.id if partner else self.company_id.partner_id.property_account_payable_id.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            # 'product_id': self.product_id.id,
            'debit': amount if amount > 0 else 0.0,
            'credit': abs(amount) if amount < 0 else 0.0,
        }

    def direct_payment_hook(self, move_lines):
        return move_lines

    ##########################
    #     BUSINESS METHOD    #
    ##########################
    def action_create_move(self):
        AccountMove = self.env['account.move']
        move_lines = [l._prepare_move_line() for l in self.line_ids]
        move_lines = self.direct_payment_hook(move_lines)
        
        total = sum([ml['debit'] - ml['credit'] for ml in move_lines])
        if total:
            payable_move_lines = self._prepare_payable_move_line(-1*total)
            if not float_is_zero(total + payable_move_lines['debit'] - payable_move_lines['credit'], 
                            precision_digits=self.company_id.currency_id.decimal_places):
                rounding_move_lines = self._prepare_rounding_move_line(total + payable_move_lines['debit'] - payable_move_lines['credit'])
                move_lines.append(rounding_move_lines)
            move_lines.append(payable_move_lines)

        move_dict = self._prepare_move()
        move_dict.update({'line_ids': list(map(lambda l: (0,0,l), move_lines))})
        new_move = AccountMove.create(move_dict)
        self.account_move_id = new_move.id
        new_move._post()

        return True


    def action_confirm(self):
        for payment in self:
            if payment.state!='draft':
                raise ValidationError(_('You cannot Confirm payment that is not in a Draft state'))
            for line in payment.line_ids:
                if line.amount is not None and line.amount <= 0:
                    raise ValidationError(_('You cannot confirm payment if any amount in payment lines is equal to or less than 0'))
            if payment.name == 'New':
                payment.name = self.env['ir.sequence'].next_by_code('account.direct.payment')
            payment.state="confirm"

    def action_post(self):
        for payment in self:
            if payment.state!='confirm':
                raise ValidationError(_('You cannot set Post payment that is not in a Confirmed State'))
            payment.action_create_move()
            payment.state="posted"

    def action_cancel(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for payment in self:
            if payment.account_move_id:
                raise ValidationError(_('You cannot set Cancel payment that is already create a journal entry'))
            payment.state="cancel"

    def action_draft(self):
        for payment in self:
            payment.state="draft"

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.mapped('account_move_id').ids,
                'default_partner_id' : self.partner_id.id,
                'default_journal_id' : self.journal_id.id,
                'default_payment_line_ids' : [(0,0,{ 
                    'move_id' : self.account_move_id.id,
                    'origin' : self.name,
                    'invoice_date' : self.date,
                    'amount_to_pay' : self.amount_total
                })]
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        

class DirectPaymentLine(models.Model):
    _name = "account.direct.payment.line"
    _description = "Direct Payment Line"

    payment_id = fields.Many2one("account.direct.payment", string="Direct Payment", ondelete="cascade")
    currency_id = fields.Many2one("res.currency", related="payment_id.currency_id", string="Currency", store=True)
    product_id = fields.Many2one("product.product", string="Product", ondelete="restrict", domain=[('detailed_type','!=','product')])
    account_id = fields.Many2one("account.account", "Account", ondelete="restrict", required=True)
    analytic_account_id = fields.Many2one("account.analytic.account", "Analytic Account", ondelete="restrict")
    name = fields.Char(string="Description", required=True)
    amount = fields.Monetary('Amount')

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.account_id = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            self.name = self.product_id.name

    def _prepare_move_line(self):
        amount = self.currency_id.compute(self.amount, self.payment_id.company_id.currency_id)
        partner =  self.payment_id.partner_id or self.payment_id.requested_by.partner_id or False
        return {
            'partner_id': partner.id if partner else False,
            'name': self.name,
            'account_id': self.account_id.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            'product_id': self.product_id.id,
            'debit': amount if amount > 0 else 0.0,
            'credit': abs(amount) if amount < 0 else 0.0,
        }

    def unlink(self):
        for line in self:
            if line.payment_id.state!='draft':
                raise UserError(_('Cannot delete a Direct Payment line which is in state \'%s\'.') % (line.payment_id.state,))
        return super(DirectPaymentLine, self).unlink()