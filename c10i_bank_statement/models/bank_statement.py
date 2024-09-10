from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
    ], string='Status', default='draft')

    def unlink(self):
        if any(self.filtered(lambda rec: rec.state != 'draft')):
            raise UserError(_('You cannot delete a bank statement which is not Draft.'))
        return super(AccountBankStatement, self).unlink()    

    def button_validate(self):
        self.write({'state': 'validated'})
    
    def button_draft(self):
        self.write({'state': 'draft'})
    
    def button_reconcile(self):
        return {
            'name': _('Reconcile Items'),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban',
            'res_model': 'account.bank.statement.line',
            'view_id': self.env.ref('account_reconcile_oca.bank_statement_line_reconcile_view').id,
            'context': {'default_journal_id': self.journal_id.id, 'search_default_not_reconciled': True, 'view_ref': 'account_reconcile_oca.bank_statement_line_form_reconcile_view'},
            'domain': [('statement_id', '=', self.id)],
        }