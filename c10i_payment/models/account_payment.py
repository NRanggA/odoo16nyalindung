from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_line_ids = fields.One2many('account.payment.line', 'account_payment_id', string='Payment Line')
    amount = fields.Monetary(compute='_compute_amount', store=True)
    
    @api.depends('payment_line_ids.amount_to_pay')
    def _compute_amount(self):
        for rec in self:
            amnt_total_to_pay = sum([line.amount_to_pay for line in rec.payment_line_ids])
            rec.amount = amnt_total_to_pay

    def get_bills(self):
        for rec in self:
            if rec.partner_id:
                existing_move_ids = [line.move_id.id for line in rec.payment_line_ids]
                for move in self.env['account.move'].search([('partner_id', '=', rec.partner_id.id), ('state', '=', 'confirm'), ('id', 'not in', existing_move_ids)]):
                    if move.id not in existing_move_ids:
                        self.env['account.payment.line'].create({
                            'account_payment_id': self.id,
                            'move_id': move.id,
                            'amount_residual': move.amount_residual,
                            'origin': ''
                        })
            else:
                raise ValidationError("Partner or Vendor must be filled")
            
    # def action_post(self):
    #     ''' draft -> posted '''
    #     # if not beneran_payment:
    #     #     super().action_post()
    #     # else:
    #     payment_line = []
    #     amount_total = 0.0
    #     debit_tot = credit_tot = 0.0
    #     for pline in self.payment_line_ids:
    #         if pline.amount_to_pay > 0:
    #             debit = credit = 0
    #             amount = self.currency_id._convert(pline.amount_to_pay, self.move_id.company_currency_id, self.company_id, self.date)
    #             debit = amount
    #             amount_currency = pline.amount_to_pay
    #             line_vals= {
    #                     'account_id': pline.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'payable'),
    #                     'debit': debit,
    #                     'credit': credit,
    #                     'amount_currency': amount_currency,
    #                     'partner_id': self.partner_id.id,
    #             }
    #             amount_total += amount
    #             payment_line.append((0,0,line_vals))

    #             bank_line_vals = {
    #                 'account_id': self.journal_id.default_account_id.id,
    #                 'debit': debit_tot,
    #                 'credit': credit_tot,
    #                 'partner_id': self.partner_id.id,
    #             }
    #         payment_line.append((0,0,bank_line_vals))

    #     self.move_id.write({'line_ids': payment_line})

    #     # self.filtered(
    #     #     lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
    #     # )._create_paired_internal_transfer_payment()
    #     self.move_id._post(soft=False)

    def action_post(self):
        ''' draft -> posted '''
        if self.payment_type != 'outbound':
            super().action_post()
        else:
            payment_lines = []
            debit_tot = credit_tot = 0
            amount_total = 0.0
            
            for pline in self.payment_line_ids:
                if pline.amount_to_pay > 0:
                    debit = credit = 0
                    amount = self.currency_id._convert(pline.amount_to_pay, self.move_id.company_currency_id, self.company_id, self.date)
                    debit = amount
                    amount_currency = pline.amount_to_pay

                    line_ids = [line for line in pline.move_id.line_ids]

                    payable_account_id = pline.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
                    
                    line_vals = {
                        'account_id': payable_account_id.id,
                        'debit': debit,
                        'credit': credit,
                        'amount_currency': amount_currency,
                        'partner_id': self.partner_id.id,
                    }
                    
                    amount_total += amount
                    payment_lines.append((0, 0, line_vals))

            if amount_total > 0:
                bank_line_vals = {
                    'account_id': self.journal_id.default_account_id.id,
                    'debit': debit_tot,
                    'credit': credit_tot,
                    'partner_id': self.partner_id.id,
                }
                payment_lines.append((0, 0, bank_line_vals))

            
            print("=============================", payment_lines)

            self.move_id.write({'line_ids': payment_lines})

            self.move_id._post(soft=False)

class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'
    _description = 'Account Payment Line'

    account_payment_id = fields.Many2one('account.payment', string='Account Payment ID')
    move_id = fields.Many2one('account.move', string='Bill')
    amount_residual = fields.Float('Amount Residual')
    amount_to_pay = fields.Float('Amount to Pay')
    write_off_amount = fields.Float('Write off Amount')
    account_id = fields.Many2one('account.account', string='Write off Account')
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
