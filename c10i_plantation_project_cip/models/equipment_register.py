from odoo import models, fields, api, _ 


class EquipmentRegister(models.Model):
    _inherit = 'equipment.register'

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
            
            if rline.project_id:
                threshold_to_param = self.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_to', default=0.0)
                threshold_to = float(threshold_to_param) if threshold_to_param else 0.0

                if threshold_to and rline.project_id.amount_cip > threshold_to:
                    line_vals = {
                        'product_id': rline.product_id.id,
                        'name': rline.name,
                        'product_uom': rline.product_uom.id or False,
                        'product_qty': rline.product_qty,
                        'price_unit': rline.project_id.amount_cip,
                        'equipment_register_line_id': rline.id,
                        # 'purchase_line_id': rline.purchase_line_id.id,
                        'asset_category_id': self.category_id.asset_category_id.id
                    }
                    lines.append((0,0,line_vals))
        values.update({'line_ids': lines})
		
        if lines:
            new_acquisition = Acquisition.create(values)
        else:
            new_acquisition = False
        
        res = super().create_asset_acquisition()
        
        return new_acquisition or res




class EquipmentRegisterLine(models.Model):
    _inherit = 'equipment.register.line'

    project_id = fields.Many2one('lhm.project', string='LHM Project')

    def _get_account_clearing(self):
        project_lines = self.filtered(lambda l : l.project_id)
        for record in project_lines:
            if record.project_id:
                activity = record.project_id.activity_ids[:1]
                record.account_id = activity.account_id.id
        super(EquipmentRegisterLine, self - project_lines)._get_account_clearing()
