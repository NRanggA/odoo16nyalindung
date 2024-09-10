from odoo import models, api

class CustomSaleOrderReport(models.AbstractModel):
    _name = 'report.ny_salesorder_report.sales_order_template_custom'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = {
            'doc_model': 'sale.order',
            'docs': self.env['sale.order'].browse(docids),
            'doc_ids': docids,
            'bank_name': False,
            'bank_acc_number': False,
        }
        options = data.get('options', {})
        if options.get('src_model')=='select.bank.wizard' and options.get('dest_model')=='sale.order':
            wizard = self.env['select.bank.wizard'].browse(options['src_id'])
            res.update({
                'doc_model': 'sale.order',
                'docs': self.env['sale.order'].browse(options['dest_id']),
                'doc_ids': [options['dest_id']],
                'bank_name': wizard.bank_id.bank_id.name,
                'bank_acc_number': wizard.bank_id.acc_number,
            })

        return res

    @api.model
    def get_report_filename(self, docids, data):
        sale_order = self.env['sale.order'].browse(docids)
        return 'Sales Order - %s.pdf' % sale_order.name
