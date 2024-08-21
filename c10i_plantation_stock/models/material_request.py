from odoo import api, fields, models, _
from odoo.exceptions import UserError

# class MaterialRequest(models.Model):
#     _inherit = 'material.request'
 
class MaterialRequestLine(models.Model):
    _inherit = 'material.request.line'

    location_type_id = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    location_id = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    activity_id = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    doc_activity_ids = fields.Many2many('lhm.activity', compute='_filtered_doc_activity_ids')

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
            'plantation_location_type_id' : self.location_type_id.id if self.location_type_id else False,
            'plantation_location_id' : self.location_id.id if self.location_id else False,
            'plantation_activity_id' : self.activity_id.id if self.activity_id else False,
        })
        return res    