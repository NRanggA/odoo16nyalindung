from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError
from num2words import num2words

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    amount_text         = fields.Char(compute='amount_to_text', string='Terbilang')

    amount_charge       = fields.Monetary(string='Amount Adm')
    memo_charge         = fields.Char('Memo Charge', default="Bank Charge")
    charge_account_id   = fields.Many2one('account.account', string='Charge Account')
    no_memo             = fields.Char('No. Giro')
    date_memo           = fields.Date('Tanggal Giro')

    # Fungsi untuk memformat jumlah
    def format_amount(self, amount):
        if amount is not None:
            # Menggunakan format desimal dengan dua tempat desimal dan pemisah ribuan
            formatted_amount = '{:,.2f}'.format(amount).replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted_amount
        return '0,00'

    def amount_to_text(self):
        for record in self:
            amount = int(record.amount)
            record.amount_text = num2words(amount, lang='id')
    
    @api.onchange('amount_charge')
    def _onchange_amount_charge(self):
        for record in self:
            record.amount = record.amount + record.amount_charge
    
    def action_post(self):
        ''' draft -> posted '''        
        if self.payment_type != 'outbound':            
            super().action_post()
        else:            
            if self.payment_line_ids:
                payment_lines = list(map(lambda x: (3, x.id), self.move_id.line_ids))
                debit_tot = credit_tot = 0
                amount_total = 0.0

                for pline in self.payment_line_ids:
                    if pline.amount_to_pay > 0:
                        amount = self.currency_id._convert(pline.amount_to_pay, self.move_id.company_currency_id, self.company_id, self.date)
                        debit = amount
                        amount_currency = pline.amount_to_pay

                        bill_line = pline.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')

                        line_vals = {
                            'account_id': bill_line.account_id.id,
                            'debit': debit,
                            'credit': 0.0,
                            'amount_currency': amount_currency,
                            'partner_id': self.partner_id.id,
                        }

                        amount_total += amount
                        payment_lines.append((0, 0, line_vals))

                        if pline.write_off_amount != 0 and pline.write_off_account_id:
                            write_off_amount = self.currency_id._convert(pline.write_off_amount, self.move_id.company_currency_id, self.company_id, self.date)
                            wo_debit = wo_credit = 0
                            if write_off_amount > 0:
                                wo_debit = write_off_amount
                            else:
                                wo_credit = abs(write_off_amount)

                            write_off_vals = {
                                'account_id': pline.write_off_account_id.id,
                                'debit': wo_debit,
                                'credit': wo_credit,
                                'amount_currency': pline.write_off_amount,
                                'partner_id': self.partner_id.id,
                            }

                            amount_total += write_off_amount
                            payment_lines.append((0, 0, write_off_vals))
                    else:
                        pline.unlink()

                # Menambahkan Debit untuk 'amount_charge'
                if self.amount_charge:
                    if not self.charge_account_id:
                        raise UserError(_(
                            "Silahkan masukkan account pada field Charge Account !",
                        ))
                    charge_debit_vals = {
                        'account_id'    : self.charge_account_id.id,
                        'debit'         : self.amount_charge,
                        'credit'        : 0.0,
                        'partner_id'    : self.partner_id.id,
                        'name'          : self.memo_charge,
                    }
                    payment_lines.append((0, 0, charge_debit_vals))

                    # Tambahkan nilai dari amount_charge ke total amount untuk kredit
                    amount_total += self.amount_charge

                if amount_total > 0:
                    credit_tot = amount_total
                else:
                    debit_tot = abs(amount_total)

                balance_line_vals = {
                    'account_id': self.outstanding_account_id.id,
                    'debit': debit_tot,
                    'credit': credit_tot,
                    'partner_id': self.partner_id.id,
                }
                payment_lines.append((0, 0, balance_line_vals))

                self.move_id.write({'line_ids': payment_lines})            

                self.move_id._post(soft=False)

                for bill, payment_move_line in zip(self.payment_line_ids.move_id, self.move_id.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')):
                    bill_line_dua = bill.line_ids.filtered(lambda x: x.account_id.account_type == 'liability_payable')
                    (bill_line_dua + payment_move_line).reconcile()
            else:
                super().action_post()

    def report_data(self):
        if self.journal_id.type == 'bank':
            return self.env.ref('ny_account.action_report_payment_vendor_bank').report_action(self)
        else:
            return self.env.ref('ny_account.action_report_payment_vendor_cash').report_action(self)
