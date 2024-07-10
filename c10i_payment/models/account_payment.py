from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_line_ids = fields.One2many('account.payment.line', 'account_payment_id', string='Payment Line')

    @api.onchange('payment_line_ids')
    def _onchange_amount(self):
        for rec in self:
            amount = 0
            if rec.payment_line_ids:
                amount = sum([line.amount_to_pay for line in rec.payment_line_ids])
                rec.amount = amount

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.payment_line_ids = [(5, 0, 0)]        

    def get_bills(self):
        for rec in self:
            if rec.partner_id:
                existing = rec.payment_line_ids.mapped('move_id')
                moves = self.env['account.move'].search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('payment_state', 'in', ['not_paid', 'in_payment', 'partial']),
                    ('move_type', '=', 'in_invoice')
                ])
                for move in moves:
                    if move not in existing:
                        rec.payment_line_ids = [(0, 0, {
                            'account_payment_id': rec.id,
                            'move_id': move.id,
                            'amount_residual': move.amount_residual,
                            'origin': move.name
                        })]                
                rec.payment_line_ids = rec.payment_line_ids.filtered(lambda line: line.move_id.partner_id == rec.partner_id)
            else:
                raise ValidationError("Partner atau Vendor harus diisi")
            
    def action_post(self):
        ''' draft -> posted '''
        if self.payment_type != 'outbound':
            super().action_post()
        else:
            payment_lines = list(map(lambda x:(3,x.id), self.move_id.line_ids))
            debit_tot = credit_tot = 0
            amount_total = 0.0
            payment_amount = 0
            
            for pline in self.payment_line_ids:
                if pline.amount_to_pay > 0:
                    debit = credit = 0
                    amount = self.currency_id._convert(pline.amount_to_pay, self.move_id.company_currency_id, self.company_id, self.date)
                    debit = amount
                    amount_currency = pline.amount_to_pay

                    bill_line = pline.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
                    
                    line_vals = {
                        'account_id': bill_line.account_id.id,
                        'debit': debit,
                        'credit': credit,
                        'amount_currency': amount_currency,
                        'partner_id': self.partner_id.id,
                    }

                    amount_total += amount
                    payment_lines.append((0, 0, line_vals))
 
                    if pline.write_off_amount != 0 and pline.write_off_account_id:
                        write_off_amount = self.currency_id._convert(pline.write_off_amount, self.move_id.company_currency_id, self.company_id, self.date)
                        if write_off_amount > 0:
                            wo_debit = write_off_amount
                        else:
                            wo_kredit = abs(write_off_amount)
                        
                        write_off_vals = {
                            'account_id': pline.write_off_account_id,
                            'debit': wo_debit,
                            'credit': wo_kredit,
                            'amount_currency': amount_currency,
                            'partner_id': self.partner_id.id,
                        }
                    
                        amount_total += write_off_amount
                        payment_lines.append((0, 0, write_off_vals))

                else:
                    pline.unlink()

            if amount_total > 0:
                credit_tot = amount_total
            else:
                debit_tot = abs(amount_total)
                
            bank_line_vals = {
                'account_id': self.journal_id.default_account_id.id,
                'debit': debit_tot,
                'credit': credit_tot,
                'partner_id': self.partner_id.id,
            }
            payment_lines.append((0, 0, bank_line_vals))

            self.move_id.write({'line_ids': payment_lines})

            self.move_id._post(soft=False)

            for bill, payment_move_line in zip(self.payment_line_ids.move_id, self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')):
                bill_line_dua = bill.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
                (bill_line_dua + payment_move_line).reconcile()
    
    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if len(liquidity_lines) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one outstanding payments/receipts account.",
                        move.display_name,
                    ))

                # if len(counterpart_lines) != 1:
                #     raise UserError(_(
                #         "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #         "include one and only one receivable/payable account (with an exception of "
                #         "internal transfers).",
                #         move.display_name,
                #     ))

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same currency.",
                        move.display_name,
                    ))

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same partner.",
                        move.display_name,
                    ))

                if counterpart_lines.account_id.account_type == 'asset_receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'                

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))
    
    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.payment.
        :param changed_fields: A list containing all modified fields on account.payment.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in self._get_trigger_fields_to_synchronize()):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

            # Make sure to preserve the write-off amount.
            # This allows to create a new payment with custom 'line_ids'.

            write_off_line_vals = []
            if liquidity_lines and counterpart_lines and writeoff_lines:
                write_off_line_vals.append({
                    'name': writeoff_lines[0].name,
                    'account_id': writeoff_lines[0].account_id.id,
                    'partner_id': writeoff_lines[0].partner_id.id,
                    'currency_id': writeoff_lines[0].currency_id.id,
                    'amount_currency': sum(writeoff_lines.mapped('amount_currency')),
                    'balance': sum(writeoff_lines.mapped('balance')),
                })

            line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

            line_ids_commands = [
                Command.update(liquidity_lines.id, line_vals_list[0]) if liquidity_lines else Command.create(line_vals_list[0]),
                # Command.update(counterpart_lines.id, line_vals_list[1]) if counterpart_lines else Command.create(line_vals_list[1])
            ]

            for line in writeoff_lines:
                line_ids_commands.append((2, line.id))

            for extra_line_vals in line_vals_list[2:]:
                line_ids_commands.append((0, 0, extra_line_vals))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.

            pay.move_id.write({
                'partner_id': pay.partner_id.id,
                'currency_id': pay.currency_id.id,
                'partner_bank_id': pay.partner_bank_id.id,
                'line_ids': line_ids_commands,
            })

class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'
    _description = 'Account Payment Line'

    account_payment_id = fields.Many2one('account.payment', string='Account Payment ID')
    move_id = fields.Many2one('account.move', string='Bill')
    amount_residual = fields.Float('Amount Residual')
    amount_to_pay = fields.Float('Amount to Pay')
    write_off_amount = fields.Float('Write off Amount')
    write_off_account_id = fields.Many2one('account.account', string='Write off Account')
    origin = fields.Char('Origin')
    is_full_payment = fields.Boolean('Full Payment')
    payment_difference = fields.Float('Payment Difference', compute='_get_payment_diffrence')
    invoice_date = fields.Date('Invoice Date', related='move_id.invoice_date')
    due_date = fields.Date('Invoice Date Due', related='move_id.invoice_date_due')
    
    @api.depends('amount_residual', 'amount_to_pay')
    def _get_payment_diffrence(self):
        for rec in self:
            if rec.amount_residual and rec.amount_to_pay:
                rec.payment_difference = rec.amount_residual - rec.amount_to_pay
            else:
                rec.payment_difference = 0
    
    @api.onchange('is_full_payment')
    def _onchange_(self):
        if self.is_full_payment:
            self.amount_to_pay = self.amount_residual
        else:            
            self.amount_to_pay = 0
