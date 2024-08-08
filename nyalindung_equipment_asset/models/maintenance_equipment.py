from odoo import models, fields, api
from datetime import date


class EquipmentAsset(models.Model):
    _inherit = 'maintenance.equipment'

    is_lva = fields.Boolean(string='LVA')
    # has_acquisition = fields.Boolean('Has Acquisition')
    seq_no = fields.Char('Sequence Number')
    condition = fields.Selection([
        ('good', 'Good'),
        ('broken', 'Broken'),
        ('lost', 'Lost'),
    ], string='condition', default="good") 
    asset_type = fields.Selection([
        ('lva', 'LVA'),
        ('fa', 'FA'),
    ], string='Asset Type', readonly=True)
    
    # @api.depends('cost')
    # def _compute_is_lva(self):
    #     for record in self:
    #         threshold = self.env['ny.low.value.asset'].search([('date_from', '<=', date.today()), ('date_to', '>=', date.today())], limit=1)
    #         if threshold and record.cost > threshold.amount:
    #             record.is_lva = True
    #         else:
    #             record.is_lva = False

    #######################
	#     HELPER METHOD   #
	#######################

	##########################
	#     BUSSINESS METHOD   #
	##########################
    # def create_asset_acquisition(self):
    #     self.ensure_one()
    #     Acquisition = self.env['account.asset.acquisition']
    #     AcquisitionLine = self.env['account.asset.acquisition.line']

    #     values = {
	# 		'origin': f"{self.name}",
	# 		'date': date.today(),
	# 		'company_id': self.company_id.id,
    #         'equipment_id' : self.id
	# 	}
    #     lines = []
    #     for equipment in self:
    #         threshold = self.env['ny.low.value.asset'].search([
    #             ('date_from', '<=', date.today()), 
    #             ('date_to', '>=', date.today())
    #         ], limit=1)
            
    #         if threshold and equipment.cost > threshold.amount:
    #             line_vals = {
	# 				'product_id': equipment.main_product_id.id if equipment.main_product_id else None,
	# 				'name': equipment.name,
	# 				'product_uom': equipment.main_product_id.uom_id.id,
	# 				'product_qty': 1,
	# 				'price_unit': equipment.cost,
	# 				'equipment_register_line_id': False,
	# 				'purchase_line_id': False,
	# 			}
    #             lines.append((0,0,line_vals))
    #             equipment.create_has_acquisition()
    #     values.update({'line_ids': lines})  
    #     new_acquisition = Acquisition.create(values)
	# 	# new_acquisition.action_submit()
    #     return self.action_open_acquisition(new_acquisition)
    
    # def create_has_acquisition(self):
    #     for record in self:
    #         record.update({
    #             'has_acquisition' : True
    #         })
    #     return True

    # def action_open_acquisition(self, equipments=False):
    #     result = self.env["ir.actions.actions"]._for_xml_id('c10i_equipment_account_asset.asset_acquisition_action')
    #     result['domain'] = "[('id','=',%s)]" % (equipments.id)
    #     return result
    
    # def action_view_acquisition(self):
    #     result = self.env['ir.actions.actions']._for_xml_id('c10i_equipment_account_asset.asset_acquisition_action')
    #     result['domain'] = "[('equipment_id','=',%s)]" % (self.id)
    #     return result
