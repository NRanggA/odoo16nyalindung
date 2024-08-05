# # -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError

class AllocationRequest(models.Model):
	_name = 'allocation.request'
	_description = "Allocation Request"
	_inherit = ["mail.thread", "mail.activity.mixin"]
	_order = 'scheduled_date desc, id asc'

	name = fields.Char(string="Subject" ,required=True, translate=True)
	allocation_type = fields.Selection([('on_demand','On-demand'),('permanent','Permanent')], default='on_demand')
	category_id = fields.Many2one('maintenance.equipment.category', string="Category")
	equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")
	product = fields.Many2one('product.product', string="Product", related='equipment_id.main_product_id')
	scheduled_date = fields.Date(string="Scheduled Date", default=fields.Datetime.now)
	priority = fields.Selection([('0', 'Very Low'), 
								 ('1', 'Low'), 
								 ('2', 'Normal'), 
								 ('3', 'High')], string='Priority')
	note = fields.Text(string="Note")
	# assigned_id = fields.Many2one('res.users', string="Assigned To", default=lambda self: self.env.user and self.env.user.id or False)
	assigned_contact_type = fields.Selection([('employee','Employee'),('partner','Partner')], string='Assigned Contact Type', default='employee')
	assigned_id = fields.Many2one('hr.employee', string="Assigned To", default=lambda self: self.env.user.employee_id)
	assigned_partner_id = fields.Many2one('res.partner', string="Assigned To")
	state = fields.Selection([('new','New'),
							('submitted','Submitted'),
							('approved','Approved'),
							('allocated','Allocated'),
							('returned','Returned'),
							('rejected','Rejected'),
							('cancel','Cancelled')], default='new',tracking=3)
	approved_by = fields.Many2one('res.users', string="Approved By")
	cancelled_by = fields.Many2one('res.users', string="Cancelled By")
	rejected_by = fields.Many2one('res.users', string="Rejected By")
	created_by = fields.Many2one('res.users', string="Created By",default=lambda self: self.env.user and self.env.user.id or False)
	created_date = fields.Datetime(string="Created Date",default=fields.Datetime.now)
	return_to = fields.Many2one('res.users',string="Return To")
	return_date = fields.Datetime(string="Return Date",default=fields.Datetime.now)

	@api.onchange('equipment_id')
	def onchange_main_product(self):
		store=[]
		active_id=self.env['maintenance.equipment'].search([])
		for temp in active_id:
			if temp == self.equipment_id:
				store.append((0,0,{
						'main_product_id':temp.main_product_id.name
						}))
				self.update({'product':temp.main_product_id})

	def action_submit(self):
		self.state = 'submitted'

	def action_approve(self):
		for request in self:
			if not request.equipment_id:
				raise ValidationError("You have not selected Equipment, please select the Equipment First.")

			other_request = self.search([('equipment_id','=',request.equipment_id.id), ('state','in',['approved','allocated'])])
			if other_request:
				return {
					'type':'ir.actions.act_window',
					'name':'Message',
					'res_model':'button.approve',
					'view_mode':'form',
					'context': {'default_prev_request_ids': [(4,other_request.id)]},
					'target':'new',
				}

			if request.assigned_id:
				assigned_name = request.assigned_id.name
			elif request.assigned_partner_id:
				assigned_name = request.request.assigned_partner_id.name
			else:
				raise ValidationError("You have not selected Assigned Person")
			display_approve_msg = """ Hello """ + assigned_name + """,""" + """
						  <br/>
						  <br/>
						  Your request for a set of """+ request.equipment_id.name +"""/""" +request.equipment_id.serial_no + """ 
						  on given scheduled date which is """ + request.scheduled_date.strftime('%d/%m/%Y') +"""
						  has been approved."""
			request.message_post(body=display_approve_msg)
			request.write({
				'state': 'approved',
				'approved_by': self.env.user.id,
			})
		return True

	def action_allocate(self):
		for request in self:
			if request.assigned_id:
				assigned_name = request.assigned_id.name
			elif request.assigned_partner_id:
				assigned_name = request.assigned_partner_id.name
			else:
				raise ValidationError("You have not selected Assigned Person")
			if request.allocation_type == 'on_demand':
				display_allocated_msg=""" Hello """ + assigned_name + """,""" + """
									<br/>
									<br/>
									""" + request.equipment_id.name + """/""" + request.equipment_id.serial_no +"""
									has been allocated to you as per your request."""
				request.message_post(body=display_allocated_msg)
			else:
				display_allocated_message=""" Hello """ + assigned_name + """,""" + """
										<br/>
										<br/>
										We have assigned you an equipment named """ + request.equipment_id.name + """/""" + request.equipment_id.serial_no +"""
										on permanent basis."""
				request.message_post(body=display_allocated_message)
			request.state = 'allocated'
			request.equipment_id.write({
				'employee_id': request.assigned_id.id if request.assigned_contact_type=='employee' else False,
				'partner_id': request.assigned_partner_id.id if request.assigned_contact_type=='partner' else False,
				'assign_date': fields.Date.context_today(self),
				'state': 'not_available'
			})
		return True

	def confirm_return(self):
		for request in self:
			request.write({
				'state':'returned', 
				'return_to': self.env.user.id
			})
			request.equipment_id.write({
				'employee_id' : False,
				'assign_date': False,
				'partner_id': False,
				'state': 'available'
				})

	def set_to_new(self):
		return self.write({'state':'new'})

	def unlink(self):
		for state in self:
			if state.state not in ['cancel', 'new']:
				raise ValidationError("You can Only delete the Request(s) that are in 'New' or 'Cancelled' state !!!")
		return super(AllocationRequest,self).unlink()

	@api.model
	def create(self, val):
		result = super(AllocationRequest ,self).create(val)
		if result.assigned_id:
			assigned_name = result.assigned_id.name
		elif result.assigned_partner_id:
			assigned_name = result.assigned_partner_id.name
		else:
			raise ValidationError("You have not selected Assigned Person")
		display_creation_msg=""" Hello, """ + """<br/><br/>An allocation request has been created 
								for a set of """ + """<b>""" + result.equipment_id.name + """/""" + result.equipment_id.serial_no + """</b>""" + """ by
								""" + """<b>""" + assigned_name + """
								(Management) </b> for the scheduled date 
								""" + """<b>""" + result.scheduled_date.strftime('%d/%m/%Y') + """.
								</b>"""
		result.message_post(body=display_creation_msg)
		return result