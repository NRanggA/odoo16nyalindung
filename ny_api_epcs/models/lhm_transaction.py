from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

class LhmTransaction(models.Model):
    _inherit = 'lhm.transaction'

    origin = fields.Char(string="Origin")