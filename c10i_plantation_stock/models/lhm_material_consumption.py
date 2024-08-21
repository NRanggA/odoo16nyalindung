from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PlantationMaterialAllocation(models.Model):
    _name = 'lhm.material.consumption'
    _description = "Allocation Material"

    stock_move_id = fields.Many2one('stock.move', 'Source Move')
    lhm_id = fields.Many2one('lhm.transaction', string='LHM ID')
    lhm_material_id = fields.Many2one('lhm.transaction.material.line', string='LHM Material ID')
    mr_id = fields.Many2one('material.request', string='MR ID')
    product_qty = fields.Float('Qty Allocated')
    # plantation_partner_activity_material_id = fields.Many2one('plantation.partner.activity.material', string='Material Partner Activity', ondelete='cascade')