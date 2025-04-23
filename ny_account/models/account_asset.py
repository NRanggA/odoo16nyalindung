from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    # boolean penanda 
    charge_to_activity          = fields.Boolean('Charge To Activity', default=False)

    # data yang akan di isi ketika boolean bernilai true
    location_type_id            = fields.Many2one('lhm.location.type', string='Tipe Lokasi')
    no_line                     = fields.Boolean(string="Mandatory", related="location_type_id.no_line")
    location_id                 = fields.Many2one('lhm.location', string='Lokasi')
    activity_id                 = fields.Many2one('lhm.activity', string="Aktivitas")
    varieties_id                = fields.Many2one('plant.varieties', string="ORG", ondelete='restrict')
    varieties_validator         = fields.Boolean(compute='_set_plantation_validator', store=True, string="Varieties Validator")
    @api.depends('location_type_id')
    def _set_plantation_validator(self):
        for line in self:
            validator = False
            if line.location_type_id:
                # Plantation FC, GC, IDC, PJ => True (artinya wajib diisi)
                validator = line.location_type_id.code in ('FC','GC','IDC','PJ')
            line.varieties_validator = validator

    filtered_locations          = fields.Many2many('lhm.location', 'asset_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    filtered_activities         = fields.Many2many('lhm.activity', 'asset_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')

    beginning_balance           = fields.Boolean('Beginning Balance', default=False, readonly=True, states={'draft': [('readonly', False)]})
    accumulated_depreciation    = fields.Monetary('Accumulated Depreciation', readonly=True, states={'draft': [('readonly', False)]})
    value_residual              = fields.Monetary(compute='_amount_residual', string='Residual Value')
    value                       = fields.Monetary(string='Gross Value', required=True, readonly=True, states={'draft': [('readonly', False)]})

    @api.depends('varieties_id','location_type_id', 'state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            # if line.state!='draft':
            #     line.filtered_locations = []
            # else:
                if line.location_type_id.code in ('WS','VH','MA','LB','NS','GC','MC'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION FC, PJ, IDC
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    
    @api.depends('varieties_id','location_type_id', 'location_id', 'state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            # if line.state!='draft':
            #     line.filtered_activities = []
            # else:
                doc_form = self.env['res.doc.type'].search([('code','=','bkt')], limit=1)
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
                    if line.location_type_id.code in ('WS','VH','MA','LB','NS'):
                        activities = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])
                    else: # GC, IDC, PLANTATION
                        if line.varieties_id:
                            if line.location_type_id.general_charge:
                                activities = line.varieties_id.general_charges_activity_ids
                            elif line.location_type_id.indirect:
                                activities = line.varieties_id.indirect_cost_activity_ids
                            # menambahkan tipe lokasi mills 
                            elif line.location_type_id.mills:
                                activities = line.varieties_id.mill_costs_ids
                            else:
                                activities = line.varieties_id.harvest_activity_ids
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
    


    @api.depends('accumulated_depreciation', 'value', 'salvage_value', 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount')
    def _amount_residual(self):
        for rec in self:
            total_amount = 0.0
            for line in rec.depreciation_line_ids:
                if line.move_check:
                    total_amount += line.amount
            if not rec.beginning_balance:
                rec.value_residual = rec.value - total_amount - rec.salvage_value
            else:
                rec.value_residual = rec.value - rec.accumulated_depreciation - total_amount - rec.salvage_value

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self, line):
        move_vals = super(AccountAssetDepreciationLine, self)._prepare_move(line)
        asset_id = line[0].asset_id
        
        if asset_id.charge_to_activity:
            move_line_2                 = move_vals['line_ids'][1][2]
            move_line_2['account_id']   = asset_id.activity_id.account_id.id if asset_id.activity_id and asset_id.activity_id.account_id else move_line_2['account_id']
            
            move_line_2['plantation_location_type_id']  = asset_id.location_type_id.id
            move_line_2['plantation_location_id']       = asset_id.location_id.id
            move_line_2['plantation_activity_id']       = asset_id.activity_id.id
            move_line_2['plantation_varieties_id']       = asset_id.varieties_id.id

        return move_vals
