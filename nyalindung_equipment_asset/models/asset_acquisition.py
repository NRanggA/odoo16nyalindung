from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AssetAcquisition(models.Model):
	_inherit = 'account.asset.acquisition'
	
	equipment_id = fields.Many2one('maintenance.equipment', string="Equipment ID")
	state = fields.Selection([('draft', 'Draft'), 
					('done', 'Registered'),
					('cancel', 'Cancelled'),
					('reject', 'Rejected'),
					], string='State', default='draft')
	move_ids = fields.One2many('account.move', 'acquisition_id', string='Move')
	count_move = fields.Integer('Count Move', compute='_get_count_move_equip')

	def _get_count_move_equip(self):
		for record in self:
			record.count_move = len(record.move_ids)

	def action_open_move_acquisition(self):
		result = self.env["ir.actions.actions"]._for_xml_id('account.action_move_line_form')
		move_ids = self.move_ids

		if not move_ids or len(move_ids) > 1:
			result['domain'] = "[('id','in',%s)]" % (move_ids.ids)
		elif len(move_ids)==1:
			result['domain'] = "[('id','=',%s)]" % (move_ids.id)

		return result
	
	def action_submit(self):
		for acquisition in self:
			# seq.name = '{}-{}/DPKS/DIT.{}/{}'.format(res.type.upper(), self.env['ir.sequence'].next_by_code('bpdpks.spp'), res.operating_unit_id.code, year)
			if any(not l.asset_category_id for l in acquisition.line_ids):
				raise ValidationError("Please input Asset Model for each line.")
			acquisition.name = self.env['ir.sequence'].next_by_code(self._name)
			acquisition.action_done()

	def action_done(self):
		for acquisition in self:
			if any(not l.asset_category_id for l in acquisition.line_ids):
				raise ValidationError("Please input Asset Model for each line.")

			AccountAsset = self.env['account.asset.asset']
			list_assets = self.env['account.asset.asset']
			dict_asset_grouped = {}
			for line in acquisition.line_ids:
				key_asset_model_id = line.asset_category_id.id
				key_line_group = f"line_{line.id}" if line.creation_mode == 'line_group' else False
				key_code_group = line.group_mark if line.creation_mode == 'code_group' else False
				if line.creation_mode == 'each_equipment':
					for equip in line.equipment_register_line_id.equipment_ids:
						for qty in range(int(line.product_qty)):
							key = f"{key_asset_model_id}:{key_line_group}:{key_code_group}:equip_id_{equip.id}:{qty}"
							if key not in dict_asset_grouped.keys():
								first_depreciation_date = acquisition.date
								dict_asset_grouped.update({key: {
									'purchase_account_values': {},
									'asset_values': {
										'name': f"{line.name}",
										'value': line.price_unit,
										'acquisition_date': acquisition.date,
										'salvage_value': 0.0,
										'method': line.asset_category_id.method,
										'method_number': line.asset_category_id.method_number,
										'method_period': line.asset_category_id.method_period,
										'prorata': line.asset_category_id.prorata,
										'first_depreciation_manual_date': first_depreciation_date,
										'category_id': line.asset_category_id.id,
										'acquisition_line_ids': [(4, line.id)],
									},
								}})
							key_account = line._get_computed_account()
							if not dict_asset_grouped[key]['purchase_account_values'].get(key_account, False):
								dict_asset_grouped[key]['purchase_account_values'].update({key_account: 0.0})
							dict_asset_grouped[key]['purchase_account_values'][key_account] += line.price_unit
				else:
					for qty in range(int(line.product_qty)):
						key = f"{key_asset_model_id}:{key_line_group}:{key_code_group}:False:{qty}"
						if key not in dict_asset_grouped.keys():
							first_depreciation_date = acquisition.date
							dict_asset_grouped.update({key: {
								'purchase_account_values': {},
								'asset_values': {
									'name': f"{line.name}",
									'value': line.price_unit,
									'acquisition_date': acquisition.date,
									'salvage_value': 0.0,
									'method': line.asset_category_id.method,
									'method_number': line.asset_category_id.method_number,
									'method_period': line.asset_category_id.method_period,
									'prorata': line.asset_category_id.prorata,
									'first_depreciation_manual_date': first_depreciation_date,
									'category_id': line.asset_category_id.id,
									'acquisition_line_ids': [(4, line.id)],
								},
							}})
						key_account = line._get_computed_account()
						if not dict_asset_grouped[key]['purchase_account_values'].get(key_account, False):
							dict_asset_grouped[key]['purchase_account_values'].update({key_account: 0.0})
						dict_asset_grouped[key]['purchase_account_values'][key_account] += line.price_unit

			for key, values in dict_asset_grouped.items():
				asset_vals = values['asset_values']
				purchase_account_dict = values['purchase_account_values']
				# Create Original Move
				move_lines = []
				move_vals = {
					'journal_id': self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')], limit=1).id,
					'date': acquisition.date,
					'acquisition_line_ids': asset_vals['acquisition_line_ids'],
				}

				asset_category = self.env['account.asset.category'].browse(asset_vals['category_id'])
				# debit_lines
				move_line_vals_asset = {
					'account_id': asset_category.account_asset_id.id,
					'name': 'Reclass Asset to SPM',
					'debit': sum(purchase_account_dict.values()),
					'credit': 0.0,
				}
				move_lines.append((0, 0, move_line_vals_asset))
				# credit_lines
				credit_account = line.product_id.categ_id.asset_clearing_account_id
				for account, amount in purchase_account_dict.items():
					move_line_vals = {
						'account_id': credit_account.id if credit_account else account.id,
						'name': 'Reclass SPM to Asset',
						'credit': amount,
						'debit': 0.0,
					}
					move_lines.append((0, 0, move_line_vals))
				# create move
				move_vals.update({'line_ids': move_lines})
				self.env['account.move'].create(move_vals)
				# new_move._post()

				# Create Asset
				new_asset = AccountAsset.create(asset_vals)
				new_asset.validate()
				list_assets |= new_asset

			acquisition.write({
				'state': 'done',
			})
		return self.action_open_asset(assets=list_assets)
	
	def create_lva_journal(self):
		for acquisition in self:
			for line in acquisition.line_ids:
				product_expense = line.product_id.property_account_expense_id.id
				product_categ_expense = line.product_id.categ_id.property_account_expense_categ_id.id

				if not product_expense and not product_categ_expense:
					raise ValidationError("Account Expense Belum Diisi")
				
				product_accounts = line.product_id.product_tmpl_id.get_product_accounts()
				stock_journal = product_accounts.get('stock_journal')
            
				if not stock_journal:
					raise ValidationError("Stock Journal not found for the product.")
				
				move_lines = []
				move_vals = {
					'journal_id': stock_journal.id,
					'date': acquisition.date,
					'acquisition_id': acquisition.id,
				}

				amount = line.purchase_line_id.price_unit * line.purchase_line_id.product_qty
				# debit_lines
				move_line_vals_asset = {
					'account_id': product_expense or product_categ_expense,
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
				self.env['account.move'].create(move_vals)
				# new_move._post()
				# line.asset_move_ids = [acquisition.id]

			acquisition.name = self.env['ir.sequence'].next_by_code(self._name)
			for equip in line.equipment_register_line_id.equipment_ids:
				equip.write({
					'asset_type' : 'lva'
				})
			acquisition.write({
				'state': 'reject',
			})
		return True
	

	def action_rejected(self):
		for acq in self:
			acq.create_lva_journal()