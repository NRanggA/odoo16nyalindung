from odoo import _, api, fields, models

class CashType(models.Model):
    _name = 'cash.type'
    _description = 'Cash Type'
    
    name = fields.Char('Name')
    image = fields.Binary('Image')
    amount = fields.Float('Amount')
    