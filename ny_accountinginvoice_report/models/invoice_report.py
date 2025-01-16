from odoo import fields, models
from num2words import num2words

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    amount_text = fields.Char(compute='amount_to_text', string='Terbilang')

    def amount_to_text(self):
        for record in self:
            amount = record.amount_total
            main_part = int(amount)
            decimal_part = int(round((amount - main_part) * 100))

            main_part_text = num2words(main_part, lang='id')

            if decimal_part > 0:
                decimal_part_text = num2words(decimal_part, lang='id')
                record.amount_text = f"{main_part_text} koma {decimal_part_text}"
            else:
                record.amount_text = main_part_text
    
    def format_amount(self, amount):
        if amount is not None:
            # Menggunakan format desimal dengan dua tempat desimal dan pemisah ribuan
            formatted_amount = '{:,.2f}'.format(amount).replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted_amount
        return '0,00'

