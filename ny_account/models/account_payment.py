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

    # Field untuk menyimpan jurnal tambahan (jurnal charge)
    charge_move_id      = fields.Many2one('account.move', string='Secondary Journal Entry', readonly=True)

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
    
    @api.onchange('payment_line_ids', 'amount_charge')
    def _onchange_amount(self):
        for rec in self:
            amount = 0
            if rec.payment_line_ids:
                amount = sum([line.amount_to_pay for line in rec.payment_line_ids])
                rec.amount = amount

                rec.amount += rec.amount_charge

    def report_data(self):
        if self.journal_id.type == 'bank':
            return self.env.ref('ny_account.action_report_payment_vendor_bank').report_action(self)
        else:
            return self.env.ref('ny_account.action_report_payment_vendor_cash').report_action(self)

    def action_post(self):
        super().action_post()
        # Mengecek apakah ada biaya administrasi (amount_charge)
        for payment in self.filtered(lambda p: p.payment_type == 'outbound'):
            if payment.amount_charge > 0:
                    if not payment.charge_account_id:
                        raise ValidationError("Charge Acount Harus di isi")
                    # Membuat entri jurnal untuk biaya administrasi
                    move_vals = {
                        'journal_id': payment.journal_id.id,
                        'move_type': 'entry',
                        'line_ids': [
                            # Baris debit 
                            (0, 0, {
                                'account_id': payment.charge_account_id.id,
                                'name'      : payment.memo_charge,
                                'debit'     : payment.amount_charge,
                                'credit'    : 0.0,
                                'partner_id': payment.partner_id.id,
                            }),
                            # Baris kredit
                            (0, 0, {
                                'account_id': payment.outstanding_account_id.id,  
                                'name'      : payment.memo_charge,
                                'debit'     : 0.0,
                                'credit'    : payment.amount_charge,
                                'partner_id': payment.partner_id.id,
                            }),
                        ],
                    }

                    # Membuat jurnal entry untuk charge
                    charge_move = self.env['account.move'].create(move_vals)

                    # Posting jurnal entry yang baru dibuat
                    charge_move._post(soft=False)

                    # Simpan jurnal kedua di charge_move_id
                    payment.charge_move_id = charge_move

    def button_open_journal_entry(self):
        ''' Override button agar bisa menampilkan 2 jurnal yang dibuar.
        '''
        self.ensure_one()
        
        # Mengambil ID dari move_id (jurnal utama) dan charge_move_id (jurnal tambahan)
        move_ids = [self.move_id.id]
        if self.charge_move_id:
            move_ids.append(self.charge_move_id.id)

        return {
            'name': _("Journal Entries"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', move_ids)], 
            'context': {'create': False},
        }
    
    # def _synchronize_from_moves(self, changed_fields):
    #     # return
    #     ''' Update the account.payment regarding its related account.move.
    #     Also, check both models are still consistent.
    #     :param changed_fields: A set containing all modified fields on account.move.
    #     '''
    #     if self._context.get('skip_account_move_synchronization'):
    #         return

    #     for pay in self.with_context(skip_account_move_synchronization=True):

    #         # After the migration to 14.0, the journal entry could be shared between the account.payment and the
    #         # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
    #         if pay.move_id.statement_line_id:
    #             continue

    #         move = pay.move_id
    #         move_vals_to_write = {}
    #         payment_vals_to_write = {}

    #         if 'journal_id' in changed_fields:
    #             if pay.journal_id.type not in ('bank', 'cash'):
    #                 raise UserError(_("A payment must always belongs to a bank or cash journal."))

    #         if 'line_ids' in changed_fields:
    #             all_lines = move.line_ids
    #             liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

    #             if len(liquidity_lines) != 1:
    #                 raise UserError(_(
    #                     "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #                     "include one and only one outstanding payments/receipts account.",
    #                     move.display_name,
    #                 ))

    #             # if len(counterpart_lines) != 1:
    #             #     raise UserError(_(
    #             #         "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #             #         "include one and only one receivable/payable account (with an exception of "
    #             #         "internal transfers).",
    #             #         move.display_name,
    #             #     ))

    #             if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
    #                 raise UserError(_(
    #                     "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #                     "share the same currency.",
    #                     move.display_name,
    #                 ))

    #             if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
    #                 raise UserError(_(
    #                     "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #                     "share the same partner.",
    #                     move.display_name,
    #                 ))

    #             if counterpart_lines.account_id.account_type == 'asset_receivable':
    #                 partner_type = 'customer'
    #             else:
    #                 partner_type = 'supplier'                

    #             liquidity_amount = liquidity_lines.amount_currency

    #             move_vals_to_write.update({
    #                 'currency_id': liquidity_lines.currency_id.id,
    #                 'partner_id': liquidity_lines.partner_id.id,
    #             })
    #             payment_vals_to_write.update({
    #                 # 'amount': abs(liquidity_amount),
    #                 'partner_type': partner_type,
    #                 'currency_id': liquidity_lines.currency_id.id,
    #                 'destination_account_id': counterpart_lines.account_id.id,
    #                 'partner_id': liquidity_lines.partner_id.id,
    #             })

    #             # kondisi jika nilai amount charge tidak ada, maka nilai amount akan diubah sesuai dengan di jurnal
    #             if not pay.amount_charge:
    #                 payment_vals_to_write.update({
    #                     'amount': abs(liquidity_amount),
    #                 })

    #             if liquidity_amount > 0.0:
    #                 payment_vals_to_write.update({'payment_type': 'inbound'})
    #             elif liquidity_amount < 0.0:
    #                 payment_vals_to_write.update({'payment_type': 'outbound'})

    #         move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
    #         pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))