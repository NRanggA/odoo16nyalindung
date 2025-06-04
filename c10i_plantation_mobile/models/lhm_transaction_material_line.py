from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

class lhm_transaction_material_line(models.Model):
    _inherit = 'lhm.transaction.material.line'

    from_mobile_apps = fields.Boolean(string="From Mobile Apps")