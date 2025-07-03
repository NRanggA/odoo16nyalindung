from odoo import models, api
from lxml import etree

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def action_view_credit_balance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Balance',
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'view_id': self.env.ref("c10i_payment_credit_balance.view_customer_unreconciled_credit_balance_tree").id,
            'domain': [('account_id', '=', self.env.company.account_credit_balance_id.id)],
            'context': {
                'search_default_unreconciled': 1,
                'search_default_group_by_partner': 1,
            },
            'target': 'current',
        }