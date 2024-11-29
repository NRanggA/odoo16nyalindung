from odoo import api, fields, models, _
from odoo.exceptions import UserError

# class MaterialRequest(models.Model):
#     _inherit = 'material.request'
 
class MaterialRequestLine(models.Model):
    _inherit = 'material.request.line'

    varieties_id = fields.Many2one('plant.varieties', string="ORG", ondelete='restrict')
    location_type_id = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    filtered_locations = fields.Many2many('lhm.location', 'mrl_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    location_id = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    filtered_activities = fields.Many2many('lhm.activity', 'mrl_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    activity_id = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    no_line = fields.Boolean(string="No Line", related="location_type_id.no_line")
    
    # doc_activity_ids = fields.Many2many('lhm.activity', compute='_filtered_doc_activity_ids')

    # @api.depends('location_type_id','location_id')
    # def _filtered_doc_activity_ids(self):
    #     for line in self:
    #         if line.mr_id.state!='draft' or not line.location_type_id:
    #             line.doc_activity_ids = []
    #             continue
    #         activity_ids = []
    #         if line.location_type_id.code=='PJ' and line.location_id:
    #             # current_project = self.env['plantation.project'].search([('location_id','=',line.location_id.id)])
    #             current_project = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
    #             activity_ids = current_project.line_ids.mapped('activity_id').ids if current_project else []
    #         else:
    #             activity_ids = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)]).ids
            
    #         line.doc_activity_ids = [(6, 0, activity_ids)]

    # Menambahkan onchange tipe lokasi yang otomatis akan mengisi ke varieties_id 
    @api.onchange('location_type_id')
    def _onchange_location_type_id(self):
        if self.location_type_id:
            self.varieties_id = self.location_type_id.varieties_id.id

    @api.depends('varieties_id','location_type_id', 'mr_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.mr_id.state!='draft' or not line.location_type_id:
                line.filtered_locations = []
            else:
                if line.location_type_id.code in ('WS','VH','MA','LB'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # GC, IDC, PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'mr_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.mr_id.state!='draft' or not line.location_type_id:
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','lhm')], limit=1)
                if line.location_type_id and line.location_type_id.project and line.location_id:
                    projects = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
                    project_activity_ids = []
                    for project in projects:
                        # if doc_form:
                        #     project_activity_ids += [x.activity_id.id for x in project.line_ids if doc_form.id in x.doc_ids.ids]
                        # else:
                            project_activity_ids += [x.activity_id.id for x in project.line_ids]

                    if project_activity_ids:
                        line.filtered_activities = [(6, 0, project_activity_ids)]
                    else:
                        line.filtered_activities = []
                else:
                    if line.location_type_id.code in ('WS','VH','MA','NS','LB'):
                        activities = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])
                    else: # GC, IDC, PLANTATION
                        if line.varieties_id:
                            if line.location_type_id.general_charge:
                                activities = line.varieties_id.general_charges_activity_ids
                            elif line.location_type_id.indirect:
                                activities = line.varieties_id.indirect_cost_activity_ids
                            # Menambahkan tipe lokasi Mills 
                            elif line.location_type_id.mills:
                                activities = line.varieties_id.mill_costs_ids
                            else:
                                activities = line.varieties_id.harvest_activity_id
                                activities |= line.varieties_id.upkeep_activity_ids
                        else:
                            # activities = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])
                            activities = []
                    if False: #doc_form:
                        act_ids = []
                        for act in activities:
                            if doc_form.id in act.doc_ids.ids:
                                act_ids.append(act.id)
                        line.filtered_activities = [(6, 0, act_ids)]
                    else:
                        line.filtered_activities = [(6, 0, activities.ids)] if activities else []

    # Ini masih dipake, untuk tambahin Value di stock.move saat MR membuat otomatis Issue <stock.picking> 
    def _prepare_stock_move_vals(self, picking, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(picking, product_uom_qty, product_uom)
        res.update({
            'plantation_varieties_id' : self.varieties_id.id if self.varieties_id else False,
            'plantation_location_type_id' : self.location_type_id.id if self.location_type_id else False,
            'plantation_location_id' : self.location_id.id if self.location_id else False,
            'plantation_activity_id' : self.activity_id.id if self.activity_id else False,
        })
        return res    