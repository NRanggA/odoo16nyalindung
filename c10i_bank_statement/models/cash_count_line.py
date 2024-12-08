from odoo import _, api, fields, models

class CashCountLine(models.Model):
    _name = 'cash.count.line'
    _description = 'Cash Count Line'
    
    cash_type_id = fields.Many2one('cash.type', string='Cash Type')
    amount = fields.Integer('Amount')
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.company.currency_id)
    total = fields.Monetary(compute='_compute_total', string='Total',currency_field="currency_id")
    statement_id = fields.Many2one('account.bank.statement', string='Statement', ondelete='cascade')

    @api.depends('cash_type_id.amount','amount')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.cash_type_id.amount * rec.amount