# # -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

class MaterialRequest(models.Model):
    _inherit = 'material.request'

    equip_allocation_count = fields.Integer(compute='_equip_allocation_count', string='# Equipment Allocation', compute_sudo=True)

    def _equip_allocation_count(self):
        for request in self:
            request.equip_allocation_count = len(request.line_ids.mapped('allocation_request_ids').ids)

    # Override material.request _create_picking
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for request in self.filtered(lambda mr: mr.state=='approved'):
            if any((product.type=='product' and not product.product_asset) for product in request.line_ids.product_id):
                request = request.with_company(request.company_id)
                res = request._prepare_picking()
                picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                moves = request.line_ids._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                # print("----------------", moves)
                # print("---------------", stop)
                # moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': request},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

    def account_view_allocation_request(self):
        self.ensure_one()
        
        form_view_ref = self.env.ref('c10i_material_request_equipment_allocation.material_request_allocation_request_form_readonly', False)
        tree_view_ref = self.env.ref('c10i_material_request_equipment_allocation.material_request_allocation_request_tree', False)

        equipment_allocation_requests = self.line_ids.mapped('allocation_request_ids')
        if len(equipment_allocation_requests)>1:
            domain = [('id','in',equipment_allocation_requests.ids)]
        else:
            domain = [('id','=',equipment_allocation_requests.id)]

        return {
            'name': _('Allocation Requests'),
            'view_mode': 'tree,form',
            'res_model': 'allocation.request',
            'type': 'ir.actions.act_window',
            'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
            'domain': domain,
            'context': {}
        }

class MaterialRequestLine(models.Model):
    _inherit = 'material.request.line'

    product_asset = fields.Boolean(related='product_id.product_asset', string='Asset Equipment')
    allocation_request_ids = fields.One2many('allocation.request', 'mr_line_id', 'Equipment Allocation Requests')

    # @api.depends('product_id', 'product_asset')
    # def _compute_qty_issued_method(self):
    #     product_not_asset = self.filtered(lambda x: not x.product_asset)
    #     super(MaterialRequestLine, self - product_not_asset)._compute_qty_issued_method()
    #     for line in self:
    #         line.qty_issued_method = 'manual'

    @api.depends(
        'product_id', 
        'product_qty', 
        'uom_id',
        'mr_id.state', 
        'move_ids.state',
        'allocation_request_ids.state')
    def _compute_qty_issued(self):
        product_asset = self.filtered(lambda x: x.product_asset)
        super(MaterialRequestLine, self - product_asset)._compute_qty_issued()
        for line in product_asset:
            if line.mr_id.state=='done':
                continue
            qty_done = qty_to_issue = 0.0
            if line.mr_id.state!='approved':
                line.qty_done = qty_done
                line.qty_to_issue = qty_to_issue
                continue
            allocated = line.allocation_request_ids.filtered(lambda a: a.state=='allocated')
            print('aaaaaaaaaaaa', allocated)
            if allocated:
                qty_done = len(allocated.mapped('equipment_id'))

            line.qty_done = qty_done
            qty_to_issue = line.product_qty - qty_done
            line.qty_to_issue = qty_to_issue if qty_to_issue > 0.0 else 0.0

    # Override material.request.line _create_stock_moves
    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            if line.product_id.type!='product' or line.product_asset:
                continue
            if float_compare(line.product_qty, 0.0, precision_rounding=line.uom_id.rounding) > 0:
                product_uom_qty, product_uom = line.uom_id._adjust_uom_quantities(line.product_qty, line.product_id.uom_id)
                values.append(line._prepare_stock_move_vals(picking, product_uom_qty, product_uom))
                # print('----------------', values)
                # print('----------------', cimolgans)
        return self.env['stock.move'].create(values)

    def create_equipment_allocation(self):
        self.ensure_one()
        if not self.product_asset:
            raise UserError(_("It must be Equipment Product if you want to create Equipment Allocation"))
        
        form_view_ref = self.env.ref('c10i_material_request_equipment_allocation.material_request_allocation_request_form', False)
        return {
            'name': _('Allocation Requests'),
            'view_mode': 'form',
            'res_model': 'allocation.request',
            'type': 'ir.actions.act_window',
            'views': [(form_view_ref.id, 'form')],
            'context': {
                'default_name': f"Request {self.name}",
                'default_mr_line_id': self.id,
                'default_mr_product_id': self.product_id.id,
                'default_assigned_id': self.mr_id.requested_by.employee_id.id,
            }
        }