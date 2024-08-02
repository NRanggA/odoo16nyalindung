# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime,date

class ButtonApprove(models.TransientModel):
	_name = 'button.approve'
	_description = "Button Approve"

	note = fields.Char(string="TEXT", default="""This equipment is currently 
											  approved for another Employee.
											  <br/>
											  <b>Note :</b> You cannot allocate
											  the same equipment to multiple 
											  requests.
											  <br/>
											  So, If you want to <b>Cancel</b> 
											  the previous approved request and 
											  create the <b>New </b>requests
											  then click on <b>"Update Now "</b> 
											  button else click on <b>"Cancel".</b>""")
	prev_request_ids = fields.Many2many('allocation.request')

	def update_equipment(self):
		active_ids = self.env['allocation.request'].browse(self.env.context.get('active_id'))
		for request in active_ids:
			display_cancel_msg=""" Hello """ + request.assigned_id.name + """,""" + """
						<br/>
						<br/>
						Your allocation request for a set of """+ """<b>"""+request.equipment_id.name+"""</b>"""+"""/"""+"""<b>"""+request.equipment_id.serial_no +"""</b>""" +"""
						has been cancelled.""" + """
						<br/>
						<br/>
						<b>Reason</b> for cancelling this request is stated below:
						</br>
						</br>""" + """<br/>""" + """Force Approved new request while cancelling this Request."""
			self.prev_request_ids.message_post(body=display_cancel_msg)
			self.prev_request_ids.write({
				'state':'cancel',
				'cancelled_by':self.env.user.id})
			request.write({'state':'approved',
				'approved_by': self.env.user.id,
				})
			request.equipment_id.write({
				'state' : 'available',
				'employee_id': False,
				})




