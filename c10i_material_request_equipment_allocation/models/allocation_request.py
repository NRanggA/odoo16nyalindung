# # -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError

class AllocationRequest(models.Model):
    _inherit = 'allocation.request'

    mr_product_id = fields.Many2one('product.product', string="Product", copy=False)
    mr_line_id = fields.Many2one('material.request.line', string='Material Request Line', copy=False)
    mr_id = fields.Many2one(related='mr_line_id.mr_id', string='Material Request', store=True)

    @api.onchange('equipment_id')
    def onchange_equipment(self):
        if self.mr_line_id and self.equipment_id:
            self.category_id = self.equipment_id.category_id.id