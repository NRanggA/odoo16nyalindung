from odoo import models, fields, api

class SelectBankWizard(models.TransientModel):
    _name = 'select.bank.wizard'
    _description = 'Select Bank Account Wizard'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    bank_id = fields.Many2one('res.partner.bank', string="Bank Account", required=True, domain=lambda self: [('partner_id', '=', self.env.company.partner_id.id)])
    # bank_id = fields.Many2one('res.bank', string="Bank Account", required=True)

    def print_report(self):
        return self.env.ref('ny_salesorder_report.report_sales_order_custom').report_action(self, data={
            'options': {'src_model': self._name, 'src_id': self.id, 'dest_model': 'sale.order', 'dest_id': self.env.context.get('active_id')}
            })