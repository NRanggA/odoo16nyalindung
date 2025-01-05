from odoo import api, fields, models, _


class WizardHasilLhm(models.TransientModel):
	_name 			= 'wizard.hasil.lhm'
	_description 	= 'Wizard Hasil LHM'


	transaction_line_id = fields.Many2one('lhm.transaction.line', string="Transaction Line")
	activity_id = fields.Many2one('lhm.activity', string='Aktivitas', related='transaction_line_id.activity_id', readonly=True, store=True)

	product_id 	 = fields.Many2one('product.product', string="Product 1")
	hasil_1 	 = fields.Float("Hasil 1")
	satuan_1 	 = fields.Many2one('uom.uom', string='Satuan 1', related='activity_id.uom_id', readonly=True)
	
	product2_id = fields.Many2one('product.product', string="Product 2")
	hasil_2 	 = fields.Float("Hasil 2")
	satuan_2 	 = fields.Many2one('uom.uom', string='Satuan 2', related='activity_id.uom2_id', readonly=True)

	@api.model
	def default_get(self, fields_list):
		defaults = super(WizardHasilLhm, self).default_get(fields_list)

		# Set default transaction_line_id if exists in context
		if self.env.context.get('default_transaction_line_id'):
			transaction_line = self.env['lhm.transaction.line'].browse(self.env.context['default_transaction_line_id'])
			defaults['transaction_line_id'] = transaction_line.id
		
		lhm_transaction = self.env['lhm.transaction.line'].search([('id', '=', defaults['transaction_line_id'])])


		product1 = lhm_transaction.activity_id.product_id
		hasil_1  = lhm_transaction.hasil_1 if lhm_transaction.hasil_1 else 0
		if product1:
			defaults['product_id'] 	= product1.id
			defaults['hasil_1'] 	= hasil_1

		product2 = lhm_transaction.activity_id.product2_id
		hasil_2  = lhm_transaction.hasil_2 if lhm_transaction.hasil_2 else 0
		if product2:
			defaults['product2_id'] = product2.id
			defaults['hasil_2'] 	= hasil_2

		return defaults


	def action_confirm(self):
		if self.transaction_line_id:
			values_to_write = {}
			if self.product_id:
				values_to_write.update({
					'product_id'	: self.product_id.id,
					'hasil_1'		: self.hasil_1,
					'satuan_1'		: self.satuan_1.id,
				})
			if self.product2_id:
				values_to_write.update({
					'product_id_2' 	: self.product2_id.id,
					'hasil_2'		: self.hasil_2,
					'satuan_2'		: self.satuan_2.id,
				})
			self.transaction_line_id.write(values_to_write)
		else:
			pass

