from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"


    # def action_done(self):
        # res = super(StockPicking, self).action_done()
        # for picking in self:
        #     for move in picking.move_lines.filtered(lambda m: m.product_id.product_asset and m.state == 'done'):

        # return res

    