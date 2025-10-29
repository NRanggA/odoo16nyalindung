# # -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError

class EquipmentRegister(models.Model):
	_name = 'equipment.register'
	_description = "Equipment Register"
	_inherit = ["mail.thread", "mail.activity.mixin"]
	_order = 'date desc, id asc'

	name = fields.Char(string="Number", default="/")
	origin = fields.Char(string="Source Document")
	date = fields.Date(string="Register Date")
	state = fields.Selection([('draft', 'Draft'), 
					('confirm', 'Ready'), 
					('done', 'Registered'),
					('cancel', 'Cancelled')], string='State', default='draft')
	register_line_ids = fields.One2many('equipment.register.line', 'register_id', 'Register Lines')
	note = fields.Text(string="Note")
	equipment_count = fields.Integer(compute='_equipment_count', string="# Equipment")
	company_id = fields.Many2one('res.company', string='Company', ondelete='restrict', default=lambda s: s.env.company.id)

	def _equipment_count(self):
		for reg in self:
			reg.equipment_count = len(reg.register_line_ids.mapped('equipment_ids').ids)

	###################
	# ONCHANGE METHOD #
	###################

	####################
	# LOW-LEVEL METHOD #
	####################
	@api.model_create_multi
	def create(self, val_list):
		result = super(EquipmentRegister ,self).create(val_list)
		return result

	# def unlink(self):
	# 	for reg in self:
	# 		if reg.state not in ['cancel', 'draft']:
	# 			raise ValidationError("You can Only delete the Request(s) that are in 'New' or 'Cancelled' state !!!")
	# 	return super(EquipmentRegister,self).unlink()

	def unlink(self):
		raise ValidationError("You cannot delete this record, only can be cancelled.")

	###################
	# BUSINESS METHOD #
	###################
	def register_hook(self):
		# TO DO: please override this function if have something you want 
		# to modify before redirecting the result of equipment
		return True

	def action_confirm(self):
		for register in self:
			# seq.name = '{}-{}/DPKS/DIT.{}/{}'.format(res.type.upper(), self.env['ir.sequence'].next_by_code('bpdpks.spp'), res.operating_unit_id.code, year)
			register.name = self.env['ir.sequence'].next_by_code(self._name)
			register.state = 'confirm'

	def action_done(self):
		for register in self:
			if register.state!='confirm':
				raise ValidationError("You can only Approve equipment regsiter thar are now in 'Ready' state")
			
			equipments = self.env['maintenance.equipment']
			purchase_requests = self.env['purchase.request']
			for line in register.register_line_ids:
				equipments += line._create_equipment()
				if line.purchase_line_id.purchase_request_lines:
					for request in line.purchase_line_id.purchase_request_lines.mapped('request_id'):
						purchase_requests |= request

			if equipments and purchase_requests:
				for pr in purchase_requests:
					temp_dict = {}
					temp_main_product = equipments.mapped('main_product_id')
					for prl in pr.line_ids.filtered(lambda rl: rl.product_id and rl.product_id.product_asset):
						temp_equip = equipments.filtered(lambda e: e.main_product_id==prl.product_id)
						if not temp_equip:
							continue
						if prl.product_id not in temp_dict.keys():
							temp_dict.update({prl.product_id: []})
						for equip in temp_equip:
							temp_dict[prl.product_id].append(equip.serial_no)

					# if temp_dict:
					if False:
						display_approve_msg = """ Hello """ + pr.requested_by.name + """,""" + """
									  <br/>
									  <br/>
									  Your request for Asset has already been registered.
									  <br/>
									  Detail of Serial Number registered as stated below"""
						for p,sn in temp_dict.items():
							p_msg = """Product <b>""" + p.name + """<b> registered with Serial Number """ + ", ".join(sn) + """.<br/>"""
							display_approve_msg += p_msg
						pr.message_post(body=display_approve_msg)
			register.write({
				'state': 'done',
			})
			register.register_hook()
		return self.action_open_equipment(equipments=equipments)

	def action_cancel(self):
		for reg in self:
			for line in reg.register_line_ids:
				if line.equipment_ids:
					raise ValidationError("You can only Cancel This when the Equipment is not created yet. Please delete the Equipment first.")
		return self.write({'state':'cancel'})
	
	def action_draft(self):
		return self.write({'state':'draft'})

	def action_open_equipment(self, equipments=False):
		result = self.env["ir.actions.actions"]._for_xml_id('c10i_purchase_equipment.equipment_action_from_register')
		if not equipments:
			equipments = self.register_line_ids.mapped('equipment_ids')
		if not equipments or len(equipments) > 1:
			result['domain'] = [('id','in',equipments.ids)]
		elif len(equipments)==1:
			# result['domain'] = [('id','=',equipments.id)]
			result['views'] = [(self.env.ref('maintenance.hr_equipment_view_form', False).id, 'form')]
			result['res_id'] = equipments.id

		return result

class EquipmentRegisterLine(models.Model):
	_name = 'equipment.register.line'
	_description = "Equipment Register Lines"

	register_id = fields.Many2one('equipment.register', string="Reference", ondelete='cascade')
	product_id = fields.Many2one('product.product', string="Product", ondelete='restrict')
	name = fields.Char(string="Desription")
	product_uom = fields.Many2one('uom.uom', 'Unit of Measure', ondelete='restrict')
	product_qty = fields.Float('Quantity')
	purchase_line_id = fields.Many2one('purchase.order.line', string="Purchase Line")
	purchase_id = fields.Many2one(related='purchase_line_id.order_id', string="Purchase Order")
	equipment_ids = fields.One2many('maintenance.equipment', 'register_line_id', string='Equipments')
	state = fields.Selection([('draft', 'Draft'),
						('confirm', 'Ready'),
						('done', 'Registered'),
						('cancel', 'Cancel')], string='State', compute='_get_state', store=True)

	@api.depends('register_id.state')
	def _get_state(self):
		for line in self:
			line.state = line.register_id.state

	#################
	# HELPER METHOD #
	#################
	def _prepare_equipment_vals(self):
		serial_no = self.env['ir.sequence'].next_by_code('maintenance.equipment')
		res = {
			'main_product_id': self.product_id.id,
			'register_line_id': self.id,
			'name': self.product_id.name,
			'note': self.name,
			'purchase_date': self.register_id.date,
			'effective_date': self.register_id.date,
			'category_id': False,
			'partner_id': self.purchase_line_id.order_id.partner_id.id,
			'partner_ref': self.purchase_line_id.order_id.partner_ref,
			'serial_no': serial_no, #harusnya diisi serial aktualnya, atau diganti dengan sequence
			'cost': self.purchase_line_id.price_unit

			# 'barcode': '/', #diisi dari sequence dlu
		}
		return res

	def _create_equipment(self):
		Equipment = self.env['maintenance.equipment']
		equipments = self.env['maintenance.equipment']
		for line in self.filtered(lambda r: r.product_id.product_asset):
			for i in range(int(line.product_qty)):
				equipment_vals = line._prepare_equipment_vals()
				new_equipment = Equipment.create(equipment_vals)
				# new_equipment.message_post_with_view('mail.message_origin_link',
				# 		values={'self': picking, 'origin': order},
				# 		subtype_id=self.env.ref('mail.mt_note').id)
				equipments |= new_equipment
		return equipments