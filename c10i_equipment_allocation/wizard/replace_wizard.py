# -*- coding: utf-8 -*-
 
from odoo import models, fields, api,_
from datetime import datetime,date

class ReplaceButton(models.TransientModel):
	_name = 'replace.button'
	_description = "Replace Button"

	category_id=fields.Many2one('maintenance.equipment.category',string="Category")
	equipment_id=fields.Many2one('maintenance.equipment',string="Equipment")
	reason=fields.Text(string="Reason")

	@api.onchange('category_id')
	def _onchange_replace_product(self):
		for replace in self:
			return{'domain':{'equipment_id':[('category_id','=',replace.category_id.name)]}}

	@api.model
	def default_get(self,fields):
		records=super(ReplaceButton,self).default_get(fields)
		context=dict(self._context or {})
		active_id=self.env['allocation.request'].browse(context['active_ids'])
		store=[]
		length=len(active_id.category_id)
		records.update({'category_id':active_id.category_id.id})
		return records

	def replace_equipment(self):
		temp=[]
		for equipment in self:
			active_id = self.env['allocation.request'].browse(self.env.context.get('active_id'))
			old_id=active_id.equipment_id
			old_serial_no=active_id.equipment_id.serial_no
			active_id.write({'equipment_id':equipment.equipment_id.id})
			maintanance_active_id=self.env['maintenance.equipment'].search([('id','!=',self.equipment_id.ids)])
			maintanance_active_id.write({'state':'available'})
			main_active_id=self.env['maintenance.equipment'].search([('id','=',self.equipment_id.ids)])
			main_active_id.write({'state':'not_available'})
			new_active_id=self.env['maintenance.equipment'].search([('id','=',self.equipment_id.id)])
			old_active_id=self.env['maintenance.equipment'].search([('id','=',old_id.id)])
			old_active_id.write({'employee_id':False})
			allocation_active_id=self.env['allocation.request'].browse(self.env.context.get('active_id'))
			new_active_id.write({'employee_id':allocation_active_id.assigned_id.id})

			display_replace_now_msg=""" Hello """ + active_id.assigned_id.name + """,""" + """
									<br/>
									<br/>
									Your previous equipment """ + old_id.name + """/""" + old_serial_no + """
									has been replaced by an another Equipment named """ + active_id.equipment_id.name + """/""" + active_id.equipment_id.serial_no + """
									. Now, """ + active_id.equipment_id.name + """/""" + active_id.equipment_id.serial_no + """ 
									 is assigned to you on the permanent basis.
									 <br/>
									 <br/>
									 <b> Reason </b> for replacing equipment is
									 <br/> """ + self.reason
			active_id.message_post(body=display_replace_now_msg)



