from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round

class EquipmentRegister(models.Model):
	_inherit = 'equipment.register'

	#######################
	#     HELPER METHOD   #
	#######################

	##########################
	#     BUSSINESS METHOD   #
	##########################
	def create_asset_acquisition(self):
		self.ensure_one()
		Acquisition = self.env['account.asset.acquisition']
		AcquisitionLine = self.env['account.asset.acquisition.line']
		
		values = {
			'origin': f"{self.origin}: {self.name}",
			'date': self.date,
			'company_id': self.company_id.id,
		}
		lines = []
		for rline in self.register_line_ids:
			line_vals = {
				'product_id': rline.product_id.id,
				'name': rline.name,
				'product_uom': rline.product_uom.id,
				'product_qty': rline.product_qty,
				'price_unit': rline.purchase_line_id.price_unit,
				'equipment_register_line_id': rline.id,
				'purchase_line_id': rline.purchase_line_id.id,
			}
			lines.append((0,0,line_vals))
		values.update({'line_ids': lines})
		new_acquisition = Acquisition.create(values)
		# new_acquisition.action_submit()
		return new_acquisition

	def register_hook(self):
		res = super().register_hook()
		for register in self:
			result = register.create_asset_acquisition()
		return res
