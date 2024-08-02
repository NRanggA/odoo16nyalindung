# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from dateutil.rrule import rrule, YEARLY, MONTHLY, WEEKLY
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class MaintenanceEquipment(models.Model):
	_inherit = 'maintenance.equipment'

	unit_of_time = fields.Selection([
							(str(YEARLY), 'Years'),
							(str(MONTHLY), 'Months'),
							(str(WEEKLY), 'Weeks')], default=lambda x: str(YEARLY))
	employee_id = fields.Many2one('hr.employee', string='Employee', tracking=1)
	partner_id = fields.Many2one('res.partner', string='Partner', tracking=1, help='This is used to assigne equipment to non-employee partner')
	
	purchase_date = fields.Date(string="Purchase Date")
	warranty_period = fields.Integer(string="Warranty Period")
	warranty_expires_on = fields.Date(string="Warranty Expires on",compute="_get_date")
	main_product_id = fields.Many2one('product.product',string="Main Product")
	
	state = fields.Selection([('available','Available'),('not_available','Not Available')], default='available')
	allocation_count = fields.Integer(string="Allocation",compute='_get_allocation_count')
	count = fields.Integer(string="Number of ranges to generate", required=True,default=1)

	def _get_allocation_count(self):
		for equip in self:
			allocation_requests = self.env['allocation.request'].search([('equipment_id','=',equip.id)])
			equip.allocation_count = len(allocation_requests)

	@api.depends('purchase_date','warranty_period')
	def _get_date(self):
		for rec in self:
			vals = rrule(freq=int(rec.unit_of_time), 
						interval=rec.warranty_period,
						dtstart=rec.purchase_date,
						count=rec.count+1)
			vals = list(vals)
			if rec.warranty_period < 1:
				rec.update({'warranty_expires_on':rec.purchase_date})
			else:
				for idx, dt_start in enumerate(vals[:-1]):
					purchase_date = dt_start.date()
					warranty_expires_on = vals[idx+1].date() - relativedelta(days=1)
					rec.update({'warranty_expires_on':warranty_expires_on})

	def open_allocation_count(self):
		self.ensure_one()

		form_view_ref = self.env.ref('c10i_equipment_allocation.allocation_request_form_view', False)
		tree_view_ref = self.env.ref('c10i_equipment_allocation.allocation_request_tree_view', False)

		return {
			'name': _('Allocation Requests'),
			'view_mode': 'tree,form',
			'res_model': 'allocation.request',
			'type': 'ir.actions.act_window',
			'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
			'domain': [('equipment_id', 'in', self.ids)],
			'context': {
			}
		}