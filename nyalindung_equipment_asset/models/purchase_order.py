# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def action_create_equipment_register(self):
        for order_line in self.order_line:
            if order_line.equipment_registered_status in ('to_register','equipment_registered') and not order_line.equipment_category_id:
                raise ValidationError("Please fill in the Equipment Category field for Product %s before proceeding."%(order_line.product_id.name))
                
        return super().action_create_equipment_register()

