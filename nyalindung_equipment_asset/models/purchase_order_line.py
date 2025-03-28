# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    equipment_category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')
    asset_type = fields.Selection(selection=[('lva','LVA'),('fa','FA')],compute='_compute_asset_type', string='Asset Type')

    qty_to_equip_register = fields.Float(compute='_compute_qty_received_eq', string='To Invoice Quantity', store=True, readonly=True,
                                            digits='Product Unit of Measure', compute_sudo=True)
    qty_registered = fields.Float(compute='_compute_qty_received_eq', string='Qty Registered', store=True, readonly=True,
                                            digits='Product Unit of Measure', compute_sudo=True)
    equipment_registered_status = fields.Selection([('no','Nothing to Register'),
        ('to_register', 'Need Equipment Register'),
        ('equipment_registered','Equipment Registered')], compute='_compute_equipment_register_status', store=True, compute_sudo=True)
	
    @api.depends('price_unit', 'product_id')
    def _compute_asset_type(self):
        for rec in self:
            if rec.product_id and rec.product_id.product_asset:
                threshold_param_to = rec.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_to', default=0.0)
                threshold_to = float(threshold_param_to) if threshold_param_to else 0.0
                rec.asset_type = 'lva' if  rec.price_unit <= threshold_to  else 'fa'
            else:
                rec.asset_type = False
    
    @api.depends('qty_received', 
            'equipment_register_line_ids.product_qty', 
            'equipment_register_line_ids.state',
            'asset_type')
    def _compute_qty_received_eq(self):
        for line in self:
            total_registered = 0.0
            threshold_param_from = self.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_from', default=0.0)
            if line.product_id.product_asset and line.price_unit >= (float(threshold_param_from) if threshold_param_from else 0):
                for lregis in line.equipment_register_line_ids.filtered(lambda l: l.product_id==line.product_id):
                    if lregis.state == 'done':
                        # total_registered = lregis.product_uom._compute_quantity(lregis.product_qty, line.product_uom, rounding_method='HALF-UP')
                        total_registered += lregis.product_uom._compute_quantity(lregis.product_qty, line.product_uom)
                line.qty_registered = total_registered
                line.qty_to_equip_register = line.qty_received - total_registered
            else:
                line.qty_registered = 0.0
                line.qty_to_equip_register = 0.0

    def _prepare_equipment_register_line(self):
        res = super()._prepare_equipment_register_line()
        res['category_id'] = self.equipment_category_id.id
        return res