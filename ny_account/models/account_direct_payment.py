from odoo import models, fields, api, _

class DirectPayment(models.Model):
    _inherit = 'account.direct.payment'

    def report_data(self):
        if self.journal_id.type == 'bank':
            return self.env.ref('ny_account.action_report_direct_payment_bank').report_action(self)
        else:
            return self.env.ref('ny_account.action_report_direct_payment_cash').report_action(self)