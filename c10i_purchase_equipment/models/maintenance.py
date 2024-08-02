# # -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError

class MaintenanceEquipment(models.Model):
	_inherit = 'maintenance.equipment'

	register_line_id = fields.Many2one('equipment.register.line', string="Register Line", ondelete='restrict')
	register_id = fields.Many2one(related='register_line_id.register_id', string="Equipment Register", store=True)
