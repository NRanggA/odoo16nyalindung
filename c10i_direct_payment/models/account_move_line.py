# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    expense_payment_line_id = fields.Many2one('account.direct.payment.line', string='Expense Payment Line', copy=False, help="Expense where the move line come from")
