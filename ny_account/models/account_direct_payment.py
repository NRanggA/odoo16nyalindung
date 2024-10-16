from odoo import models, fields, api, _
from num2words import num2words

class DirectPayment(models.Model):
    _inherit = 'account.direct.payment'

    amount_text         = fields.Char(compute='amount_to_text', string='Terbilang')

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
        if self.journal_id.type == 'bank':
            return self.env.ref('ny_account.action_report_direct_payment_bank').report_action(self)
        else:
            return self.env.ref('ny_account.action_report_direct_payment_cash').report_action(self)