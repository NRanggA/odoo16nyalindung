from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _prepare_data_cash_statement(self):
        res = {
            'journal_id': self.journal_id.id,
            'date': self.date,
            'company_id': self.env.user.company_id.id,
            'line_ids': []

        }
        
        return res
    
    def _prepare_data_line_cash_statement(self):

        res = {
            'date': self.date,
            'direct_payment_move_id': self.id,
            'partner_id': self.partner_id.id,
            'amount': self.amount_total_signed,
            'payment_ref': self.payment_id.name or self.name,

        }

        return res

    def _post(self, soft=True):
        res = super(AccountMove,self)._post(soft=True)
        if self.journal_id.create_cash_register:
            cash_statement ={}
            cashregister = self.env['account.bank.statement']
            cash_statement_id =  cashregister.search([('journal_id', '=', self.journal_id.id),('date', '=', fields.Date.today())])
            line_ids = self._prepare_data_line_cash_statement()
            if cash_statement_id:
                cash_statement_id.write({'line_ids': [(0,0,line_ids)]})
            else:
                cash_statement = self._prepare_data_cash_statement()
                cash_statement['line_ids'] = self._prepare_data_line_cash_statement()
                cashregister.create(cash_statement)
        return res
    
    def button_draft(self):
        res = super(AccountMove,self).button_draft()

        if self.journal_id.create_cash_register:
            
            cashregister = self.env['account.bank.statement.line'].search([('date', '=', self.date),('direct_payment_move_id', '=', self.id)])
            if cashregister:

                # move_id = cashregister.move_id
                for cash_statement_id in cashregister:
                    statement_id = cash_statement_id.statement_id
                
                    statement_id.write({'line_ids':[(2,cash_statement_id.id,0)]})


        return res
