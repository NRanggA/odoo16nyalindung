from odoo import models, fields, api, _
from num2words import num2words
from odoo.exceptions import ValidationError, UserError


class DirectPayment(models.Model):
    _inherit = 'account.direct.payment'

    amount_text         = fields.Char(compute='amount_to_text', string='Terbilang')
    jenis_pembayaran    = fields.Selection([
                            ('tunai', 'Tunai'),
                            ('transfer', 'Transfer'),
                            ('auto_debit', 'Auto Debit')
                        ], string='Jenis Pembayaran')
    atas_nama           = fields.Char('Atas Nama')
    
    department_id       = fields.Many2one('hr.department', string='Department')
    alokasi             = fields.Selection([
                            ('biaya', 'Biaya'),
                            ('persediaan', 'Persediaan'),
                        ], string='Alokasi')


    @api.onchange('partner_id')
    def _onchange_atas_nama(self):
        if self.partner_id:
            self.atas_nama = self.partner_id.name
        else:
            self.atas_nama = ''

    def format_amount(self, amount_total):
        if amount_total is not None:
            # Menggunakan format desimal dengan dua tempat desimal dan pemisah ribuan
            formatted_amount = '{:,.2f}'.format(amount_total).replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted_amount
        return '0,00'

    def amount_to_text(self):
        for record in self:
            amount = int(record.amount_total)
            record.amount_text = num2words(amount, lang='id')

    def report_data(self):

        if self.journal_id.type == 'bank' and self.direct_state == 'send':
            if not self.partner_id.bank_ids:
                raise ValidationError("Partner tidak memiliki informasi bank yang terdaftar.")
            return self.env.ref('ny_account.action_report_direct_payment_bank').report_action(self)
        elif self.journal_id.type == 'bank' and self.direct_state == 'receive':
            return self.env.ref('ny_account.action_report_direct_payment_bank_receive').report_action(self)
        elif self.journal_id.type == 'cash' and self.direct_state == 'send':
            return self.env.ref('ny_account.action_report_direct_payment_cash').report_action(self)
        elif self.journal_id.type == 'cash' and self.direct_state == 'receive':
            return self.env.ref('ny_account.action_report_direct_payment_cash_receive').report_action(self)