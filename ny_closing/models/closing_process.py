from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ClosingProcess(models.Model):
    _name = 'closing.process'
    _description = 'Closing Process'

    SELECTION = [('draft','New'),
        ('running_workshop', 'Running Workshop'),
        ('running_vehicle', 'Running Vehicle'),
        ('running_machine', 'Running Machine'),
        ('closing_project', 'Closing Project'),
        ('closing_nursery', 'Closing Nursery'),
        ('closing_plantation', 'Closing Plantation'),
        ('closing_production', 'Closing Production'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]

    date_from = fields.Date()
    date_to = fields.Date()
    state = fields.Selection(SELECTION, default='draft', string='Status')

    running_workshop_ids = fields.One2many('running.workshop', 'closing_process_id', string='Running Workshop')
    mark_running_workshop_is_done = fields.Boolean()
    running_vehicle_ids = fields.One2many('running.vehicle', 'closing_process_id', string='Running Vehicle')
    mark_running_vehicle_is_done = fields.Boolean()
    running_machine_ids = fields.One2many('running.machine', 'closing_process_id', string='Running Machine')
    mark_running_machine_is_done = fields.Boolean()
    closing_project_ids = fields.One2many('closing.project', 'closing_process_id', string='Closing Project')
    mark_closing_project_is_done = fields.Boolean()
    closing_nursery_ids = fields.One2many('closing.nursery', 'closing_process_id', string='Closing Nursery')
    mark_closing_nursery_is_done = fields.Boolean()
    closing_plantation_ids = fields.One2many('closing.plantation', 'closing_process_id', string='Closing Plantation')
    mark_closing_plantation_is_done = fields.Boolean()
    closing_production_ids = fields.One2many('closing.production', 'closing_process_id', string='Closing Production')
    mark_closing_production_is_done = fields.Boolean(compute='_compute_mark_done_production', store=True)

    @api.depends('closing_production_ids.state')
    def _compute_mark_done_production(self):
        for rec in self:
            if rec.closing_production_ids:
                if all([x.state=='done' for x in rec.closing_production_ids]):
                    rec.mark_closing_nursery_is_done = True
                else:
                    rec.mark_closing_nursery_is_done = False
            else:
                rec.mark_closing_nursery_is_done = False

    #################### BEGIN HELPER METHOD #####################
    def get_workshop(self):
        for rec in self:
            existing_run_ws = rec.running_workshop_ids
            if existing_run_ws:
                workshop = self.env['lhm.workshop'].search([('id','not in',rec.running_workshop_ids.workshop_id.ids)])
            else:
                workshop = self.env['lhm.workshop'].search([])
            
            to_insert = []
            for ws in workshop:
                to_insert.append((0,0,{
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'workshop_id': ws.id,
                }))
            if to_insert:
                rec.running_workshop_ids = to_insert
            
            if existing_run_ws:
                existing_run_ws.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def get_vehicle(self):
        for rec in self:
            existing_run_vh = rec.running_vehicle_ids
            if existing_run_vh:
                vehicle = self.env['lhm.utility'].search([('type','=','vh'),('id','not in',rec.running_vehicle_ids.vehicle_id.ids)])
            else:
                vehicle = self.env['lhm.utility'].search([('type','=','vh')])
            
            to_insert = []
            for vh in vehicle:
                to_insert.append((0,0,{
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'vehicle_id': vh.id,
                }))
            if to_insert:
                rec.running_vehicle_ids = to_insert
            
            if existing_run_vh:
                existing_run_vh.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def get_machine(self):
        for rec in self:
            existing_run_ma = rec.running_machine_ids
            if existing_run_ma:
                machine = self.env['lhm.utility'].search([('type','=','ma'),('id','not in',rec.running_machine_ids.machine_id.ids)])
            else:
                machine = self.env['lhm.utility'].search([('type','=','ma')])
            
            to_insert = []
            for ma in machine:
                to_insert.append((0,0,{
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'machine_id': ma.id,
                }))
            if to_insert:
                rec.running_machine_ids = to_insert
            
            if existing_run_ma:
                existing_run_ma.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def get_project(self):
        for rec in self:
            existing_cl_pj = rec.closing_project_ids
            if existing_cl_pj:
                project = self.env['lhm.project'].search([('id','not in',rec.closing_project_ids.project_id.ids)])
            else:
                project = self.env['lhm.project'].search([])
            
            to_insert = []
            for pj in project:
                to_insert.append((0,0,{
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'project_id': pj.id,
                }))
            if to_insert:
                rec.closing_project_ids = to_insert
            
            if existing_cl_pj:
                existing_cl_pj.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def get_nursery(self):
        for rec in self:
            existing_cl_nurs = rec.closing_nursery_ids
            if existing_cl_nurs:
                nursery = self.env['lhm.nursery'].search([('id','not in',rec.closing_nursery_ids.nursery_id.ids)])
            else:
                nursery = self.env['lhm.nursery'].search([])
            
            to_insert = []
            for ns in nursery:
                to_insert.append((0,0,{
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'nursery_id': ns.id,
                }))
            if to_insert:
                rec.closing_nursery_ids = to_insert
            
            if existing_cl_nurs:
                existing_cl_nurs.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def get_plantation(self):
        for rec in self:
            existing_cl_plant = rec.closing_plantation_ids
            if existing_cl_plant:
                plant_blocks = self.env['lhm.plant.block'].search([('id','not in',rec.closing_plantation_ids.plant_block_id.ids)])
            else:
                plant_blocks = self.env['lhm.plant.block'].search([])
            
            to_insert = []
            for plb in plant_blocks:
                to_insert.append((0,0,{
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'plant_block_id': plb.id,
                }))
            if to_insert:
                rec.closing_plantation_ids = to_insert
            
            if existing_cl_plant:
                existing_cl_plant.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def get_production(self):
        for rec in self:
            if not rec.closing_production_ids:
                rec.closing_production_ids = [(0,0,{
                        'date_from': rec.date_from, 'date_to': rec.date_to,
                    })]

    #################### END HELPER METHOD #####################

    #################### BEGIN WORKFLOW METHOD #####################
    def button_start(self):
        self.get_workshop()
        self.write({'state': 'running_workshop'})
    
    def button_continue_to_running_vehicle(self):
        for rec in self:
            if not rec.mark_running_workshop_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            self.get_vehicle()
            rec.write({'state': 'running_vehicle'})
            # rec.compute_initial_and_cost_fg2()
        return True

    def button_continue_to_running_machine(self):
        for rec in self:
            if not rec.mark_running_vehicle_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_machine()
            rec.write({'state': 'running_machine'})
            # rec.compute_initial_and_cost_fg2()
        return True

    def button_continue_to_closing_project(self):
        for rec in self:
            if not rec.mark_running_machine_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_project()
            rec.write({'state': 'closing_project'})
            # rec.compute_initial_and_cost_fg2()
        return True

    def button_continue_to_closing_nursery(self):
        for rec in self:
            if not rec.mark_closing_project_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_nursery()
            rec.write({'state': 'closing_nursery'})
            # rec.compute_initial_and_cost_fg2()
        return True

    def button_continue_to_closing_plantation(self):
        for rec in self:
            if not rec.mark_closing_nursery_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_plantation()
            rec.write({'state': 'closing_plantation'})
            # rec.compute_initial_and_cost_fg2()
        return True

    def button_continue_to_closing_production(self):
        for rec in self:
            if not rec.mark_closing_plantation_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_production()
            rec.write({'state': 'closing_production'})
            # rec.compute_initial_and_cost_fg2()
        return True
    
    def action_done(self):
        for rec in self:
            if not rec.mark_closing_production_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.write({'state': 'done'})
    
    def button_back(self):
        selection_key = list(map(lambda x: x[0], self.SELECTION))
        for rec in self:
            index_state = selection_key.index(rec.state)
            if index_state:
                rec.state = selection_key[index_state-1]
    
    def button_cancel(self):
        selection_key = list(map(lambda x: x[0], self.SELECTION))
        self.filtered(lambda x: x.state in selection_key[:8]).write({'state':'cancel'})
        return True
    
    def button_set_new(self):
        self.filtered(lambda x: x.state=='cancel').write({'state':'draft'})
        return True
    #################### END WORKFLOW METHOD #####################

    #################### BEGIN OPERATION METHOD #####################
    def action_open_running_workshop(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.running_workshop_action")
        action['domain'] = [('id','in',self.running_workshop_ids.ids)]
        return action
    
    def action_open_output_journal_workshop(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['domain'] = [('id','in',self.running_workshop_ids.running_move_id.ids)]
        return action
    
    def action_open_all_move_line_workshop(self):
        src_move_lines = self.env['account.move.line'].search([('plantation_location_type_id','=',self.running_workshop_ids.workshop_id.location_id.type_id.ids),
            ('plantation_location_id','in',self.running_workshop_ids.workshop_id.location_id.ids),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('parent_state','=','posted')])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        ids_to_show = self.running_workshop_ids.running_move_id.line_ids.ids
        if src_move_lines:
            ids_to_show.extend(src_move_lines.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action

    def action_open_running_vehicle(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.running_vehicle_action")
        action['domain'] = [('id','in',self.running_vehicle_ids.ids)]
        return action

    def action_open_output_journal_vehicle(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['domain'] = [('id','in',self.running_vehicle_ids.running_move_id.ids)]
        return action
    
    def action_open_all_move_line_vehicle(self):
        src_move_lines = self.env['account.move.line'].search([('plantation_location_type_id','in',self.running_workshop_ids.vehicle_id.location_id.type_id.ids),
            ('plantation_location_id','in',self.running_workshop_ids.vehicle_id.location_id.ids),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('parent_state','=','posted')])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        ids_to_show = self.running_workshop_ids.running_move_id.line_ids.ids
        if src_move_lines:
            ids_to_show.extend(src_move_lines.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action
    
    def action_open_running_machine(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.running_machine_action")
        action['domain'] = [('id','in',self.running_machine_ids.ids)]
        return action
    
    def action_open_closing_project(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_project_action")
        action['domain'] = [('id','in',self.closing_project_ids.ids)]
        return action
    
    def action_open_closing_nursery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_nursery_action")
        action['domain'] = [('id','in',self.closing_nursery_ids.ids)]
        return action

    def action_open_closing_plantation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_plantation_action")
        action['domain'] = [('id','in',self.closing_plantation_ids.ids)]
        return action

    def action_open_closing_production(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_production_action")
        action['views'] = [(self.env.ref("ny_closing.closing_production_view_form").id, "form")]
        action['res_id'] = self.closing_production_ids.id
        action['domain'] = [('id','=',self.closing_production_ids.id)]
        return action
    #################### END OPERATION METHOD #####################
