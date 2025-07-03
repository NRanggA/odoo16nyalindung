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
                # amount += sum([line.write_off_amount for line in rec.payment_line_ids if line.write_off_amount != 0 and line.write_off_account_id])

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.payment_line_ids = [(5, 0, 0)]        

    def get_bills(self):
        for rec in self.filtered(lambda x: x.state=='draft'):
            if rec.partner_id:
                existing = rec.payment_line_ids.mapped('move_id')
                domain = [
                    ('partner_id', '=', rec.partner_id.id),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'in_payment', 'partial']),
                    ('amount_residual', '>', 0), # Kondisi baru yang di tambahkan, kalo 0 tidak usah ditampilkan lagi 
                    
                ]
                if rec.payment_type == 'outbound':
                    domain.append(('move_type', '=', 'in_invoice'))
                elif rec.payment_type == 'inbound':
                    domain.append(('move_type', '=', 'out_invoice'))

                moves = self.env['account.move'].search(domain)
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
    
    ###################### HELPER METHOD ######################
    def _prepare_move_vals_from_payment_lines(self):
        payment_lines = []
        amount_total = 0.0
        for pline in self.payment_line_ids.filtered(lambda x: x.amount_to_pay > 0 or x.write_off_amount > 0):
            amount, line_vals = pline._prepare_move_line_vals()
            amount_total += amount
            payment_lines.append(line_vals)

            # If there is a write-off amount and account, prepare the write-off line
            # Especially for inbound payments where customer pays more than the invoice residual amount
            # User must assign write-off amount and account
            if self.payment_type=='inbound' and pline.amount_to_pay > pline.amount_residual:
                if pline.write_off_amount != pline.payment_difference:
                    raise UserError(_("Write-off amount must be equal to Payment Difference since Customer Pay more than Invoice Residual Amount."))
                elif not pline.write_off_account_id:
                    raise UserError(_("Write-off amount must assign to an Account since Customer Pay more than Invoice Residual Amount."))
            if pline.write_off_amount and pline.write_off_account_id:
                write_off_amount, write_off_vals = pline._prepare_writeoff_line_vals()
                amount_total += -write_off_amount
                payment_lines.append(write_off_vals)
        return amount_total, payment_lines

    def _prepare_payment_move_vals(self, amount_total):
        self.ensure_one()
        debit_tot = credit_tot = 0
        if self.payment_type == 'inbound':
            if amount_total > 0:
                debit_tot = amount_total
            else:
                credit_tot = abs(amount_total)
        elif self.payment_type == 'outbound':
            if amount_total > 0:
                credit_tot = amount_total
            else:
                debit_tot = abs(amount_total)
            
        return {
            # 'account_id': self.journal_id.default_account_id.id,
            'name' : self.ref,
            'account_id': self.outstanding_account_id.id,
            'debit': debit_tot,
            'credit': credit_tot,
            'partner_id': self.partner_id.id,
        }

    def reconcile_payment_lines(self):
        """ Reconcile payment lines with their respective invoices or bills """
        if self.payment_type == 'inbound':
            for invoice, payment_move_line in zip(
                    self.payment_line_ids.move_id, 
                    self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'asset_receivable')
            ):
                inv_line_to_recon = invoice.line_ids.filtered(lambda x: x.account_id.account_type == 'asset_receivable')
                (inv_line_to_recon + payment_move_line).reconcile()
        elif self.payment_type == 'outbound':
            for bill, payment_move_line in zip(
                self.payment_line_ids.move_id, 
                self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
            ):
                bill_line_to_recon = bill.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
                (bill_line_to_recon + payment_move_line).reconcile()

    def action_post(self):
        ''' draft -> posted '''        
        if self.payment_type in ('inbound','outbound') and self.payment_line_ids and any([l.amount_to_pay>0 for l in self.payment_line_ids]):
            # Delete payment_line_ids that is not allocated
            not_allocated_payment = self.payment_line_ids.filtered(lambda l: l.amount_to_pay == 0 and l.write_off_amount == 0)
            if not_allocated_payment:
                not_allocated_payment.unlink()

            # Delete Existing Move Lines
            payment_lines = list(map(lambda x:(3,x.id), self.move_id.line_ids))
            
            amount_total, payment_line_vals_list = self._prepare_move_vals_from_payment_lines()
            # Add Move LInes from Selected payment_line_ids
            payment_lines.extend(list(map(lambda vals: (0, 0, vals), payment_line_vals_list)))

            # Add Move LInes for Account Bank/Cash
            payment_lines.append((0, 0, self._prepare_payment_move_vals(amount_total)))

            # Update Existing Move Lines
            self.move_id.write({
                # 'ref': '',
                'ref': self.ref,
                'line_ids': payment_lines
                })            
            
            self.move_id._post(soft=False)

            # Reconciliation
            self.reconcile_payment_lines()
        else:
            super().action_post()

    def action_post_old(self):
        ''' draft -> posted '''        
        if self.payment_type=='inbound' and self.payment_line_ids and any([l.amount_to_pay>0 for l in self.payment_line_ids]):
            payment_lines = list(map(lambda x:(3,x.id), self.move_id.line_ids))
            debit_tot = credit_tot = 0
            amount_total = 0.0
            
            for pline in self.payment_line_ids:
                if pline.amount_to_pay > 0:
                    debit = credit = 0
                    amount_receivable_to_pay = pline.amount_to_pay
                    if pline.write_off_amount and pline.write_off_account_id:
                        amount_receivable_to_pay += pline.write_off_amount
                    amount = self.currency_id._convert(amount_receivable_to_pay, self.move_id.company_currency_id, self.company_id, self.date)
                    credit = amount
                    amount_currency = amount_receivable_to_pay

                    bill_line = pline.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'asset_receivable')
                    line_vals = {
                        'name': pline.move_id.name,
                        'account_id': bill_line.account_id.id,
                        'debit': debit,
                        'credit': credit,
                        'amount_currency': -amount_currency,
                        'partner_id': self.partner_id.id,
                    }

                    amount_total += amount
                    payment_lines.append((0, 0, line_vals))

                    if pline.write_off_amount and pline.write_off_account_id:
                        write_off_amount = self.currency_id._convert(pline.write_off_amount, self.move_id.company_currency_id, self.company_id, self.date)
                        wo_debit = wo_kredit = 0
                        if write_off_amount > 0:
                            wo_debit = write_off_amount
                        else:
                            wo_kredit = abs(write_off_amount)
                        
                        write_off_vals = {
                            'name': pline.description,
                            'account_id': pline.write_off_account_id.id,
                            'debit': wo_debit,
                            'credit': wo_kredit,
                            'amount_currency': pline.write_off_amount,
                            'partner_id': self.partner_id.id,
                        }
                    
                        amount_total += -write_off_amount
                        payment_lines.append((0, 0, write_off_vals))
                else:
                    pline.unlink()

            if amount_total > 0:
                debit_tot = amount_total
            else:
                credit_tot = abs(amount_total)
                
            bank_line_vals = {
                # 'account_id': self.journal_id.default_account_id.id,
                'name' : self.ref,
                'account_id': self.outstanding_account_id.id,
                'debit': debit_tot,
                'credit': credit_tot,
                'partner_id': self.partner_id.id,
            }

            payment_lines.append((0, 0, bank_line_vals))

            self.move_id.write({
                # 'ref': '',
                'ref': self.ref,
                'line_ids': payment_lines
                })            
            
            self.move_id._post(soft=False)

            for bill, payment_move_line in zip(self.payment_line_ids.move_id, self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'asset_receivable')):
                bill_line_dua = bill.line_ids.filtered(lambda x: x.account_id.account_type == 'asset_receivable')
                (bill_line_dua + payment_move_line).reconcile()
        elif self.payment_type=='outbound' and self.payment_line_ids and any([l.amount_to_pay>0 for l in self.payment_line_ids]):
            payment_lines = list(map(lambda x:(3,x.id), self.move_id.line_ids))
            debit_tot = credit_tot = 0
            amount_total = 0.0
            
            for pline in self.payment_line_ids:
                if pline.amount_to_pay > 0:
                    debit = credit = 0
                    amount_payable_to_pay = pline.amount_to_pay
                    if pline.write_off_amount != 0 and pline.write_off_account_id:
                        amount_payable_to_pay += pline.write_off_amount
                    amount = self.currency_id._convert(amount_payable_to_pay, self.move_id.company_currency_id, self.company_id, self.date)
                    debit = amount
                    amount_currency = amount_payable_to_pay

                    bill_line = pline.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
                    
                    line_vals = {
                        'name': pline.move_id.name,
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
                        wo_debit = wo_kredit = 0
                        if write_off_amount > 0:
                            wo_kredit = write_off_amount
                        else:
                            wo_debit = abs(write_off_amount)
                        
                        write_off_vals = {
                            'account_id': pline.write_off_account_id.id,
                            'debit': wo_debit,
                            'credit': wo_kredit,
                            'amount_currency': -pline.write_off_amount,
                            'partner_id': self.partner_id.id,
                        }
                    
                        amount_total += -write_off_amount
                        payment_lines.append((0, 0, write_off_vals))
                else:
                    pline.unlink()

            if amount_total > 0:
                credit_tot = amount_total
            else:
                debit_tot = abs(amount_total)
                
            bank_line_vals = {
                # 'account_id': self.journal_id.default_account_id.id,
                'name' : self.ref,
                'account_id': self.outstanding_account_id.id,
                'debit': debit_tot,
                'credit': credit_tot,
                'partner_id': self.partner_id.id,
            }

            payment_lines.append((0, 0, bank_line_vals))

            # self.move_id.write({'line_ids': payment_lines})  
            self.move_id.write({
                # 'ref': '',
                'ref': self.ref,
                'line_ids': payment_lines
                })             
            
            self.move_id._post(soft=False)

            for bill, payment_move_line in zip(self.payment_line_ids.move_id, self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')):
                bill_line_dua = bill.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
                (bill_line_dua + payment_move_line).reconcile()
        else:
            super().action_post()

    def _synchronize_from_moves(self, changed_fields):
        return
    
    def _synchronize_to_moves(self, changed_fields):
        return

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
    
    def _prepare_move_line_vals(self):
        self.ensure_one()
        payment = self.account_payment_id
        if not self.amount_to_pay:
            return 0.0, {}
        
        amount_residual_to_pay = self.amount_to_pay
        if self.write_off_amount and self.write_off_account_id:
            amount_residual_to_pay += self.write_off_amount
        amount = payment.currency_id._convert(amount_residual_to_pay, 
                    payment.move_id.company_currency_id, payment.company_id, payment.date)
        
        if not self.move_id.amount_residual:
            raise ValidationError(_(f"Its seem the {'Invoice' if payment.payment_type=='inbound' else 'Bill' } is already Paid."))
        
        # this was enable because sometimes customer pay more than the Invoice amount
        print(":::::::::::::::", amount, self.move_id.amount_residual)
        # if payment.payment_type == 'inbound' and amount > self.move_id.amount_residual:
        #     raise ValidationError("Cannot allocate more than the residual amount.")
        # while this one should never happened. user should not be able to pay more than the bill amount
        if payment.payment_type == 'outbound' and amount > self.move_id.amount_residual:
            raise ValidationError("Cannot allocate more than the residual amount.")

        # Prepare the values for the move line
        if not self.move_id:
            raise ValidationError("Move line must be set before preparing move line values.")
        
        debit = credit = 0
        account = False
        if payment.payment_type == 'inbound':
            account = self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'asset_receivable').account_id
            credit = amount
            amount_currency = -amount_residual_to_pay
        elif payment.payment_type == 'outbound':
            account = self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable').account_id
            debit = amount
            amount_currency = amount_residual_to_pay
        
        line_vals = {
            'name': self.move_id.name,
            'account_id': account.id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency,
            'partner_id': payment.partner_id.id,
        }
        return amount, line_vals

    def _prepare_writeoff_line_vals(self):
        self.ensure_one()
        payment = self.account_payment_id
        if payment.payment_type=='inbound' and self.amount_to_pay < self.amount_residual and self.write_off_amount > self.payment_difference:
            raise UserError(_("Write-off amount cannot be greater than the payment difference."))
        elif payment.payment_type=='outbound' and self.write_off_amount > self.payment_difference:
            raise UserError(_("Write-off amount cannot be greater than the payment difference."))
        
        if not self.write_off_amount or not self.write_off_account_id:
            return 0.0, {}
        
        write_off_amount = payment.currency_id._convert(self.write_off_amount, payment.move_id.company_currency_id, 
                                        payment.company_id, payment.date)
        
        wo_debit = wo_kredit = amount_currency = 0
        if payment.payment_type == 'inbound':
            if write_off_amount > 0:
                wo_debit = write_off_amount
            else:
                wo_kredit = abs(write_off_amount)
            amount_currency = self.write_off_amount
        elif payment.payment_type == 'outbound':
            if write_off_amount > 0:
                wo_kredit = write_off_amount
            else:
                wo_debit = abs(write_off_amount)
            amount_currency = -1*self.write_off_amount
        
        write_off_vals = {
            'name': self.description,
            'account_id': self.write_off_account_id.id,
            'debit': wo_debit,
            'credit': wo_kredit,
            'amount_currency': amount_currency,
            'partner_id': payment.partner_id.id,
        }

        return write_off_amount, write_off_vals