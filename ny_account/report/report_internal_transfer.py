import base64
from decimal import Decimal

from odoo import models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource


class InternalTransferReport(models.AbstractModel):
    _name = 'report.ny_account.report_internal_transfer'
    _description = 'Internal Transfer Report'

    def _get_report_values(self, docids, data=None):
        from num2words import num2words

        payments = self.env['account.payment'].browse(docids).exists()
        payments.check_access_rights('read')
        payments.check_access_rule('read')
        if not payments or any(not payment.is_internal_transfer for payment in payments):
            raise UserError('Report ini hanya untuk Internal Transfer.')

        # Cetak transaksi asal sekali, termasuk saat kedua sisi dipilih.
        origins = self.env['account.payment']
        for payment in payments:
            origin = payment
            if payment.payment_type == 'inbound' and payment.paired_internal_transfer_payment_id:
                origin = payment.paired_internal_transfer_payment_id
            origin.check_access_rule('read')
            origins |= origin

        status_labels = {'draft': 'Draft', 'posted': 'Posted', 'cancel': 'Dibatalkan'}
        separators = str.maketrans(',.', '.,')
        details = {}
        for payment in origins:
            currency = payment.currency_id
            rounded = Decimal(str(currency.round(payment.amount)))
            formatted = format(rounded, f',.{currency.decimal_places}f').translate(separators)
            prefix = 'Rp' if currency.name == 'IDR' else currency.name
            if currency.name == 'IDR':
                whole = int(rounded)
                cents = int((rounded - whole) * 100)
                words = num2words(whole, lang='id') + ' rupiah'
                if cents:
                    words += ' dan ' + num2words(cents, lang='id') + ' sen'
            else:
                words = currency.amount_to_text(float(rounded))
            details[payment.id] = {
                'amount': f'{prefix} {formatted}',
                'words': words,
                'status': status_labels.get(payment.state, payment.state),
            }

        logo_path = get_module_resource('ny_account', 'static', 'src', 'img', 'logo1.png')
        logo = False
        if logo_path:
            with open(logo_path, 'rb') as image_file:
                logo = 'data:image/png;base64,' + base64.b64encode(image_file.read()).decode('ascii')

        return {
            'doc_ids': origins.ids,
            'doc_model': 'account.payment',
            'docs': origins,
            'transfer_details': details,
            'transfer_logo': logo,
        }
