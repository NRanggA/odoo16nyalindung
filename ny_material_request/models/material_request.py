from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import ValidationError, UserError
from itertools import groupby


class StockMove(models.Model):
    _inherit = 'stock.move'

    requested_by = fields.Many2one('res.users', string='Requested by')

class MaterialRequest(models.Model):
    _inherit = "material.request"

    def _create_picking(self):
        super(MaterialRequest, self)._create_picking()
        StockPicking = self.env['stock.picking']
        for request in self.filtered(lambda mr: mr.state == 'approved'):
            if any((product.type == 'product' and not product.product_asset) for product in request.line_ids.product_id):
                request = request.with_company(request.company_id)
                for user in request.line_ids.requested_by:
                    res = request._prepare_picking()
                    res.update({"partner_id": user.partner_id.id})
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                    for mrlines in request.line_ids:
                        if user == mrlines.requested_by:
                            moves = mrlines._create_stock_moves(picking)
                            moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                            picking.message_post_with_view('mail.message_origin_link',
                                values={'self': picking, 'origin': request},
                                subtype_id=self.env.ref('mail.mt_note').id)
        return True

class MaterialRequestLine(models.Model):
    _inherit = "material.request.line"

    requested_by = fields.Many2one("res.users", string="Requested by")
    product_asset = fields.Boolean(related='product_id.product_asset', string='Asset Equipment')

    

    #         # Override material.request _create_picking
    # def _create_picking(self):
    #     StockPicking = self.env['stock.picking']
    #     # print(".........................1", StockPicking)
    #     # print(".........................2", self) # material.request(17,)
    #     # print(".........................21", self.description) # material.request(17,18,19)
    #     # print(".........................22", self.picking_type_id) # stock.picking.type(19,)
    #     # print(".........................23", self.picking_type_id.name) # material.request(17,18,19)
    #     # print(".........................23", self.picking_type_id.default_location_src_id) # material.request(17,18,19)
    #     # print(".........................24", self.line_ids) # material.request.line(15,16)
    #     # print(".........................25", self.line_ids.requested_by) # res.user(7, 2)
    #     # # print(".........................25", self.line_ids.name) # material.request.line(17,18,19)
    #     # for x in self.line_ids.requested_by:
    #     #     print(".........................251", x.name ) # material.request(17,18,19)
    #     # # print(".........................25", self.line_ids.requested_by.name) # material.request(17,18,19)
    #     # xx = self.filtered(lambda mr: mr.state=='approved')
    #     # print(".........................3", xx)
    #     for request in self.filtered(lambda mr: mr.state=='approved'):
    #         # print(",,,,,,,,,,,,,,,,,,,,,26", [(product.type=='product' and not product.product_asset) for product in request.line_ids.product_id])
    #         # print("............. 28",request.line_ids.product_id)
    #         # temp = []
    #         # for product in request.line_ids.product_id:
    #         #     if product.type=='product' and not product.product_asset:
    #         #         temp.append(True)
    #         #     else:
    #         #         temp.append(False)
    #         # print("............. 29",temp)
            
    #         if any((product.type=='product' and not product.product_asset) for product in request.line_ids.product_id):
    #             request = request.with_company(request.company_id) #konteks
    #             # print("............. 30", request) #isinya self
    #             res = request._prepare_picking()
    #             # print("............. 31", res) #isinya dictionary/object
    #             picking = StockPicking.with_user(SUPERUSER_ID).create(res)
    #             # print("............. 32", picking.move_ids) # apalah
    #             moves = request.line_ids._create_stock_moves(picking)
    #             # print("............. 33", moves) # apalah
    #             # print("............. 34", picking.move_ids) # apalah
    #             moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
    #             # moves._action_assign()
    #             picking.message_post_with_view('mail.message_origin_link',
    #                 values={'self': picking, 'origin': request},
    #                 subtype_id=self.env.ref('mail.mt_note').id)
    #     # print(".........................", asd)
    #     return True