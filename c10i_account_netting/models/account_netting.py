from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

class AccountNetting(models.Model):
    _name = 'account.netting'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Account Netting'
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, default=lambda self: _('New'), tracking=True)
    date = fields.Date(string='Accounting Date', default=fields.Date.today, required=True, tracking=True)
    
    # Source and Destination Partners and Accounts
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='restrict')
    # src_partner_id = fields.Many2one('res.partner', string='Partner', required=False, ondelete='restrict')
    account_ids = fields.Many2many('account.account', 
                                'src_netting_account_rel', 'src_netting_id', 'account_id', 
                                string='Source Accounts', required=True)
    # dest_partner_id = fields.Many2one('res.partner', string='Destination Partner', required=False, ondelete='restrict')
    # dest_account_ids = fields.Many2many('account.account',
    #                             'dest_netting_account_rel', 'dest_netting_id', 'account_id',
    #                             string='Destination Accounts', required=True)
    line_ids = fields.One2many('account.netting.line', 'netting_id', string='Origin Entries')
    dr_line_ids = fields.One2many('account.netting.line', 'netting_id', domain=[('amount_residual','>',0)], string='Debtors Entries')
    cr_line_ids = fields.One2many('account.netting.line', 'netting_id', domain=[('amount_residual','<',0)], string='Creditors Entries')

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, ondelete='restrict')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], default='draft', string='Status', tracking=True)

    # @api.onchange('src_partner_id')
    # def onchange_src_partner(self):
    #     if self.src_partner_id:
    #         self.dest_partner_id = self.src_partner_id

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can only delete netting entries in draft state.'))
        return super(AccountNetting, self).unlink()

    def reconcile_netting_lines(self):
        self.ensure_one()
        for reverse_line, ori_line  in zip(self.move_id.line_ids, self.line_ids.mapped('move_line_id')):
            (reverse_line + ori_line).reconcile()

    def action_post(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('No entries to Compensate.'))

            # total_balance = sum(rec.line_ids.mapped('amount_residual'))
            # if float_compare(total_balance, 0.0, precision_rounding=self.env.company.currency_id.rounding) != 0:
            #     raise UserError(_('Total balance must be zero to net.'))

            move_lines = []
            total_debtors = sum(rec.dr_line_ids.mapped('amount_residual'))
            total_creditors = sum(rec.cr_line_ids.mapped('amount_residual'))
            netting_amount = min(total_debtors, -total_creditors)

            available_creditors = netting_amount
            for dline in rec.dr_line_ids:
                credit_amount = min(available_creditors, dline.amount_residual)
                if credit_amount:
                    move_lines.append(dline._prepare_reverse_move(-credit_amount))
                available_creditors -= credit_amount
            
            available_debtors = netting_amount
            for cline in rec.cr_line_ids:
                debit_amount = min(available_debtors, -cline.amount_residual)
                if debit_amount:
                    move_lines.append(cline._prepare_reverse_move(debit_amount))
                available_debtors -= debit_amount
            
            if move_lines:
                move_vals = {
                    # 'ref': _('Netting from %s to %s') % (rec.src_partner_id.name, rec.dest_partner_id.name),
                    'journal_id': rec.journal_id.id,
                    'date': rec.date,
                    'line_ids': list(map(lambda x: (0, 0, x), move_lines)),
                }
            
            if not rec.move_id:
                move = self.env['account.move'].create(move_vals)
            else:
                move = rec.move_id
                move.line_ids.unlink()  # Clear existing lines
                move.write(move_vals)
            move.action_post()
            rec.move_id = move.id
            rec.name = move.name

            # Reconcile original and reverse lines
            rec.reconcile_netting_lines()

            rec.state = 'posted'
    
    def action_draft(self):
        for rec in self:
            if rec.state != 'posted':
                raise UserError(_('You can only reset netting entries that are posted.'))
            rec.move_id.button_draft()
            rec.move_id.line_ids.remove_move_reconcile()
            rec.state = 'draft'

class AccountNettingLine(models.Model):
    _name = 'account.netting.line'
    _description = 'Account Netting Line'

    netting_id = fields.Many2one('account.netting', string='Netting')
    src_netting_id = fields.Many2one('account.netting', string='Debtors Netting')
    dest_netting_id = fields.Many2one('account.netting', string='Creditors Netting')

    move_line_id = fields.Many2one('account.move.line', string='Journal Item', required=True)
    move_id = fields.Many2one('account.move', string='Move', related='move_line_id.move_id', store=True, readonly=True)
    amount_residual = fields.Monetary(string='Residual Amount', readonly=True)
    currency_id = fields.Many2one('res.currency', related='move_line_id.currency_id', store=True, readonly=True)
    amount_currency = fields.Monetary(string='Amount in Currency', related='move_line_id.amount_currency', store=True, readonly=True)

    def _prepare_reverse_move(self, amount):
        self.ensure_one()
        # if self.amount_residual == 0.0:
        #     raise UserError(_('Cannot create reverse entry for zero residual amount.'))
        if float_compare(self.amount_residual, 0.0, precision_rounding=self.env.company.currency_id.rounding) == 0:
            raise UserError(_('Cannot create reverse entry for zero residual amount.'))
        debit = amount if amount > 0 else 0.0
        credit = abs(amount) if amount < 0 else 0.0
        return {
            'account_id': self.move_line_id.account_id.id,
            'partner_id': self.move_line_id.partner_id.id,
            'debit': debit,
            'credit': credit,
            'name': _('Netting Reverse Entry of %s') % self.move_id.name,
            # 'currency_id': self.currency_id.id,
            'amount_currency': amount
        }
