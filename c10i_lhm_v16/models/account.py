from hashlib import sha256
from json import dumps

from odoo import models, api, fields, _
from odoo.exceptions import UserError



class account_period(models.Model):
    _inherit      = 'account.period'
    
    def close_period(self):
        for record in self:
            record.state = "done"
    
    def reopen_period(self):
        for record in self:
            record.state = "draft"
    

class AccountMove(models.Model):
    _inherit = "account.move"
    
    def _post(self, soft=True):
        default_loc_type = self.env['lhm.location.type'].search([('name', '=', '-')])
        for move in self:
            for line in move.line_ids:
                if not line.plantation_location_type_id:
                    line.plantation_location_type_id = default_loc_type and default_loc_type[0].id or False
        return super(AccountMove, self)._post(soft=soft)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    plantation_varieties_id = fields.Many2one('plant.varieties', string='ORG', ondelete='restrict')
    plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    filtered_locations = fields.Many2many('lhm.location', 'aml_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    plantation_location_id      = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
    filtered_activities = fields.Many2many('lhm.activity', 'aml_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    plantation_activity_id      = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")
    plantation_validator        = fields.Boolean(string="Plantation Validator", related="plantation_location_type_id.no_line")
    
    plantation_src_journal_id = fields.Many2one('account.journal', string="Asal Journal")
    
    @api.depends('plantation_varieties_id','plantation_location_type_id', 'move_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.move_id.state!='draft' or not line.plantation_location_type_id:
                line.filtered_locations = []
            else:
                if line.plantation_location_type_id.code in ('WS','VH','MA', 'MC'): # Menambahkan tipe Mills (MC)
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.plantation_location_type_id.id)])
                else: # GC, IDC, PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.plantation_location_type_id.id),('varieties_id','=',line.plantation_varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('plantation_varieties_id','plantation_location_type_id', 'plantation_location_id', 'move_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.move_id.state!='draft' or not line.plantation_location_type_id:
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','lhm')], limit=1)
                if line.plantation_location_type_id and line.plantation_location_type_id.project and line.plantation_location_id:
                    projects = self.env['lhm.project'].search([('location_id','=',line.plantation_location_id.id)])
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
                    # menambahkan Mills (MC)
                    if line.plantation_location_type_id.code in ('WS','VH','MA','NS', 'MC'):
                        activities = self.env['lhm.activity'].search([('type_id','=',line.plantation_location_type_id.id)])
                    else: # GC, IDC, PLANTATION
                        if line.plantation_varieties_id:
                            if line.plantation_location_type_id.general_charge:
                                activities = line.plantation_varieties_id.general_charges_activity_ids
                            elif line.plantation_location_type_id.indirect:
                                activities = line.plantation_varieties_id.indirect_cost_activity_ids
                            # menambahkan tipe lokasi mills 
                            elif line.plantation_location_type_id.mills:
                                activities = line.plantation_varieties_id.mill_costs_ids
                            else:
                                activities = line.plantation_varieties_id.harvest_activity_id
                                activities |= line.plantation_varieties_id.upkeep_activity_ids
                        else:
                            # activities = self.env['lhm.activity'].search([('type_id','=',line.plantation_location_type_id.id)])
                            activities = []
                    if False: #doc_form:
                        act_ids = []
                        for act in activities:
                            if doc_form.id in act.doc_ids.ids:
                                act_ids.append(act.id)
                        line.filtered_activities = [(6, 0, act_ids)]
                    else:
                        line.filtered_activities = [(6, 0, activities.ids)] if activities else []
    
    @api.onchange('plantation_location_type_id')
    def _onchange_plantation_location_type_id(self):
        if self.plantation_location_type_id:
            self.plantation_location_id = False
            self.plantation_activity_id = False
            
            # Menambahkan onchage ORG ketika memilih tipe lokasi
            self.plantation_varieties_id = self.plantation_location_type_id.varieties_id.id
            
            if self.plantation_location_type_id.no_line and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
                self.account_id = False
            else:
                self.account_id = self.plantation_location_type_id.account_id.id if self.plantation_location_type_id.account_id else False

    @api.onchange('plantation_location_id')
    def _onchange_plantation_location_id(self):
        if self.plantation_location_id:
            self.plantation_activity_id = False

    @api.onchange('plantation_activity_id')
    def _onchange_plantation_activity_id(self):
        if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
            self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False