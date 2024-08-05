from odoo import models, fields, api, _

class AssetAcquisition(models.Model):
    _inherit = 'account.asset.acquisition'
      
    equipment_id = fields.Many2one('maintenance.equipment', string="Equipment ID")