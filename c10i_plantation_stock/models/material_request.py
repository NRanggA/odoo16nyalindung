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


    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    # cost_allocation_mark = fields.Selection(related='cost_allocation_id.mark', string='Allocation Mark', store=True)
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    doc_activity_ids    = fields.Many2many('lhm.activity', compute='_filtered_doc_activity_ids')

    # cost_allocation_id = location_type_id
    # cost_center_id = location_id
    # cost_activity_id = activity_id
    # filtered_cost_activity_ids = doc_activity_ids

    @api.depends('location_type_id','location_id')
    def _filtered_doc_activity_ids(self):
        for line in self:
            if line.mr_id.state!='draft' or not line.location_type_id:
                line.doc_activity_ids = []
                continue
            activity_ids = []
            if line.location_type_id.code=='PJ' and line.location_id:
                # current_project = self.env['plantation.project'].search([('location_id','=',line.location_id.id)])
                current_project = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
                activity_ids = current_project.line_ids.mapped('activity_id').ids if current_project else []
            else:
                activity_ids = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)]).ids
            
            line.doc_activity_ids = [(6, 0, activity_ids)]

    # Ini masih dipake, untuk tambahin Value di stock.move saat MR membuat otomatis Issue <stock.picking> 
    def _prepare_stock_move_vals(self, picking, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(picking, product_uom_qty, product_uom)
        res.update({
            'cost_allocation_id': self.location_type_id.id,
            'cost_center_id': self.location_id.id,
            'cost_activity_id': self.activity_id.id,
            # 'operating_unit_id': self.mr_id.operating_unit_id.id,
        })
        return res    