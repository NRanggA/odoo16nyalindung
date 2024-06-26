from odoo import api, fields, models, _


class WizardHasilLhm(models.TransientModel):
	_name 			= 'wizard.hasil.lhm'
	_description 	= 'Wizard Hasil LHM'


	product_id = fields.Many2one('product.template', string="Product")
	qty 	   = fields.Integer("Jumlah / Qty")
	uom    = fields.Many2one('uom.uom', string='Satuan', related='product_id.uom_id', readonly=True)	
	hasil      = fields.Selection([
			('hasil1', 'Hasil 1'),
			('hasil2', 'Hasil 2')
		])


	def action_confirm(self):
		print("data hasil")
        # return {
        # 	'type': 'ir.actions.act_window_close',
        # 	}
