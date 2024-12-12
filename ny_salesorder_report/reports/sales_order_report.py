from odoo import models, api
from num2words import num2words


class CustomSaleOrderReport(models.AbstractModel):
    _name = 'report.ny_salesorder_report.sales_order_template_custom'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Pastikan data tidak None untuk menghindari error
        data = data or {}
        res = {
            'doc_model': 'sale.order',
            'docs': self.env['sale.order'].browse(docids),
            'doc_ids': docids,
            'bank_name': False,
            'bank_acc_number': False,
            'lang': self.env.context.get('lang', 'id_ID'),
        }
        options = data.get('options', {})
        if options.get('src_model') == 'select.bank.wizard' and options.get('dest_model') == 'sale.order':
            wizard = self.env['select.bank.wizard'].browse(options['src_id'])
            res.update({
                'doc_model': 'sale.order',
                'docs': self.env['sale.order'].browse(options['dest_id']),
                'doc_ids': [options['dest_id']],
                'bank_name': wizard.bank_id.bank_id.name,
                'bank_acc_number': wizard.bank_id.acc_number,
            })

        return res

    def format_price(self, price_total):
        if price_total is not None:
            # Format desimal dengan dua tempat desimal dan pemisah ribuan
            formatted_price = '{:,.2f}'.format(price_total).replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted_price
        return '0,00'

    def price_to_text(self, price):
        # Konversi harga menjadi teks terbilang
        return num2words(price, lang='id')

    @api.model
    def get_report_filename(self, docids, data):
        if len(docids) == 1:
            sale_order = self.env['sale.order'].browse(docids[0])
            return 'Sales Order - %s.pdf' % sale_order.name
        return 'Sales Orders.pdf'
