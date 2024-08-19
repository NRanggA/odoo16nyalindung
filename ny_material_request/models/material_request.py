from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import ValidationError, UserError


class MaterialRequestLine(models.Model):
    _inherit = "material.request.line"

    requested_by = fields.Many2one("res.users", string="Requested by")
    product_asset = fields.Boolean(related='product_id.product_asset', string='Asset Equipment')


    def _create_picking(self):
        requested_by = super()._create_picking()

        if 'Requested By' in self.requested_by > 1 :
            self.requested_by = self.name

        return requested_by