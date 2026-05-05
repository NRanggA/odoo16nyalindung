from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

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

	account_journal_id = fields.Many2one('account.journal', string='Account Journal', compute='_account_asset_on_sale', store=True)

	@api.depends('line_ids')
	def _account_asset_on_sale(self):
		for record in self:
			if record.line_ids:
				product = record.line_ids[0].product_id.categ_id
				record.account_journal_id = product.asset_journal_id if product else False

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
		# print("=== MASUK ACTION_SUBMIT ===")
		for acquisition in self:
			# seq.name = '{}-{}/DPKS/DIT.{}/{}'.format(res.type.upper(), self.env['ir.sequence'].next_by_code('bpdpks.spp'), res.operating_unit_id.code, year)
			if any(l.acquisition_type=='create' and not l.asset_category_id for l in acquisition.line_ids):
				raise ValidationError("Please input Asset Model for creating a new Asset.")
			if any(l.acquisition_type=='merge' and not l.existing_asset_id for l in acquisition.line_ids):
				raise ValidationError("Please input Existing Asset for merging to existing Asset.")
			acquisition.name = self.env['ir.sequence'].next_by_code(self._name)
			acquisition.action_done()

	def action_done(self):
		# print("=== MASUK ACTION_DONE ===")
		for acquisition in self:
			if any(l.acquisition_type=='create' and not l.asset_category_id for l in acquisition.line_ids):
				raise ValidationError("Please input Asset Model for creating a new Asset.")
			if any(l.acquisition_type=='merge' and not l.existing_asset_id for l in acquisition.line_ids):
				raise ValidationError("Please input Existing Asset for merging to existing Asset.")

			AccountAsset = self.env['account.asset.asset']
			list_assets = self.env['account.asset.asset']
			dict_asset_grouped = {}
			for line in acquisition.line_ids.filtered(lambda l: l.acquisition_type=='create'):
				# Hitung ulang price_unit jika non_credit aktif
				price_unit = line.price_unit
				if line.purchase_line_id.order_id.non_credit:
					if line.purchase_line_id.taxes_id:
						qty = line.purchase_line_id.product_qty or 1
						price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
						tax_result = line.purchase_line_id.taxes_id.with_context(round=False).compute_all(
							price_unit,
							currency=line.purchase_line_id.order_id.currency_id,
							quantity=qty,
						)
						price_unit_including_tax = tax_result['total_included'] / qty
						price_unit = float_round(price_unit_including_tax, precision_digits=price_unit_prec)
					if line.purchase_line_id.product_uom.id != line.purchase_line_id.product_id.uom_id.id:
						price_unit *= line.purchase_line_id.product_uom.factor / line.purchase_line_id.product_id.uom_id.factor

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
										'code': equip.seq_no,
										'value': price_unit,
										'date': acquisition.date,
										'acquisition_date': acquisition.date,
										'salvage_value': 0.0,
										'method': line.asset_category_id.method,
										'method_number': line.asset_category_id.method_number,
										'method_period': line.asset_category_id.method_period,
										'prorata': line.asset_category_id.prorata,
										'first_depreciation_manual_date': first_depreciation_date,
										'category_id': line.asset_category_id.id,
										'gain_account_id': line.asset_category_id.gain_account_id.id,
										'loss_account_id': line.asset_category_id.loss_account_id.id,
										'write_on_asset_sales_account_id': line.asset_category_id.write_on_asset_sales_account_id.id,
										'acquisition_line_ids': [(4, line.id)],
									},
								}})
							key_account = line._get_computed_account()
							if not dict_asset_grouped[key]['purchase_account_values'].get(key_account, False):
								dict_asset_grouped[key]['purchase_account_values'].update({key_account: 0.0})
							dict_asset_grouped[key]['purchase_account_values'][key_account] += price_unit
				else:
					for qty in range(int(line.product_qty)):
						key = f"{key_asset_model_id}:{key_line_group}:{key_code_group}:False:{qty}"
						equip = line.equipment_register_line_id.equipment_ids[:1]
						if key not in dict_asset_grouped.keys():
							first_depreciation_date = acquisition.date
							dict_asset_grouped.update({key: {
								'purchase_account_values': {},
								'asset_values': {
									'name': f"{line.name}",
									'code': (equip and equip[0].seq_no) or False,
									'value': price_unit,
									'date': acquisition.date,
									'acquisition_date': acquisition.date,
									'salvage_value': 0.0,
									'method': line.asset_category_id.method,
									'method_number': line.asset_category_id.method_number,
									'method_period': line.asset_category_id.method_period,
									'prorata': line.asset_category_id.prorata,
									'first_depreciation_manual_date': first_depreciation_date,
									'category_id': line.asset_category_id.id,
									'gain_account_id': line.asset_category_id.gain_account_id.id,
									'loss_account_id': line.asset_category_id.loss_account_id.id,
									'write_on_asset_sales_account_id': line.asset_category_id.write_on_asset_sales_account_id.id,
									'acquisition_line_ids': [(4, line.id)],
								},
							}})
						key_account = line._get_computed_account()
						if not dict_asset_grouped[key]['purchase_account_values'].get(key_account, False):
							dict_asset_grouped[key]['purchase_account_values'].update({key_account: 0.0})
						dict_asset_grouped[key]['purchase_account_values'][key_account] += price_unit
			
			# parent_assets = self.env['account.asset.asset']
			new_parent = []
			to_recompute_parent = self.env['account.asset.asset']
			existing_asset_dict = {}
			for line in acquisition.line_ids.filtered(lambda l: l.acquisition_type=='merge'):
				first_depreciation_date = acquisition.date
				if line.existing_asset_id.child_ids:
					parent_asset = line.existing_asset_id
					# first_depreciation_date = min(x.depreciation_date for x in parent_asset.child_ids.depreciation_line_ids.filtered(lambda d: not d.move_id))
					first_depreciation_date = min([d.depreciation_date for d in parent_asset.depreciation_line_ids.filtered(lambda d: not d.move_check)])
					remaining_depr = len(parent_asset.depreciation_line_ids.filtered(lambda d: not d.move_check).ids)
					if line.merge_mode=='no_extension':
						new_asset_method_number = remaining_depr
					else:
						if not line.extend_period:
							raise ValidationError("Please input Extend Period")
						if line.merge_mode=='extend_merged_asset' and not line.remaining_period:
							raise ValidationError("You try to Merge New Asset with Old Asset that doenst have Remaining Depreciation Period.\n Please change it to Extend Child Asset Only")
						
						# new_asset_method_number = parent_asset.category_id.method_number
						new_asset_method_number = remaining_depr + line.extend_period
						
						# if line.merge_mode=='prolong_old_asset':
						if line.merge_mode=='extend_merged_asset':
							for child in line.existing_asset_id.child_ids:
								if child not in existing_asset_dict.keys():
									existing_asset_dict.update({child: {
										# 'method_number': child.entry_count + new_asset_method_number,
										'method_number': child.method_number + line.extend_period,
										'method_period': child.method_period,
										'method_end': child.method_end,
									}})
				else:
					parent_vals = line.existing_asset_id.copy_data({
						'depreciation_line_ids': False,
						'state': 'open',
					})[0]
					# parent_vals['name'] = line.existing_asset_id.name
					parent_vals['name'] = f"Merge: {line.existing_asset_id.name}"
					parent_asset = self.env['account.asset.asset'].create(parent_vals)
					new_parent.append((parent_asset.id, line.existing_asset_id))
					first_depreciation_date = min(x.depreciation_date for x in line.existing_asset_id.depreciation_line_ids.filtered(lambda d: not d.move_check))
					remaining_depr = len(line.existing_asset_id.depreciation_line_ids.filtered(lambda d: not d.move_check).ids)
					if line.merge_mode=='no_extension':
						new_asset_method_number = remaining_depr
					else:
						new_asset_method_number = remaining_depr + line.extend_period
						# if line.merge_mode=='prolong_old_asset':
						if line.merge_mode=='extend_merged_asset':
							if line.existing_asset_id not in existing_asset_dict.keys():
								existing_asset_dict.update({line.existing_asset_id: {
									'method_number': line.existing_asset_id.method_number + line.extend_period,
									'method_period': line.existing_asset_id.method_period,
									'method_end': line.existing_asset_id.method_end,
								}})
				
				price_unit = line.price_unit
				if line.purchase_line_id.order_id.non_credit:
					if line.purchase_line_id.taxes_id:
						qty = line.purchase_line_id.product_qty or 1
						price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
						tax_result = line.purchase_line_id.taxes_id.with_context(round=False).compute_all(
							price_unit,
							currency=line.purchase_line_id.order_id.currency_id,
							quantity=qty,
						)
						price_unit_including_tax = tax_result['total_included'] / qty
						price_unit = float_round(price_unit_including_tax, precision_digits=price_unit_prec)
					if line.purchase_line_id.product_uom.id != line.purchase_line_id.product_id.uom_id.id:
						price_unit *= line.purchase_line_id.product_uom.factor / line.purchase_line_id.product_id.uom_id.factor

				to_recompute_parent |= parent_asset
				
				key_asset_model_id = line.existing_asset_id.category_id.id
				key_line_group = False
				key_code_group = False
				for qty in range(int(line.product_qty)):
					key = f"{key_asset_model_id}:{key_line_group}:{key_code_group}:False:{qty}"
					# equip = line.equipment_register_line_id.equipment_ids[:1] #KalauDibutuhkan
					if key not in dict_asset_grouped.keys():
						dict_asset_grouped.update({key: {
							'purchase_account_values': {},
							'asset_values': {
								'name': f"{line.name}",
								# 'code': (equip and equip[0].seq_no) or False, #KalauDibutuhkan
								'parent_id': parent_asset.id,
								'value': price_unit,
								'date': acquisition.date,
								'acquisition_date': acquisition.date,
								'salvage_value': 0.0,
								'method': parent_asset.method,
								'method_number': new_asset_method_number,
								'method_period': parent_asset.method_period,
								'prorata': parent_asset.prorata,
								'first_depreciation_manual_date': first_depreciation_date,
								'category_id': parent_asset.category_id.id,
								'gain_account_id': line.asset_category_id.gain_account_id.id,
								'loss_account_id': line.asset_category_id.loss_account_id.id,
								'write_on_asset_sales_account_id': line.asset_category_id.write_on_asset_sales_account_id.id,
								'acquisition_line_ids': [(4, line.id)],
							},
						}})
					key_account = line._get_computed_account()
					if not dict_asset_grouped[key]['purchase_account_values'].get(key_account, False):
						dict_asset_grouped[key]['purchase_account_values'].update({key_account: 0.0})
					dict_asset_grouped[key]['purchase_account_values'][key_account] += price_unit

			for key, values in dict_asset_grouped.items():
				asset_vals = values['asset_values']
				purchase_account_dict = values['purchase_account_values']
				if purchase_account_dict and line.product_id:
					asset_category = self.env['account.asset.category'].browse(asset_vals['category_id'])
					# Create Original Move

					journal = self.account_journal_id
					move_lines = []
					move_vals = {
						'journal_id': journal.id if journal else False,
						'date': acquisition.date,
						'acquisition_line_ids': asset_vals['acquisition_line_ids'],
					}
					# debit_lines
					move_line_vals_asset = {
						'account_id': asset_category.account_asset_id.id,
						'name': 'Reclass Asset Clearing to Asset',
						'debit': sum(purchase_account_dict.values()),
						'credit': 0.0,
					}
					move_lines.append((0, 0, move_line_vals_asset))
					# credit_lines
					credit_account = line.product_id.categ_id.asset_clearing_account_id
					for account, amount in purchase_account_dict.items():
						move_line_vals = {
							'account_id': credit_account.id if credit_account else account.id,
							'name': 'Reclass Asset Clearing to Asset',
							'credit': amount,
							'debit': 0.0,
						}
						move_lines.append((0, 0, move_line_vals))
					# create move
					move_vals.update({'line_ids': move_lines})
					new_move = self.env['account.move'].create(move_vals)
					new_move._post()

				# Create Asset
				# print("ASSET VALS:", values['asset_values'])
				# print("VALS CODE:", asset_vals.get('code'))
				new_asset = AccountAsset.create(asset_vals)
				# print("AFTER CREATE:", new_asset.code)
				new_asset.validate()
				# print("AFTER VALIDATE:", new_asset.code)
				# print("KEY:", key)
				# print(stop)
				list_assets |= new_asset

			for exs_asset, values in existing_asset_dict.items():
				old_values = {
					'method_number': exs_asset.method_number,
					'method_period': exs_asset.method_period,
					'method_end': exs_asset.method_end,
				}
				# print("::::::::::::::::::old_values", old_values)
				# print("::::::::::::::::::new_values", values)
				exs_asset.write(values)
				exs_asset.compute_depreciation_board()
				tracked_fields = self.env['account.asset.asset'].fields_get(['method_number', 'method_period', 'method_end'])
				changes, tracking_value_ids = exs_asset._mail_track(tracked_fields, old_values)
				if changes:
					exs_asset.message_post(subject=_('Asset Merge: Depreciation board modified'), body=self.name, tracking_value_ids=tracking_value_ids)
			
			for parent_id, existing_asset in new_parent:
				existing_asset.write({
					'parent_id': parent_id,
					# 'name': f"Merge: {existing_asset.name}",
				})

			# TODO: Recompute Parent Depreciation Board
			if to_recompute_parent:
				to_recompute_parent.compute_parent_depreciation_board()
			
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
					'name': 'Reclass Asset Clearing to Asset',
					'debit': amount,
					'credit': 0.0,
				}
				move_lines.append((0, 0, move_line_vals_asset))
				# credit_lines
				credit_account = line.product_id.categ_id.asset_clearing_account_id
				move_line_vals = {
					'account_id': credit_account.id,
					'name': 'Reclass Asset Clearing to Asset',
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