# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PaymentCreditBalance(models.Model):
    _name = 'account.payment.credit'
    _description = 'Payment Credit Balance'

    account_payment_id = fields.Many2one('account.payment', string='Payment', ondelete='cascade')
    move_line_id = fields.Many2one('account.move.line', string='Move Line', ondelete='restrict')
    move_id = fields.Many2one('account.move', related='move_line_id.move_id', store=True, readonly=True)
    date = fields.Date('Date', related='move_id.date', store=True, readonly=True)
    amount_residual = fields.Float('Amount Residual', readonly=True)
    amount_to_allocate = fields.Float('Allocate Amount')

    def _prepare_move_line_vals(self):
        """ Prepare move line values for the credit balance allocation. """
        self.ensure_one()
        if not self.amount_to_allocate:
            return 0.0, {}
        
        if not self.move_line_id.amount_residual:
            raise ValidationError("Its seem the Credit Balance is already Reconciled.")

        if -self.amount_to_allocate < self.move_line_id.amount_residual:
            raise ValidationError("Cannot allocate more than the residual amount.")
        # Prepare the values for the move line
        if not self.move_line_id:
            raise ValidationError("Move line must be set before preparing move line values.")
        
        payment = self.account_payment_id
        amount_credit_balance_to_allocate = self.amount_to_allocate
        amount = payment.currency_id._convert(amount_credit_balance_to_allocate, 
                            payment.move_id.company_currency_id, payment.company_id, payment.date)
        amount_currency = amount_credit_balance_to_allocate
    
        vals = {
            'name': self.move_line_id.name,
            'account_id': self.move_line_id.account_id.id,
            'debit': amount,
            'credit': 0.0,
            'partner_id': self.move_line_id.partner_id.id,
            'amount_currency': amount_currency,
        }
        return amount, vals