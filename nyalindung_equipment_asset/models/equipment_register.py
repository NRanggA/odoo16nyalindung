from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class EquipmentRegister(models.Model):
	_inherit = 'equipment.register'
	_order = 'id desc'

	lva_threshold = fields.Boolean('LVA', compute='get_lva_threshold')
	move_ids = fields.One2many('account.move', 'equip_register_id', string='Move')
	count_move = fields.Integer('Count Move', compute='_get_count_move_equip')

	@api.depends()
	def get_lva_threshold(self):
		for record in self:
			threshold_param_from = self.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_from', default=0.0)
			threshold_param_to = self.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_to', default=0.0)
			threshold_from = float(threshold_param_from) if threshold_param_from else 0.0
			threshold_to = float(threshold_param_to) if threshold_param_to else 0.0
			record.lva_threshold = bool(any((line.purchase_line_id.price_unit >= threshold_from and line.purchase_line_id.price_unit <= threshold_to) for line in record.register_line_ids))
	
	def _get_count_move_equip(self):
		for record in self:
			record.count_move = len(record.move_ids)
	
	def create_lva_journal(self):
		for register in self:
			for line in register.register_line_ids:
				if not line.account_id:
					raise ValidationError("Account Expense Belum Diisi")
				
				product_accounts = line.product_id.product_tmpl_id.get_product_accounts()
				stock_journal = product_accounts.get('stock_journal')
            
				if not stock_journal:
					raise ValidationError("Stock Journal not found for the product.")
				
				move_lines = []
				move_vals = {
					'journal_id': stock_journal.id,
					'date': register.date,
					'equip_register_id': register.id,
				}

				# amount = line.purchase_line_id.price_unit * line.purchase_line_id.product_qty
				amount = line.purchase_line_id.price_unit # TODO : musti pertimbangkan juga harga ppn tidak dikreditkan
				# debit_lines
				move_line_vals_asset = {
					'account_id': line.account_id.id,
					'name': 'Reclass Asset to SPM',
					'debit': amount,
					'credit': 0.0,
				}
				move_lines.append((0, 0, move_line_vals_asset))
				# credit_lines
				credit_account = line.product_id.categ_id.asset_clearing_account_id
				move_line_vals = {
					'account_id': credit_account.id,
					'name': 'Reclass SPM to Asset',
					'credit': amount,
					'debit': 0.0,
				}
				move_lines.append((0, 0, move_line_vals))
				# create move
				move_vals.update({'line_ids': move_lines})
				new_move = self.env['account.move'].create(move_vals)
				new_move._post()

		return True
	
	def action_open_move(self):
		result = self.env["ir.actions.actions"]._for_xml_id('account.action_move_line_form')
		move_ids = self.move_ids

		if not move_ids or len(move_ids) > 1:
			result['domain'] = "[('id','in',%s)]" % (move_ids.ids)
		elif len(move_ids)==1:
			result['domain'] = "[('id','=',%s)]" % (move_ids.id)

		return result

	def action_done(self):
		for register in self:			
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
							temp_dict[prl.product_id].append(equip.seq_no)

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
			if register.lva_threshold:
				register.create_lva_journal()
			
		return self.action_open_equipment(equipments=equipments)
		
class EquipmentRegisterLine(models.Model):
	_inherit = 'equipment.register.line'
	location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
	location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
	activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
	doc_activity_ids    = fields.Many2many('lhm.activity', compute='_filtered_doc_activity_ids')
	account_id          = fields.Many2one('account.account', string='Account', compute='_get_account_clearing')
	category_id         = fields.Many2one('maintenance.equipment.category', string="Equipment Category", ondelete="restrict")
	
	
	@api.depends('location_type_id','location_id')
	def _filtered_doc_activity_ids(self):
		for line in self:
			if not line.location_type_id:
				line.doc_activity_ids = []
				continue
			activity_ids = []
			if line.location_type_id.code=='PJ' and line.location_id:
				current_project = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
				activity_ids = current_project.line_ids.mapped('activity_id').ids if current_project else []
			else:
				activity_ids = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)]).ids
				
			line.doc_activity_ids = [(6, 0, activity_ids)]

	def _get_account_clearing(self):
		for record in self:
			if record.product_id:
				product_expense = record.product_id.property_account_expense_id.id
				product_categ_expense = record.product_id.categ_id.property_account_expense_categ_id.id
				record.account_id = product_expense or product_categ_expense or None

	#################
	# HELPER METHOD #
	#################
	def _prepare_equipment_vals(self):
		seq_code = self.category_id.sequence_id.code
		serial_no = self.env['ir.sequence'].next_by_code(seq_code)
				
		threshold_param_to = self.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_to', default=0.0)
		threshold_to = float(threshold_param_to) if threshold_param_to else 0.0
		asset_type = 'lva' if self.purchase_line_id.price_unit <= threshold_to  else 'fa'
		
		res = {
            # 'category_id' : self.register_id.category_id.id,
            'equipment_assign_to' : self.register_id.equipment_assign_to,
            'department_id' : self.register_id.department_id.id,
            'employee_id' : self.register_id.employee_id.id,
            'location' : self.register_id.location,
            'warranty_period' : self.register_id.warranty_period,
            'unit_of_time' : self.register_id.unit_of_time,
            'partner_id' : self.register_id.partner_id.id,
            'partner_ref' : self.register_id.partner_ref,
            'model' : self.register_id.model,
            'serial_no' : self.register_id.serial_no,
			'main_product_id': self.product_id.id,
			'register_line_id': self.id,
			'name': self.product_id.name,
			'note': self.name,
			'purchase_date': self.register_id.date,
			'effective_date': self.register_id.date,
			'category_id': self.category_id.id,
			'partner_id': self.purchase_line_id.order_id.partner_id.id,
			'partner_ref': self.purchase_line_id.order_id.partner_ref,
			'seq_no': serial_no,
			'cost': self.purchase_line_id.price_unit,
			'asset_type' : asset_type

			# 'barcode': '/', #diisi dari sequence dlu
		}
		return res