from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError,UserError
from datetime import date

today = date.today()

class LHM(models.Model):
    _inherit = 'lhm.transaction'

    consumed_material_ids = fields.One2many('lhm.material.consumption', 'lhm_id', string='Consumed Material')

    def action_outstanding_material(self):
        for rec in self:
            to_write = []
            for line in rec.material_line_ids:
                if (line.residual_qty - line.realization) < 0.0:
                    raise UserError(_("Picking %s doesn't have enough quantity") % line.product_id.name)
                else:
                    to_write.append({                        
                        'stock_move_id': line.move_id.id,
                        'lhm_id': rec.id,
                        'mr_id': line.move_id.mr_line_id.mr_id.id,
                        'lhm_material_id': line.id,
                        'product_qty': line.realization,
                    })

            if to_write:
                rec.consumed_material_ids = list(map(lambda x:(0,0,x), to_write))
        return True

    def button_confirm(self):
        res = super().button_confirm()
        for rec in self:
            rec.action_outstanding_material()
        return res

class LhmMaterialLine(models.Model):
    _inherit = 'lhm.transaction.material.line'

    stock_move_id = fields.Many2one("stock.move", string="Origin Move", ondelete="restrict")
    residual_qty = fields.Float(related='move_id.allocation_residual_qty', store=True, string='Residual Qty')

    stock_allocation_ids = fields.One2many('lhm.material.consumption', 'lhm_material_id', string='Allocations')

    def _prepare_move_allocation_vals(self):
        return {
                'stock_move_id':  self.stock_move_id.id,
                'lhm_line_id' : self.id,
                'product_qty' : self.consumed_qty,
            }

    def action_stock_move_create(self):
        to_create = []
        for line in self:
            if (line.residual_qty - line.consumed_qty) < 0.0:
                raise UserError(_("Picking %s doesnt have enough quantity")%line.name)
            to_create.append(line._prepare_move_allocation_vals())
        self.env['plantation.material.allocation'].create(to_create)        
        return True
