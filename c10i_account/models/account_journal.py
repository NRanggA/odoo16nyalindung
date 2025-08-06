from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_disallowed_ids = fields.Many2many('account.account', string='Disallowed Accounts', help='Accounts that are not allowed to be used in this journal.')

    @api.constrains('account_control_ids', 'account_disallowed_ids')
    def _check_account_conflict(self):
        for journal in self:
            conflict = journal.account_control_ids & journal.account_disallowed_ids
            if conflict:
                raise ValidationError(_("Conflict: These accounts are in both allowed and disallowed lists:\n%s") %
                                      ', '.join(conflict.mapped('display_name')))