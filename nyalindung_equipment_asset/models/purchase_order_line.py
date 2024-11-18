# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    equipment_category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')
    asset_type = fields.Selection(selection=[('lva','LVA'),('fa','FA')],compute='_compute_asset_type', string='Asset Type',precompute=True)
	
    @api.depends('price_unit')
    def _compute_asset_type(self):
        for rec in self:
            threshold_param_to = rec.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_to', default=0.0)
            threshold_to = float(threshold_param_to) if threshold_param_to else 0.0
            rec.asset_type = 'lva' if  rec.price_unit <= threshold_to  else 'fa'
            
            

    def _prepare_equipment_register_line(self):
        res = super()._prepare_equipment_register_line()
        res['category_id'] = self.equipment_category_id.id
        return res