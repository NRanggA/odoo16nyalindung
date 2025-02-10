from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PlantVarieties(models.Model):
    _name = 'plant.varieties'
    _description = 'Varietas'

    active = fields.Boolean('active', default=True)
    name = fields.Char('ORG', required=True)
    code = fields.Char('Code')
    product_id = fields.Many2one('product.product', string='Output Product')
    secondary_product_id = fields.Many2one('product.product', string='Secondary Product')
    other_product_ids = fields.Many2many('product.product', 'varitas_product_rel', string='Other Products')

    plant_block_ids = fields.One2many('lhm.plant.block', 'varieties_id', string='Planted Block')
    
    # Many2one
    # harvest_activity_id = fields.Many2one('lhm.activity', string='Harvesting Activity')
    # Many2many
    harvest_activity_ids = fields.Many2many('lhm.activity', string='Harverst Activities')
    upkeep_activity_ids = fields.Many2many('lhm.activity', 'varieties_upkeep_rel', string='Upkeep Activities')
    general_charges_activity_ids = fields.Many2many('lhm.activity', 'varieties_gc_rel', string='Indirec Cost Activities')
    indirect_cost_activity_ids = fields.Many2many('lhm.activity', 'varieties_idc_rel', string='General Charges Activities')

    # project_activity_ids = fields.Many2many('lhm.activity', 'project_upkeep_rel', string='Project Activities')
    project_ids = fields.One2many('lhm.project', 'varieties_id', string='Project')
    # nursery_ids = fields.One2many('lhm.nursery', 'varieties_id', string='Nursery')
    
    mill_costs_ids = fields.Many2many('lhm.activity', 'varieties_mill_costs_rel', string='Mill Costs Activities')

    panen = fields.Boolean('Panen', default=False)


    def write(self, update_vals):
        # location_to_unlink = self.env['lhm.location']
        # location_to_link = self.env['lhm.location']
        check = {}

        if update_vals.get('active') == False:
            if self.plant_block_ids:
                raise ValidationError(_("ORG tidak bisa di non-aktifkan karena masih terdapat blok yang terhubung dengan ORG ini."))
            
        for rec in self:
            if rec.id not in check:
                check.update({rec.id: {
                    'bef_project' : self.env['lhm.project'],
                    'aft_project' : self.env['lhm.project'],
                    'bef_nursery' : self.env['lhm.nursery'],
                    'aft_nursery' : self.env['lhm.nursery']
                    }
                })
            if 'project_ids' in update_vals:
                check[rec.id]['bef_project'] = rec.project_ids
            if 'nursery_ids' in update_vals:
                check[rec.id]['bef_nursery'] = rec.nursery_ids
        
        res = super(PlantVarieties, self).write(update_vals)

        for rec in self:
            if 'project_ids' in update_vals:
                check[rec.id]['aft_project'] = rec.project_ids
            if 'nursery_ids' in update_vals:
                check[rec.id]['aft_nursery'] = rec.nursery_ids
        
            to_check = check[rec.id]
            if (to_check['bef_project'] - to_check['aft_project']):
                (to_check['bef_project'] - to_check['aft_project']).location_id.write({'varieties_id': False})
            if (to_check['aft_project'] - to_check['bef_project']):
                (to_check['aft_project'] - to_check['bef_project']).location_id.write({'varieties_id': rec.id})
        return res