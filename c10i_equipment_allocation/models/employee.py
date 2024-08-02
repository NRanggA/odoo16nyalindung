# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

class Employee(models.Model):
	_inherit = 'hr.employee'

	equipment_count = fields.Integer('Equipments', compute='_compute_equipment_count', compute_sudo=True)

	def _compute_equipment_count(self):
		equipment_requests = self.env['maintenance.equipment'].search([('employee_id','=',self.id)])
		self.equipment_count = len(equipment_requests)