from odoo import api, fields, models, _


class WizardHasilLhm(models.TransientModel):
	_name 			= 'wizard.hasil.lhm'
	_description 	= 'Wizard Hasil LHM'


	transaction_line_id = fields.Many2one('lhm.transaction.line', string="Transaction Line")
	
	product_id 	= fields.Many2one('product.product', string="Product 1")
	hasil_1 	= fields.Integer("Hasil 1")
	satuan_1 	= fields.Many2one('uom.uom', string='Satuan 1', related='product_id.uom_id', readonly=True)
	
	product_id_2 = fields.Many2one('product.product', string="Product 2")
	hasil_2 	 = fields.Integer("Hasil 2")
	satuan_2 	 = fields.Many2one('uom.uom', string='Satuan 2', related='product_id_2.uom_id', readonly=True)

	@api.model
	def default_get(self, fields_list):
	    defaults = super(WizardHasilLhm, self).default_get(fields_list)
	    if self.env.context.get('default_transaction_line_id'):
	        transaction_line = self.env['lhm.transaction.line'].browse(self.env.context['default_transaction_line_id'])
	        defaults['transaction_line_id'] = transaction_line.id
	    return defaults

	def action_confirm(self):
		if self.transaction_line_id:
		    values_to_write = {}
		    if self.product_id:
		        values_to_write.update({
		        	'product_id': self.product_id.id,
					'hasil_1'	: self.hasil_1,
					'satuan_1'	: self.satuan_1.id,
		        })
		    if self.product_id_2:
		        values_to_write.update({
		        	'product_id_2' : self.product_id_2.id,
		            'hasil_2': self.hasil_2,
		            'satuan_2': self.satuan_2.id,
		        })
		    self.transaction_line_id.write(values_to_write)
		else:
		    pass

