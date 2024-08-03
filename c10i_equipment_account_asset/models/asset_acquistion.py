# # -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError

class AssetAcquisition(models.Model):
	_name = 'account.asset.acquisition'
	_description = "Asset Acquisition"
	_inherit = ["mail.thread", "mail.activity.mixin"]
	# _order = 'date desc, id asc'

	name = fields.Char(string="Number", default="/")
	origin = fields.Char(string="Source Document")
	date = fields.Date(string="Register Date")
	state = fields.Selection([('draft', 'Draft'), 
					('submit', 'Submitted'), 
					('done', 'Registered'),
					('cancel', 'Cancelled')], string='State', default='draft')
	line_ids = fields.One2many('account.asset.acquisition.line', 'acquisition_id', 'Acquisition Lines')
	asset_count = fields.Integer(compute='_asset_count', string="# Asset", compute_sudo=True)
	move_count = fields.Integer(compute='_move_count', string="# Journal Entry", compute_sudo=True)
	company_id = fields.Many2one('res.company', string='Company', ondelete='restrict', default=lambda s: s.env.company.id)

	def _asset_count(self):
		for acq in self:
			acq.asset_count = len(acq.line_ids.mapped('asset_ids').ids)

	def _move_count(self):
		for acq in self:
			acq.move_count = len(acq.line_ids.mapped('asset_move_ids').ids)

	###################
	# ONCHANGE METHOD #
	###################

	#################
	# HELPER METHOD #
	#################
	
	####################
	# LOW-LEVEL METHOD #
	####################
	@api.model_create_multi
	def create(self, val_list):
		result = super(AssetAcquisition ,self).create(val_list)
		return result

	def unlink(self):
		for reg in self:
			if reg.state not in ['cancel', 'draft']:
				raise ValidationError("You can Only delete the Request(s) that are in 'New' or 'Cancelled' state !!!")
		return super(AssetAcquisition,self).unlink()

	###################
	# BUSINESS METHOD #
	###################
	def action_submit(self):
		for acquisition in self:
			# seq.name = '{}-{}/DPKS/DIT.{}/{}'.format(res.type.upper(), self.env['ir.sequence'].next_by_code('bpdpks.spp'), res.operating_unit_id.code, year)
			if any(not l.asset_category_id for l in acquisition.line_ids):
				raise ValidationError("Please input Asset Model for each line.")
			acquisition.name = self.env['ir.sequence'].next_by_code(self._name)
			acquisition.state = 'submit'

	def action_done(self):
		for acquisition in self:
			if acquisition.state!='submit':
				raise ValidationError("You can only Approve Asset Acquisition that are now in 'Submitted' state")
			if any(not l.asset_category_id for l in acquisition.line_ids):
				raise ValidationError("Please input Asset Model for each line.")

			AccountAsset = self.env['account.asset.asset']
			list_assets = self.env['account.asset.asset']
			dict_asset_grouped = {}
			for line in acquisition.line_ids:
				key_asset_model_id = line.asset_category_id.id
				key_line_group = f"line_{line.id}" if line.creation_mode=='line_group' else False
				key_code_group = line.group_mark if line.creation_mode=='code_group' else False
				if line.creation_mode=='each_equipment':
					for equip in line.equipment_register_line_id.equipment_ids:
						key_equip = f"equip_id_{equip.id}"
						key = f"{key_asset_model_id}:{key_line_group}:{key_code_group}:{key_equip}"

						if key not in dict_asset_grouped.keys():
							first_depreciation_date = acquisition.date
							dict_asset_grouped.update({key: {
								'purchase_account_values': {},
								'asset_values': {
									'name': line.name,
									'value' : 0.0,
									'acquisition_date': acquisition.date,
									'salvage_value': 0.0,
									'method': line.asset_category_id.method,
									'method_number': line.asset_category_id.method_number,
									'method_period': line.asset_category_id.method_period,
									'prorata': line.asset_category_id.prorata,
									'first_depreciation_manual_date': first_depreciation_date,
									'category_id': line.asset_category_id.id,
									'acquisition_line_ids': [],
									# 'equipment_ids'
								},
							}})
						dict_asset_grouped[key]['asset_values']['original_value'] += line.price_subtotal / line.product_qty
						dict_asset_grouped[key]['asset_values']['acquisition_line_ids'].append((4,line.id))

						key_account = line._get_computed_account()
						if not dict_asset_grouped[key]['purchase_account_values'].get(key_account, False):
							dict_asset_grouped[key]['purchase_account_values'].update({key_account: 0.0})
						dict_asset_grouped[key]['purchase_account_values'][key_account] += line.price_subtotal / line.product_qty
				else:
					key = f"{key_asset_model_id}:{key_line_group}:{key_code_group}:False"
					if key not in dict_asset_grouped.keys():
						first_depreciation_date = acquisition.date
						dict_asset_grouped.update({key: {
							'purchase_account_values': {},
							'asset_values': {
								'name': line.name,
								'value' : 0.0,
								'acquisition_date': acquisition.date,
								'salvage_value': 0.0,
								'method': line.asset_category_id.method,
								'method_number': line.asset_category_id.method_number,
								'method_period': line.asset_category_id.method_period,
								'prorata': line.asset_category_id.prorata,
								'first_depreciation_manual_date': first_depreciation_date,
								'category_id': line.asset_category_id.id,
								'acquisition_line_ids': [],
							},
						}})
					dict_asset_grouped[key]['asset_values']['value'] += line.price_subtotal
					dict_asset_grouped[key]['asset_values']['acquisition_line_ids'].append((4,line.id))

					key_account = line._get_computed_account()
					if not dict_asset_grouped[key]['purchase_account_values'].get(key_account, False):
						dict_asset_grouped[key]['purchase_account_values'].update({key_account: 0.0})
					dict_asset_grouped[key]['purchase_account_values'][key_account] += line.price_subtotal

			for keyx, valuesx in dict_asset_grouped.items():
				asset_vals = valuesx['asset_values']
				purchase_account_dict = valuesx['purchase_account_values']
				# Create Original Move
				move_lines = []
				move_vals = {
					'journal_id': self.env['account.journal'].search([('name','=','Miscellaneous Operations')], limit=1).id,
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
				move_lines.append((0,0,move_line_vals_asset))
				# credit_lines
				for account, amount in purchase_account_dict.items():
					move_line_vals = {
						'account_id': account.id,
						'name': 'Reclass SPM to Asset',
						'credit': amount,
						'debit': 0.0,
					}
					move_lines.append((0,0,move_line_vals))
				# create move
				move_vals.update({'line_ids': move_lines})
				new_move = self.env['account.move'].create(move_vals)
				new_move._post()

				# Create Asset
				# original_move_line_ids = new_move.line_ids.filtered(lambda xx: xx.account_id.id==asset_vals['category_id'].account_asset_id.id)
				# asset_vals.update({'original_move_line_ids': original_move_line_ids})
				new_asset = AccountAsset.create(asset_vals)
				new_asset.validate()
				list_assets |= new_asset
			
			acquisition.write({
				'state': 'done',
			})
		return self.action_open_asset(assets=list_assets)

	def action_cancel(self):
		for acquisition in self:
			for line in acquisition.line_ids:
				if line.asset_ids:
					raise ValidationError("You can only Cancel This when the Asset is not created yet. Please delete the asset first.")
				if line.asset_move_ids:
					if any(m.state!='cancel' for m in line.asset_move_ids):
						raise ValidationError("You can only Cancel This when the Asset Journal Entry is not created yet. Please Cancel the Entry first.")
					for m in line.asset_move_ids:
						m.with_context(force_delete=True).unlink()
		return self.write({'state':'cancel'})

	def action_set_draft(self):
		for acquisition in self:
			if acquisition.state!='cancel':
				raise ValidationError("You can only Set to Draft Asset Acquisition that are now in 'Cancel' state")
		return self.write({'state':'draft'})

	def action_open_asset(self, assets=False):
		result = self.env["ir.actions.actions"]._for_xml_id('om_account_asset.action_account_asset_asset_form')
		if not assets:
			assets = self.line_ids.mapped('asset_ids')

		if not assets or len(assets) > 1:
			result['domain'] = "[('id','in',%s)]" % (assets.ids)
		elif len(assets)==1:
			result['domain'] = "[('id','=',%s)]" % (assets.id)

		return result

	def action_open_move(self):
		result = self.env["ir.actions.actions"]._for_xml_id('account.action_move_line_form')
		moves = self.line_ids.mapped('asset_move_ids')

		if not moves or len(moves) > 1:
			result['domain'] = "[('id','in',%s)]" % (moves.ids)
		elif len(moves)==1:
			result['domain'] = "[('id','=',%s)]" % (moves.id)

		return result

class AssetAcquisitionLine(models.Model):
	_name = 'account.asset.acquisition.line'
	_description = "Asset Acquisition Lines"

	acquisition_id = fields.Many2one('account.asset.acquisition', string="Reference", ondelete='cascade')
	asset_model_id = fields.Many2one('account.asset.asset', string="Asset Model", ondelete='restrict', domain=[('state', '!=', 'close')])
	asset_category_id = fields.Many2one('account.asset.category', string='Asset Category', ondelete='restrict')
	product_id = fields.Many2one('product.product', string="Product", ondelete='restrict')
	name = fields.Char(string="Desription")
	product_uom = fields.Many2one('uom.uom', 'Unit of Measure', ondelete='restrict')
	product_qty = fields.Float('Quantity')
	price_unit = fields.Float('Price Unit')
	price_subtotal = fields.Float(compute='_amount_line', string='Value')
	equipment_register_line_id = fields.Many2one('equipment.register.line', string="Register Line", ondelete='restrict')
	purchase_line_id = fields.Many2one('purchase.order.line', string="Purchase Line", ondelete='restrict')
	purchase_id = fields.Many2one(related='purchase_line_id.order_id', string="Purchase Order", ondelete='restrict')
	creation_mode = fields.Selection([
		('each_equipment', 'Each Equipment'),
		('line_group', 'Group foreach Line'),
		('code_group', 'Group foreach Mark'),
		], string='Creation Mode', default='line_group',
		help="""Creation Mode\n
Each Equipment will create an Accounting Asset for each unit quantity registered.\n
Group foreach Line will create an Accounting Asset for each line.\n
Group foreach Mark will create an Accounting Asset for each Mark that you put in Group Mark.\n
Group Mark only work if you put the same Asset Model
""")
	group_mark = fields.Char('Group Mark')
	asset_ids = fields.Many2many('account.asset.asset', 'acquisition_line_account_asset_rel', 
						'acquisition_line_id', 'asset_id', string='Assets')
	asset_move_ids = fields.Many2many('account.move', 'acquisition_line_account_move_rel', 
						'acquisition_line_id', 'move_id', string='Moves')

	def _amount_line(self):
		for line in self:
			# TODO: tolong tambahkan kondisi jika price kena pajak 
			# include dan atau ada diskon di Purchase Line
			line.price_subtotal = line.price_unit * line.product_qty

	#################
	# HELPER METHOD #
	#################
	def _get_computed_account(self):
		self.ensure_one()
		self = self.with_company(self.acquisition_id.company_id)

		if not self.product_id:
			return

		accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=False)
		return accounts['expense']