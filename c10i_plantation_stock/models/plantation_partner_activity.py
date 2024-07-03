from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError,UserError

class PartnerActivity(models.Model):
    _inherit = 'plantation.partner.activity'

    def action_outstanding_material(self):
        # TODO : this will be updated at c10i_plantation_stock
        for rec in self:
            to_write = []
            timesheets_need_material = rec.timesheet_ids.filtered(lambda ts: ts.cost_activity_id.need_material)
            for activity in timesheets_need_material.mapped('cost_activity_id'):
                for cost_center in timesheets_need_material.filtered(lambda ts2: ts2.cost_activity_id.id==activity.id).mapped('cost_center_id'):
                    
                    moves_avaliable = self.env['stock.move'].search([('allocation_residual_qty','>',0.0),
                        ('cost_center_id','=',cost_center.id), ('cost_activity_id','=',activity.id), ('mr_line_id.mr_id.is_kontraktor','=',True)])

                    for move in moves_avaliable:
                        to_write.append({
                            'name': move.picking_id.name,
                            'stock_move_id': move.id,
                            'stock_product_id': move.product_id.id,
                            'cost_center_id': move.cost_center_id.id,
                            'cost_activity_id': move.cost_activity_id.id,
                            'date': move.date
                        })
            if to_write:
                rec.consumed_material_ids = list(map(lambda x:(0,0,x), to_write))
        return True


    # def action_confirm_material(self):
    #     res = super().action_confirm_material()
    #     for rec in self:
    #         rec.consumed_material_ids.action_stock_move_create()
    #     return res

class PartnerActivityMaterial(models.Model):
    _inherit = 'plantation.partner.activity.material'

    stock_move_id = fields.Many2one("stock.move", string="Origin Move", ondelete="restrict")
    residual_qty = fields.Float(related='stock_move_id.allocation_residual_qty', store=True, string='Residual Qty')

    stock_allocation_ids = fields.One2many('lhm.material.consumption', 'plantation_partner_activity_material_id', string='Allocations')

    def _prepare_move_allocation_vals(self):
        return {
                'stock_move_id':  self.stock_move_id.id,
                'plantation_partner_activity_material_id' : self.id,
                'product_qty' : self.consumed_qty,
            }

    def action_stock_move_create(self):
        to_create = []
        for line in self:
            if (line.residual_qty - line.consumed_qty) < 0.0:
                raise UserError(_("Picking %s doenst have enough quantity")%line.name)
            to_create.append(line._prepare_move_allocation_vals())
        self.env['lhm.material.consumption'].create(to_create)
        return True
