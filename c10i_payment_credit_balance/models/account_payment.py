# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Payment(models.Model):
    _inherit = 'account.payment'

    credit_balance_ids = fields.One2many(
        'account.payment.credit',
        'account_payment_id', 
        string='Credit Balances',
        help='Credit balances that can be allocated to this payment.'
    )

    def get_bills(self):
        super(Payment, self).get_bills()

        if self.env.company.account_credit_balance_id:
            for rec in self.filtered(lambda x: x.state=='draft' and x.payment_type=='inbound'):
                existing = rec.credit_balance_ids.mapped('move_line_id')
                to_remove = []
                if rec.credit_balance_ids:
                    to_remove_line = rec.credit_balance_ids.filtered(lambda x: x.move_line_id.partner_id!=rec.partner_id or x.move_line_id.reconciled)
                    if to_remove_line:
                        to_remove = list(map(lambda x: (2, x.id), to_remove_line))
                domain = [
                    ('partner_id', '=', rec.partner_id.id),
                    ('parent_state', '=', 'posted'),
                    ('reconciled', '=', False),
                    ('account_id', '=', rec.company_id.account_credit_balance_id.id)
                ]
                credit_balances = self.env['account.move.line'].search(domain)
                to_add = []
                to_update = []
                for aml in credit_balances:
                    if aml in existing:
                        existing_aml = rec.credit_balance_ids.filtered(lambda x: x.move_line_id.id == aml.id)
                        if existing_aml and existing_aml.amount_residual != aml.amount_residual:
                            to_update.append((1, existing_aml.id, {
                                'amount_residual': -1*aml.amount_residual
                            }))
                    else:
                        to_add.append((0, 0, {
                            'account_payment_id': rec.id,
                            'move_line_id': aml.id,
                            'amount_residual': -1*aml.amount_residual
                        }))
                rec.credit_balance_ids = to_remove + to_update + to_add

    @api.onchange('payment_line_ids', 'credit_balance_ids')
    def _onchange_amount(self):
        for rec in self:
            amount = 0
            if rec.payment_line_ids:
                amount = sum([line.amount_to_pay for line in rec.payment_line_ids])
            if rec.credit_balance_ids:
                amount += sum([line2.amount_to_allocate for line2 in rec.credit_balance_ids])
            rec.amount = amount
    
    def _prepare_move_vals_from_payment_lines(self):
        """ Prepare move values from payment lines, including write-off lines if applicable.
        This method extends the base functionality to include credit balance amounts and accounts.
        """
        if self.payment_type != 'inbound':
            return super(Payment, self)._prepare_move_vals_from_payment_lines()

        amount_total, payment_lines = super(Payment, self)._prepare_move_vals_from_payment_lines()
        for cline in self.credit_balance_ids.filtered(lambda x: x.amount_to_allocate):
            amount, line_vals = cline._prepare_move_line_vals()
            amount_total -= amount
            payment_lines.append(line_vals)
        
        return amount_total, payment_lines
    
    def reconcile_payment_lines(self):
        super(Payment, self).reconcile_payment_lines()

        # Reconcile credit balance lines if applicable
        if self.payment_type == 'inbound':
            for credit_entry, credit_balance_allocated in zip(
                self.credit_balance_ids.move_line_id, 
                self.move_id.line_ids.filtered(lambda x: x.account_id.id==self.env.company.account_credit_balance_id.id)
            ):
                (credit_entry + credit_balance_allocated).reconcile()