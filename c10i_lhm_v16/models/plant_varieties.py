from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PlantVarieties(models.Model):
    _name = 'plant.varieties'
    _description = 'Varietas'

    name = fields.Char('ORG', required=True)
    code = fields.Char('Code')
    product_id = fields.Many2one('product.product', string='Output Product')
    secondary_product_id = fields.Many2one('product.product', string='Secondary Product')

    plant_block_ids = fields.One2many('lhm.plant.block', 'varieties_id', string='Planted Block')
    harvest_activity_id = fields.Many2one('lhm.activity', string='Harvesting Activity')
    upkeep_activity_ids = fields.Many2many('lhm.activity', 'varieties_upkeep_rel', string='Upkeep Activities')

    # project_activity_ids = fields.Many2many('lhm.activity', 'project_upkeep_rel', string='Project Activities')
    project_ids = fields.One2many('lhm.project', 'varieties_id', string='Project')
    nursery_ids = fields.One2many('lhm.nursery', 'varieties_id', string='Nursery')

    general_charges_activity_ids = fields.Many2many('lhm.activity', 'varieties_gc_rel', string='Indirec Cost Activities')
    indirect_cost_activity_ids = fields.Many2many('lhm.activity', 'varieties_idc_rel', string='General Charges Activities')