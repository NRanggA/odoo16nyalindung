# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError

class Payment(models.Model):
    _inherit = "account.payment"

    expense_payment_id = fields.Many2one('account.direct.payment', string='Expense Payment', ondelete='restrict')