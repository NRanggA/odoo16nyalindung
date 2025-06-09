from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

class lhm_transaction_material_line(models.Model):
    _inherit = 'lhm.transaction.material.line'

    from_mobile_apps = fields.Boolean(string="From Mobile Apps")

    @api.depends('realization')
    def _get_residual(self):
        line_from_mobile_apps = self.filtered(lambda l: l.from_mobile_apps)
        for line in line_from_mobile_apps:
            # residual = line.real_stock_qty - line.stock_qty - line.realization
            line.residual_qty = 0.0
        super(lhm_transaction_material_line, self - line_from_mobile_apps)._get_residual()