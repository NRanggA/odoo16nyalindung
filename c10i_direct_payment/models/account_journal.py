from odoo import _, api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    create_cash_register = fields.Boolean('Create Cash Register')
