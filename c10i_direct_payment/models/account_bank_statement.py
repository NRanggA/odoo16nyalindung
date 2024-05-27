from odoo import _, api, fields, models

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    # def write(self, values):
    #     print(">>>>>>>>>>>>>",values)
    #     if 'line_ids' in values and values['line_ids'][0][0] == 2:
    #         statementline_ids = self.env['account.bank.statement.line'].browse(values['line_ids'][0][1])
    #         # if statementline_ids:
                
            
    #     return super(AccountBankStatement,self).write(values)


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'


    direct_payment_move_id = fields.Many2one('account.move', string='Account Move From Direct Payment')
