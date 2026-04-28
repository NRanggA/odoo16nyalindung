from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

class LhmContractor(models.Model):
    _inherit = 'lhm.contractor'

    payment_type = fields.Selection(selection_add=[('custom','Custom Range')], default='custom', ondelete={'custom': 'set default'})
    spk_number = fields.Char()
    origin = fields.Char(string="Origin")