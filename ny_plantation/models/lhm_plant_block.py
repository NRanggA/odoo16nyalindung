from odoo import models, fields, api, _

class PlantBlock(models.Model):
    _inherit = 'lhm.plant.block'
    
    production_daily_target = fields.Float('Target Panen Kanen')