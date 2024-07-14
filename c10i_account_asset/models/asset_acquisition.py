# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero
from itertools import groupby

class AssetAcquisition(models.Model):
	_name = 'asset.acquisition'
	_inherit = ["mail.thread", "mail.activity.mixin"]
	_description = 'Asset Acquisition'

	name = fields.Char(string="Name")
	journal_id = fields.Many2one("account.journal", string="Journal")
	partner_id = fields.Many2one("res.partner", string="Vendor")
	date = fields.Date(string="Date Acquisition")
	first_depr_date = fields.Date(string="Start Depreciating")
	state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], 'Status', readonly=True, copy=False,
							 default='draft')
	acquisition_line_ids = fields.One2many("asset.acquisition.line", "asset_acquisition_id", string="Details")
	asset_ids = fields.One2many("account.asset.asset", 'asset_acquisition_id', string="Assets")
	move_id = fields.Many2one("account.move", string="Journal Entries")
	invoice_id = fields.Many2one("account.move", string="Vendor Bill")
	asset_count = fields.Integer(compute="_asset_count")

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

	@api.depends('asset_ids')
	def _asset_count(self):
		for res in self:
			res.asset_count = len(res.asset_ids)

	def action_view_asset(self):
		assets = self.env['account.asset.asset'].search([('id','in',self.asset_ids.ids)])

		return {
			'name': 'Asset',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.asset.asset',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id','in',assets.ids)],
		} if len(assets.ids) > 1 else {
			'name': 'Asset',
			'view_mode': 'form',
			'res_model': 'account.asset.asset',
			'views': [(False,'form')],
			'type': 'ir.actions.act_window',
			'res_id': assets.ids[0],
			'target': 'current',
		}

	@api.model
	def create(self, vals):
		sequence_code = 'asset.acquisition.seq'
		name = self.env['ir.sequence'].next_by_code(sequence_code)
		if name:
			vals['name'] = name
		return super(AssetAcquisition, self).create(vals)

	def action_post(self):
		self.ensure_one()
		move_lines = []
		move = self.env['account.move']
		line_grouped = {}
		for x in self.acquisition_line_ids:
			key = f"{x.group or ''}:{x.model_id.id}"
			if key not in line_grouped.keys():
				line_grouped.update({
						key: self.env['asset.acquisition.line'],
					})
			line_grouped[key] += x

		for group, lines in line_grouped.items():
			# datas = self.acquisition_line_ids.filtered(lambda x: x.group == group)
			check = group.split(":")[0]
			if check:
				datas = lines
				original_value = sum([x.purchase_value*x.qty for x in datas])
				salvage_value = sum([x.not_depr_value*x.qty for x in datas])
				model = datas.mapped('model_id')
				name = group+": %s"%(", ".join(datas.mapped('product_id').mapped('name')))
				self.asset_ids = [(0,0,{
						'name': name,
						'original_value' : original_value,
						'acquisition_date': self.date,
						'salvage_value': salvage_value,
						'model_id': datas[-1].model_id.id,
						'method': model.method,
						'method_number': model.method_number,
						'method_period': model.method_period,
						'prorata': model.prorata,
						'first_depreciation_date': self.first_depr_date,
						'account_asset_id': model.account_asset_id.id,
						'account_depreciation_id': model.account_depreciation_id.id,
						'account_depreciation_expense_id': model.account_depreciation_expense_id.id,
						'journal_id': model.journal_id.id,
						'asset_type': 'purchase',
					})]

				account_asset_id = model.account_asset_id
				if not account_asset_id:
					raise UserError(_("Fixed Asset Account belum didefinisikan di Asset Model [%s]" %(model.name)))
				move_lines.append((0,0,{
					'account_id' : account_asset_id.id,
					'partner_id' : self.partner_id.id,
					'name' : name,
					'debit': original_value,
					'credit': 0.0,
					'date': self.date,
				}))
				for data in datas:
					account_asset_clearing_id = data.product_id.property_account_expense_id or data.product_id.categ_id.property_account_expense_categ_id
					if not account_asset_clearing_id:
						raise UserError(_("Expense Account belum didefinisikan di product [%s]" %(data.product_id.name)))

					move_lines.append((0,0,{
						'account_id' : account_asset_clearing_id.id,
						'partner_id' : self.partner_id.id,
						'name' : "Asset Acquisition: "+ data.product_id.name,
						'debit': 0.0,
						'credit': data.purchase_value*data.qty,
						'date': self.date,
					}))
			else:

	# else:		
				for line in lines:
					for i in range(1,int(line.qty)+1):
						self.asset_ids = [(0,0,{
								'name': line.product_id.name+" "+str(i),
								'original_value' : line.purchase_value,
								'acquisition_date': self.date,
								'salvage_value': line.not_depr_value,
								'model_id': line.model_id.id,
								'method': line.model_id.method,
								'method_number': line.model_id.method_number,
								'method_period': line.model_id.method_period,
								'prorata': line.model_id.prorata,
								'first_depreciation_date': self.first_depr_date,
								'account_asset_id': line.model_id.account_asset_id.id,
								'account_depreciation_id': line.model_id.account_depreciation_id.id,
								'account_depreciation_expense_id': line.model_id.account_depreciation_expense_id.id,
								'journal_id': line.model_id.journal_id.id,
								'asset_type': 'purchase',
							})]

						account_asset_id = line.model_id.account_asset_id
						if not account_asset_id:
							raise UserError(_("Fixed Asset Account belum didefinisikan di Asset Model [%s]" %(line.model_id.name)))
						move_lines.append((0,0,{
							'account_id' : account_asset_id.id,
							'partner_id' : self.partner_id.id,
							'name' : "Asset: "+line.product_id.name+" "+str(i),
							'debit': line.purchase_value or 0.0,
							'credit': 0.0,
							'date': self.date,
						}))
						account_asset_clearing_id = line.product_id.property_account_expense_id or line.product_id.categ_id.property_account_expense_categ_id
						if not account_asset_clearing_id:
							raise UserError(_("Expense Account belum didefinisikan di product [%s]" %(line.product_id.name)))

						move_lines.append((0,0,{
							'account_id' : account_asset_clearing_id.id,
							'partner_id' : self.partner_id.id,
							'name' : "Asset Acquisition: "+ line.product_id.name+" "+str(i),
							'debit': 0.0,
							'credit': line.purchase_value or 0.0,
							'date': self.date,
						}))

		if move_lines:
			move = move.create({
					'journal_id' : self.journal_id.id,
					'date' : self.date,
					'line_ids': move_lines,
				})
			move.post()
			self.write({
				'state': 'posted',
				'move_id': move.id})

	def _prepare_invoice(self):
		"""Prepare the dict of values to create the new invoice for a purchase order.
		"""
		self.ensure_one()
		move_type = self._context.get('default_move_type', 'in_invoice')
		journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
		if not journal:
			raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

		partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
		invoice_vals = {
			'ref': '',
			'move_type': move_type,
			# 'narration': self.notes,
			'currency_id': self.company_id.currency_id.id,
			# 'invoice_user_id': self.user_id and self.user_id.id,
			'partner_id': partner_invoice_id,
			# 'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
			'payment_reference': '',
			'partner_bank_id': self.partner_id.bank_ids[:1].id,
			'invoice_origin': self.name,
			# 'invoice_payment_term_id': self.payment_term_id.id,
			'invoice_line_ids': [],
			'company_id': self.company_id.id,
		}
		return invoice_vals

	def action_view_invoice(self, invoices=False):
		"""This function returns an action that display existing vendor bills of
		given purchase order ids. When only one found, show the vendor bill
		immediately.
		"""
		if not invoices:
			# Invoice_ids may be filtered depending on the user. To ensure we get all
			# invoices related to the purchase order, we read them in sudo to fill the
			# cache.
			self.sudo()._read(['invoice_id'])
			invoices = self.invoice_id
		print("...............", invoices, len(invoices ))

		result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
		# choose the view_mode accordingly
		if len(invoices) > 1:
			result['domain'] = [('id', 'in', invoices.ids)]
		elif len(invoices) == 1:
			res = self.env.ref('account.view_move_form', False)
			form_view = [(res and res.id or False, 'form')]
			if 'views' in result:
				result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
			else:
				result['views'] = form_view
			result['res_id'] = invoices.id
		else:
			result = {'type': 'ir.actions.act_window_close'}

		return result
		

	def action_craete_bill(self):
		"""Create the invoice associated to the PO.
		"""
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

		# 1) Prepare invoice vals and clean-up the section lines
		invoice_vals_list = []
		for acq in self:
			# if acq.invoice_status != 'to invoice':
			#     continue
			if acq.invoice_id:
				continue

			acq = acq.with_company(acq.company_id)
			pending_section = None
			# Invoice values.
			invoice_vals = acq._prepare_invoice()
			# Invoice line values (keep only necessary sections).
			for line in acq.acquisition_line_ids:
				if not float_is_zero(line.qty, precision_digits=precision):
					invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
			invoice_vals_list.append(invoice_vals)

		if not invoice_vals_list:
			raise UserError(_('There is no invoiceable line. Please make sure you have inputted the Quantity and Purchase Value'))

		# 2) group by (company_id, partner_id, currency_id) for batch creation
		new_invoice_vals_list = []
		for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
			origins = set()
			payment_refs = set()
			refs = set()
			ref_invoice_vals = None
			for invoice_vals in invoices:
				if not ref_invoice_vals:
					ref_invoice_vals = invoice_vals
				else:
					ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
				origins.add(invoice_vals['invoice_origin'])
				payment_refs.add(invoice_vals['payment_reference'])
				refs.add(invoice_vals['ref'])
			ref_invoice_vals.update({
				'ref': ', '.join(refs)[:2000],
				'invoice_origin': ', '.join(origins),
				'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
			})
			new_invoice_vals_list.append(ref_invoice_vals)
		invoice_vals_list = new_invoice_vals_list

		# 3) Create invoices.
		moves = self.env['account.move']
		AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
		for vals in invoice_vals_list:
			new_move = AccountMove.with_company(vals['company_id']).create(vals)
			self.invoice_id = new_move.id
			moves |= new_move

		return self.action_view_invoice(moves)

class AssetAcquisitionLine(models.Model):
	_name = 'asset.acquisition.line'
	_description = 'Asset Acquisition Line'

	asset_acquisition_id = fields.Many2one("asset.acquisition", string="Asset Acquisition")
	product_id = fields.Many2one("product.product", string="Product")
	model_id = fields.Many2one("account.asset.asset", string="Asset Model", domain=[('state', '=', 'model')])
	origin = fields.Char(string="Source Document")
	name = fields.Char(string="Description")
	acquisition_value = fields.Float(string="Acquisition Value", compute="_compute_acquisition", store=True)
	not_depr_value = fields.Float(string="Not Depreciable Value")
	purchase_value = fields.Float(string="Purchase Value")
	qty = fields.Float(string="Quantity")
	group = fields.Char(string="Group")
	total_value = fields.Float(string="Total", compute="_compute_total", store=True)

	@api.depends('purchase_value', 'not_depr_value')
	def _compute_acquisition(self):
		for line in self:
			line.acquisition_value = line.purchase_value - line.not_depr_value

	@api.depends('qty', 'acquisition_value')
	def _compute_total(self):
		for line in self:
			line.total_value = line.qty * line.acquisition_value

	def _prepare_account_move_line(self, move=False):
		self.ensure_one()
		res = {
			# 'display_type': self.display_type,
			# 'sequence': self.sequence,
			'name': '%s: %s' % (self.asset_acquisition_id.name, self.name),
			'product_id': self.product_id.id,
			'product_uom_id': self.product_id.uom_po_id.id,
			'quantity': self.qty,
			'price_unit': self.purchase_value,
			# 'tax_ids': [(6, 0, self.taxes_id.ids)],
			# 'analytic_account_id': self.account_analytic_id.id,
			# 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
			# 'purchase_line_id': self.id,
		}
		if not move:
			return res

		if self.currency_id == move.company_id.currency_id:
			currency = False
		else:
			currency = move.currency_id

		res.update({
			'move_id': move.id,
			'currency_id': currency and currency.id or False,
			'date_maturity': move.invoice_date_due,
			'partner_id': move.partner_id.id,
		})
		return res