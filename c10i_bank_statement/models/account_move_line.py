from odoo import _, api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self):
        account_type = self.mapped('account_id.account_type')
        bank_cash = self.filtered_domain([('move_id.journal_id.type','in',['bank','cash']), ('statement_line_id','!=',False)])
        statement_line = bank_cash.move_id.statement_line_id
        receivable = self.filtered_domain([('move_id.journal_id.type','=', 'sale')])
        if 'asset_receivable' in account_type and bank_cash:
            payment = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_id': bank_cash.partner_id.id,
                'amount': bank_cash.credit,
                'ref': receivable.name,
                'journal_id': bank_cash.move_id.journal_id.id,
            })
            payment.action_post()
            outstanding_payment = payment.move_id.line_ids.filtered_domain([('account_id.account_type','!=', 'asset_receivable')])
            outstanding_statement = receivable
            outstanding_statement.write({
                'date_maturity': False,
                'account_id': outstanding_payment.account_id.id,
            })
            # self.env.cr.execute("""UPDATE account_move_line set account_id=%s where id=%s""" % (outstanding_payment.account_id.id, outstanding_statement.id))
            # outstanding_statement.account_id = outstanding_payment.account_id.id
            payment_to_reconcile = payment.move_id.line_ids.filtered_domain([('account_id.account_type','=', 'asset_receivable')])
            reconciled_payment = payment_to_reconcile + receivable
            reconciled_payment.reconcile()
        return super(AccountMoveLine, self).reconcile()    