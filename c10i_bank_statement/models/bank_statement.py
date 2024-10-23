from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    cash_count_line_ids = fields.One2many('cash.count.line', 'statement_id', string='Cash Count Line')
    type = fields.Selection([], string='Type', related="journal_id.type")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
    ], string='Status', default='draft')
    
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        compute=False, store=True,
        check_company=True,
    )

    def unlink(self):
        if any(self.filtered(lambda rec: rec.state != 'draft')):
            raise UserError(_('You cannot delete a bank statement which is not Draft.'))
        return super(AccountBankStatement, self).unlink()    

    def button_validate(self):
        self.write({'state': 'validated'})
        for line in self.line_ids:
            line.reconcile_bank_line()
    
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
        
    @api.model
    def default_get(self, fields):
        res = super(AccountBankStatement, self).default_get(fields)
        if res:
            records = self.env['cash.type'].search([])
            vals = [(0, 0, {'cash_type_id': rec.id}) for rec in records]
            res.update({"cash_count_line_ids":vals})
        return res
    
    @api.onchange('cash_count_line_ids')
    def onchange_ending_balance(self):
        total = sum(rec.cash_type_id.amount * rec.amount for rec in self.cash_count_line_ids)
        self.write({'balance_end_real': total})
        
    # Overide Function
    # Note: removed the code that changes the field date
    @api.depends('line_ids.internal_index', 'line_ids.state')
    def _compute_date_index(self):
        for stmt in self:
            try:
                sorted_lines = stmt.line_ids.sorted('internal_index')
                stmt.first_line_index = sorted_lines[:1]
            except:
                stmt.first_line_index = False
            # stmt.date = sorted_lines.filtered(lambda l: l.state == 'posted')[-1:].date
        
    def button_get_payments(self):
        self = self.sudo()
        journal_domain = [("date","=",self.date), ('journal_id','=',self.journal_id.id), ("state", "=", "posted")]
        self.line_ids = [(5,0,0)]
        account_payments = self.env["account.payment"].search(journal_domain)
        direct_payments = self.env["account.direct.payment"].search(journal_domain)
        for d in direct_payments:
            for a in i.line_ids:
                if d.direct_state == 'send':
                    amount_payment = -a.amount
                elif d.direct_state == 'receive':
                    amount_payment = a.amount
                    
                self.line_ids = [(0,0,{
                        'journal_id': d.journal_id.id,
						'date': d.date,
						'payment_ref' : a.name,
						'partner_id' : d.partner_id.id,
						'amount': amount_payment,
					})]
        for p in account_payments:
            if p.payment_type == 'outbound':
                amount_payment = -p.amount
            else:
                amount_payment = p.amount
            self.line_ids = [(0,0,{
                'journal_id': p.journal_id.id,
                'date': p.date,
                'payment_ref' : p.name,
                'partner_id' : p.partner_id.id,
                'amount': amount_payment,
            })]

class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    date = fields.Date('Date', default=fields.Date.today())
    
    def _prepare_statement_vals(self):
        res = super(AccountBankStatementImport, self)._prepare_statement_vals()
        res['date'] = self.date
        res['name'] = 'Statement Of ' + str(self.date)
        return res