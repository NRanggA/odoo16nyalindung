from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

from lxml import etree

import logging
_logger = logging.getLogger(__name__)

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

    counterpart_running_ws_account_id = fields.Many2one('account.account', string='Counterpart Running WS Account')
    running_workshop_ids = fields.One2many('running.workshop', 'closing_process_id', string='Running Workshop')
    mark_running_workshop_is_done = fields.Boolean()
    counterpart_running_vh_account_id = fields.Many2one('account.account', string='Counterpart Running VH Account')
    running_vehicle_ids = fields.One2many('running.vehicle', 'closing_process_id', string='Running Vehicle')
    mark_running_vehicle_is_done = fields.Boolean()
    counterpart_running_ma_account_id = fields.Many2one('account.account', string='Counterpart Running MA Account')
    running_machine_ids = fields.One2many('running.machine', 'closing_process_id', string='Running Machine')
    mark_running_machine_is_done = fields.Boolean()
    counterpart_closing_pj_account_id = fields.Many2one('account.account', string='Counterpart Closing Project Account')
    closing_project_ids = fields.One2many('closing.project', 'closing_process_id', string='Closing Project')
    mark_closing_project_is_done = fields.Boolean()
    counterpart_closing_ns_account_id = fields.Many2one('account.account', string='Counterpart Closing Nursery Account')
    closing_nursery_ids = fields.One2many('closing.nursery', 'closing_process_id', string='Closing Nursery')
    mark_closing_nursery_is_done = fields.Boolean()
    counterpart_closing_plant_account_id = fields.Many2one('account.account', string='Counterpart Closing Plantation Account')
    closing_plantation_ids = fields.One2many('closing.plantation', 'closing_process_id', string='Closing Plantation')
    mark_closing_plantation_is_done = fields.Boolean()
    closing_production_ids = fields.One2many('closing.production', 'closing_process_id', string='Closing Production')
    mark_closing_production_is_done = fields.Boolean(compute='_compute_mark_done_production', store=True)

    @api.model
    def get_views(self, views, options=None):
        result = super(ClosingProcess, self).get_views(views, options=options)
        if self._context.get('params',{}).get('id',0)>0:
            res_active_rec = self.search_read([('id','=',self._context['params']['id'])], ['state'])
            if res_active_rec and res_active_rec[0]['state'] not in ('draft','cancel'):
                form_arch = etree.fromstring(result['views']['form']['arch'])
                page_name_active = res_active_rec[0]['state']
                if page_name_active=='done':
                    page_name_active = 'closing_production'
                for node in form_arch.xpath(f"//page[@name='{page_name_active}']"):
                    node.set("autofocus", "autofocus")
                result['views']['form']['arch'] = etree.tostring(form_arch, encoding="unicode").replace('\t', '')
        return result

    @api.onchange('counterpart_running_ws_account_id')
    def onchange_counterpart_running_ws_account(self):
        if self.counterpart_running_ws_account_id:
            self.running_workshop_ids.write({'closing_account_id': self.counterpart_running_ws_account_id.id})

    @api.onchange('counterpart_running_vh_account_id')
    def onchange_counterpart_running_vh_account(self):
        if self.counterpart_running_vh_account_id:
            self.running_vehicle_ids.write({'closing_account_id': self.counterpart_running_vh_account_id.id})
    
    @api.onchange('counterpart_running_ma_account_id')
    def onchange_counterpart_running_ma_account(self):
        if self.counterpart_running_ma_account_id:
            self.running_machine_ids.write({'closing_account_id': self.counterpart_running_ma_account_id.id})

    @api.onchange('counterpart_closing_pj_account_id')
    def onchange_counterpart_closing_pj_account(self):
        if self.counterpart_closing_pj_account_id:
            self.closing_project_ids.write({'closing_account_id': self.counterpart_closing_pj_account_id.id})
    
    @api.onchange('counterpart_closing_ns_account_id')
    def onchange_counterpart_closing_ns_account(self):
        if self.counterpart_closing_ns_account_id:
            self.closing_nursery_ids.write({'closing_account_id': self.counterpart_closing_ns_account_id.id})
    
    @api.onchange('counterpart_closing_plant_account_id')
    def onchange_counterpart_closing_plant_account(self):
        if self.counterpart_closing_plant_account_id:
            self.closing_plantation_ids.write({'closing_account_id': self.counterpart_closing_plant_account_id.id})
    
    @api.depends('closing_production_ids.state')
    def _compute_mark_done_production(self):
        for rec in self:
            if rec.closing_production_ids:
                if all([x.state=='done' for x in rec.closing_production_ids]):
                    rec.mark_closing_production_is_done = True
                else:
                    rec.mark_closing_production_is_done = False
            else:
                rec.mark_closing_production_is_done = False

    #################### BEGIN HELPER METHOD #####################
    def get_workshop(self):
        for rec in self:
            existing_run_ws = rec.running_workshop_ids
            if existing_run_ws:
                workshop = self.env['lhm.utility'].search([('type','=','ws'),('id','not in',rec.running_workshop_ids.workshop_id.ids)])
            else:
                workshop = self.env['lhm.utility'].search([('type','=','ws')])
            
            to_insert = []
            for ws in workshop:
                to_insert.append((0,0,{
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'workshop_id': ws.id,
                    'closing_account_id': rec.counterpart_running_ws_account_id.id,
                }))
            if to_insert:
                rec.running_workshop_ids = to_insert
            
            if existing_run_ws:
                existing_run_ws.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to,
                    'closing_account_id': rec.counterpart_running_ws_account_id.id,
                })
    
    def summerize_workshop_cost(self):
        for rec in self:
            rec.running_workshop_ids.summarize_move_line()
    def create_account_move_workshop(self):
        for rec in self:
            rec.running_workshop_ids.create_account_move()
            rec.running_workshop_ids.running_move_id._post(soft=False)

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
                    'closing_account_id': rec.counterpart_running_vh_account_id.id,
                }))
            if to_insert:
                rec.running_vehicle_ids = to_insert
            
            if existing_run_vh:
                existing_run_vh.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def summerize_vehicle_cost(self):
        for rec in self:
            rec.running_vehicle_ids.summarize_move_line()
    def create_account_move_vehicle(self):
        for rec in self:
            rec.running_vehicle_ids.create_account_move()
            rec.running_vehicle_ids.running_move_id._post(soft=False)
    
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
                    'closing_account_id': rec.counterpart_running_ma_account_id.id,
                }))
            if to_insert:
                rec.running_machine_ids = to_insert
            
            if existing_run_ma:
                existing_run_ma.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def summerize_machine_cost(self):
        for rec in self:
            rec.running_machine_ids.summarize_move_line()
    def create_account_move_machine(self):
        for rec in self:
            rec.running_machine_ids.create_account_move()
            rec.running_machine_ids.running_move_id._post(soft=False)
    
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
                    'closing_account_id': rec.counterpart_closing_pj_account_id.id,
                }))
            if to_insert:
                rec.closing_project_ids = to_insert
            
            if existing_cl_pj:
                existing_cl_pj.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def summerize_project_cost(self):
        for rec in self:
            rec.closing_project_ids.summarize_move_line()
    def create_account_move_project(self):
        for rec in self:
            rec.closing_project_ids.create_account_move()
            rec.closing_project_ids.closing_move_id._post(soft=False)

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
                    'closing_account_id': rec.counterpart_closing_ns_account_id.id,
                }))
            if to_insert:
                rec.closing_nursery_ids = to_insert
            
            if existing_cl_nurs:
                existing_cl_nurs.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def summerize_nursery_cost(self):
        for rec in self:
            rec.closing_nursery_ids.compute_initial_and_cost_value()
    def create_account_move_nursery(self):
        for rec in self:
            rec.closing_nursery_ids.create_account_move()
            rec.closing_nursery_ids.closing_move_id._post(soft=False)

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
                    'closing_account_id': rec.counterpart_closing_plant_account_id.id,
                }))
            if to_insert:
                rec.closing_plantation_ids = to_insert
            
            if existing_cl_plant:
                existing_cl_plant.write({
                    'date_from': rec.date_from, 'date_to': rec.date_to
                })
    
    def summerize_plantation_cost(self):
        for rec in self:
            rec.closing_plantation_ids.summarize_move_line()
    def create_account_move_plantation(self):
        for rec in self:
            rec.closing_plantation_ids.create_account_move()
            rec.closing_plantation_ids.closing_move_id._post(soft=False)
    
    def get_production(self):
        for rec in self:
            if not rec.closing_production_ids:
                vals = {
                        'date_from': rec.date_from, 'date_to': rec.date_to, 
                    }
                prev_closing = self.env['closing.production'].search([('date_to','<',rec.date_from),('state','=','done')], order='date_from desc', limit=1)
                if prev_closing:
                    vals.update({'prev_closing_id': prev_closing.id,
                        'latex_inventory_account_id': prev_closing.latex_inventory_account_id.id if prev_closing.latex_inventory_account_id else False,
                        'latex_wip_account_id': prev_closing.latex_wip_account_id.id if prev_closing.latex_wip_account_id else False,
                        'latex_consumption_account_id': prev_closing.latex_consumption_account_id.id if prev_closing.latex_consumption_account_id else False,
                        'lump_inventory_account_id': prev_closing.lump_inventory_account_id.id if prev_closing.lump_inventory_account_id else False,
                        'lump_wip_account_id': prev_closing.lump_wip_account_id.id if prev_closing.lump_wip_account_id else False,
                        'lump_consumption_account_id': prev_closing.lump_consumption_account_id.id if prev_closing.lump_consumption_account_id else False,
                        'sheet_inventory_account_id': prev_closing.sheet_inventory_account_id.id if prev_closing.sheet_inventory_account_id else False,
                        'sheet_wip_account_id': prev_closing.sheet_wip_account_id.id if prev_closing.sheet_wip_account_id else False,
                        'sheet_consumption_account_id': prev_closing.sheet_consumption_account_id.id if prev_closing.sheet_consumption_account_id else False,
                        'manufacturing_cost_account_ids': [(6,0,prev_closing.manufacturing_cost_account_ids.ids)] if prev_closing.manufacturing_cost_account_ids else False,
                    })
                rec.closing_production_ids = [(0,0,vals)]

    #################### END HELPER METHOD #####################

    #################### BEGIN WORKFLOW METHOD #####################
    def button_start(self):
        # Get Previous Closing Process
        for rec in self:
            prev_closing = self.search([('state','=','closing_production'),('date_to','<',rec.date_from)], order='date_from desc', limit=1)
            rec.write({
                'counterpart_running_ws_account_id': prev_closing.counterpart_running_ws_account_id.id if prev_closing and prev_closing.counterpart_running_ws_account_id else False,
                'counterpart_running_vh_account_id': prev_closing.counterpart_running_vh_account_id.id if prev_closing and prev_closing.counterpart_running_vh_account_id else False,
                'counterpart_running_ma_account_id': prev_closing.counterpart_running_ma_account_id.id if prev_closing and prev_closing.counterpart_running_ma_account_id else False,
                'counterpart_closing_pj_account_id': prev_closing.counterpart_closing_pj_account_id.id if prev_closing and prev_closing.counterpart_closing_pj_account_id else False,
                'counterpart_closing_ns_account_id': prev_closing.counterpart_closing_ns_account_id.id if prev_closing and prev_closing.counterpart_closing_ns_account_id else False,
                'counterpart_closing_plant_account_id': prev_closing.counterpart_closing_plant_account_id.id if prev_closing and prev_closing.counterpart_closing_plant_account_id else False,
            })
            rec.get_workshop()
            rec.state = 'running_workshop'
    
    def button_continue_to_running_vehicle(self):
        for rec in self:
            if not rec.mark_running_workshop_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_vehicle()
            rec.write({'state': 'running_vehicle'})
            # rec.compute_initial_and_cost_fg2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_continue_to_running_machine(self):
        for rec in self:
            if not rec.mark_running_vehicle_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_machine()
            rec.write({'state': 'running_machine'})
            # rec.compute_initial_and_cost_fg2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_continue_to_closing_project(self):
        for rec in self:
            if not rec.mark_running_machine_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_project()
            rec.write({'state': 'closing_project'})
            # rec.compute_initial_and_cost_fg2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_continue_to_closing_nursery(self):
        for rec in self:
            if not rec.mark_closing_project_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_nursery()
            rec.write({'state': 'closing_nursery'})
            # rec.compute_initial_and_cost_fg2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_continue_to_closing_plantation(self):
        for rec in self:
            if not rec.mark_closing_nursery_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_plantation()
            rec.write({'state': 'closing_plantation'})
            # rec.compute_initial_and_cost_fg2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_continue_to_closing_production(self):
        for rec in self:
            if not rec.mark_closing_plantation_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_production()
            rec.write({'state': 'closing_production'})
            # rec.compute_initial_and_cost_fg2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
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
                rec.write({'state': selection_key[index_state-1],
                    f"mark_{selection_key[index_state-1]}_is_done": False})
    
    def button_cancel(self):
        selection_key = list(map(lambda x: x[0], self.SELECTION))
        self.filtered(lambda x: x.state in selection_key[:8]).write({
                'state':'cancel',
                'mark_running_workshop_is_done': False,
                'mark_running_vehicle_is_done': False,
                'mark_running_machine_is_done': False,
                'mark_closing_project_is_done': False,
                'mark_closing_nursery_is_done': False,
                'mark_closing_plantation_is_done': False,
                'mark_closing_production_is_done': False,
            })
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
        src_move_lines = self.env['account.move.line'].search([('plantation_location_type_id','in',self.running_vehicle_ids.vehicle_id.location_id.type_id.ids),
            ('plantation_location_id','in',self.running_vehicle_ids.vehicle_id.location_id.ids),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('parent_state','=','posted')])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        ids_to_show = self.running_vehicle_ids.running_move_id.line_ids.ids
        if src_move_lines:
            ids_to_show.extend(src_move_lines.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action
    
    def action_open_running_machine(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.running_machine_action")
        action['domain'] = [('id','in',self.running_machine_ids.ids)]
        return action

    def action_open_output_journal_machine(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['domain'] = [('id','in',self.running_machine_ids.running_move_id.ids)]
        return action
    
    def action_open_all_move_line_machine(self):
        src_move_lines = self.env['account.move.line'].search([('plantation_location_type_id','in',self.running_machine_ids.machine_id.location_id.type_id.ids),
            ('plantation_location_id','in',self.running_machine_ids.machine_id.location_id.ids),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('parent_state','=','posted')])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        ids_to_show = self.running_machine_ids.running_move_id.line_ids.ids
        if src_move_lines:
            ids_to_show.extend(src_move_lines.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action
    
    def action_open_closing_project(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_project_action")
        action['domain'] = [('id','in',self.closing_project_ids.ids)]
        return action

    def action_open_output_journal_project(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['domain'] = [('id','in',self.closing_project_ids.closing_move_id.ids)]
        return action
    
    def action_open_all_move_line_project(self):
        src_move_lines = self.env['account.move.line'].search([('plantation_location_type_id','in',self.closing_project_ids.project_id.location_id.type_id.ids),
            ('plantation_location_id','in',self.closing_project_ids.project_id.location_id.ids),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('parent_state','=','posted')])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        ids_to_show = self.closing_project_ids.closing_move_id.line_ids.ids
        if src_move_lines:
            ids_to_show.extend(src_move_lines.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action
    
    def action_open_closing_nursery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_nursery_action")
        action['domain'] = [('id','in',self.closing_nursery_ids.ids)]
        return action
    
    def action_open_output_journal_nursery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        # action['domain'] = [('id','in',self.closing_nursery_ids.closing_move_id.ids)]
        ids_to_show = self.closing_nursery_ids.closing_out_move_ids.ids or []
        ids_to_show.extend(self.closing_nursery_ids.closing_move_id.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action
    
    def action_open_all_move_line_nursery(self):
        src_move_lines = self.env['account.move.line'].search([('plantation_location_type_id','in',self.closing_nursery_ids.nursery_id.location_id.type_id.ids),
            ('plantation_location_id','in',self.closing_nursery_ids.nursery_id.location_id.ids),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('parent_state','=','posted')])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        ids_to_show = self.closing_nursery_ids.closing_move_id.line_ids.ids
        if self.closing_nursery_ids.closing_out_move_ids:
            ids_to_show.extend(self.closing_nursery_ids.closing_out_move_ids.line_ids.ids)
        if src_move_lines:
            ids_to_show.extend(src_move_lines.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action

    def action_open_closing_plantation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_plantation_action")
        action['domain'] = [('id','in',self.closing_plantation_ids.ids)]
        return action

    def action_open_output_journal_plantation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['domain'] = [('id','in',self.closing_plantation_ids.closing_move_id.ids)]
        return action
    
    def action_open_all_move_line_plantation(self):
        src_move_lines = self.env['account.move.line'].search([('plantation_location_type_id','in',self.closing_plantation_ids.plant_block_id.location_id.type_id.ids),
            ('plantation_location_id','in',self.closing_plantation_ids.plant_block_id.location_id.ids),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('parent_state','=','posted')])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        ids_to_show = self.closing_plantation_ids.closing_move_id.line_ids.ids
        if src_move_lines:
            ids_to_show.extend(src_move_lines.ids)
        action['domain'] = [('id','in',ids_to_show)]
        return action

    def action_open_closing_production(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.closing_production_action")
        action['views'] = [(self.env.ref("ny_closing.closing_production_view_form").id, "form")]
        action['res_id'] = self.closing_production_ids.id
        action['domain'] = [('id','=',self.closing_production_ids.id)]
        return action
    #################### END OPERATION METHOD #####################
