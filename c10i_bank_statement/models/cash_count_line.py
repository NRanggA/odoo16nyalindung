from odoo import _, api, fields, models

class CashCountLine(models.Model):
    _name = 'cash.count.line'
    _description = 'Cash Count Line'
    
    cash_type_id = fields.Many2one('cash.type', string='Cash Type')
    amount = fields.Integer('Amount')
    statement_id = fields.Many2one('account.bank.statement', string='Statement', ondelete='cascade')