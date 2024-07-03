from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    cost_allocation_id = fields.Many2one('plantation.cost.type', string='Cost Allocation')
    cost_center_id = fields.Many2one('plantation.cost.center', string='Cost Center', 
        domain="[('type_id','=',cost_allocation_id)]")
    cost_activity_id = fields.Many2one('plantation.cost.activity', string='Activity', 
        domain="[('type_id','=',cost_allocation_id)]")