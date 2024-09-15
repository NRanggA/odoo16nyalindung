from odoo import _, api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    def create_cash_statement(self):
        return {
            'name': ('Account Bank Statement'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'view_id': self.env.ref('account_statement_base.view_bank_statement_form').id,
            'context': {'default_journal_id': self.id},
        }    