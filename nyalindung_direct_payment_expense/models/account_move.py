from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = 'account.move'


    employee_expense_id = fields.Many2one('account.direct.payment', string='Employee Expense')