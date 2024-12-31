from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def _must_check_constrains_date_sequence(self):
        
        if self.journal_id.type in ['bank', 'cash']:
            return False
        
        return super(AccountMove, self)._must_check_constrains_date_sequence()