from odoo import models, fields

class EquipmentRegister(models.Model):
    _inherit = 'equipment.register'

    asset_coordinator = fields.Many2one('hr.employee', string='Asset Coordinator')