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
        for rec in self:
            
            if rec.journal_id.type == 'bank':
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
    