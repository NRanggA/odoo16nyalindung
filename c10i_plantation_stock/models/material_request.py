from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MaterialRequest(models.Model):
    _inherit = 'material.request'

    # operating_unit_id = fields.Many2one('operating.unit', string='Operation Unit', check_company=True, default=lambda s: s.env.operating_unit)
    # operating_unit_id = fields.Many2one('operating.unit', related="location_id.operating_unit_id", string='Operation Unit', store=True)
    # is_kontraktor = fields.Boolean('Kontraktor')

    # def _prepare_picking(self):
    #     res = super()._prepare_picking()
    #     res.update({
    #             'operating_unit_id': self.operating_unit_id.id,
    #         })
    #     return res

    
class MaterialRequestLine(models.Model):
    _inherit = 'material.request.line'

    # TODO : ini ganti dengan location_type_id, cek di model lhm.transaction.line (punya ryan)
    cost_allocation_id = fields.Many2one('plantation.cost.type', string='Cost Allocation')
    # cost_allocation_mark = fields.Selection(related='cost_allocation_id.mark', string='Allocation Mark', store=True)
    # TODO : ini ganti namanya ke location_id, cek di model lhm.transaction.line (punya ryan)
    cost_center_id = fields.Many2one('plantation.cost.center', string='Cost Center', 
        domain="[('type_id','=',cost_allocation_id)]")
    # TODO : ini ganti namanya ke activity_id, cek di model lhm.transaction.line (punya ryan)
    cost_activity_id = fields.Many2one('plantation.cost.activity', string='Activity')
    # TODO : ini jg ada di lhm.transaction.line, lupa namanya disamakan saja
    filtered_cost_activity_ids = fields.Many2many('plantation.cost.activity', string='Filter Activity', compute='_filtered_cost_activity_ids')

    @api.depends('cost_allocation_id','cost_center_id')
    def _filtered_cost_activity_ids(self):
        for line in self:
            if line.mr_id.state!='draft' or not line.cost_allocation_id:
                line.filtered_cost_activity_ids = []
                continue
            activity_ids = []
            if line.cost_allocation_id.code=='PJ' and line.cost_center_id:
                current_project = self.env['plantation.project'].search([('cost_center_id','=',line.cost_center_id.id)])
                activity_ids = current_project.project_activity_ids.mapped('cost_activity_id').ids if current_project else []
            else:
                activity_ids = self.env['plantation.cost.activity'].search([('type_id','=',line.cost_allocation_id.id)]).ids
            
            line.filtered_cost_activity_ids = [(6, 0, activity_ids)]

    # Ini masih dipake, untuk tambahin Value di stock.move saat MR membuat otomatis Issue <stock.picking> 
    def _prepare_stock_move_vals(self, picking, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(picking, product_uom_qty, product_uom)
        res.update({
            'cost_allocation_id': self.cost_allocation_id.id,
            'cost_center_id': self.cost_center_id.id,
            'cost_activity_id': self.cost_activity_id.id,
            # 'operating_unit_id': self.mr_id.operating_unit_id.id,
        })
        return res