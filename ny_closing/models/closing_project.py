from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class ClosingProjectPlantDeferred(models.Model):
    _name = 'closing.project.plant.deferred' 
    _description = 'Closing Project - Plantation Deffered Cost'

    closing_id = fields.Many2one('closing.project', string='Closing Plantation')
    plantation_location_type_id = fields.Many2one('lhm.location.type', string='Tipe Lokasi', ondelete='restrict')
    plantation_location_id = fields.Many2one('lhm.location', string='Lokasi', ondelete='restrict')
    plantation_activity_id = fields.Many2one('lhm.activity', string='Aktivitas', ondelete='restrict')
    plantation_src_journal_id = fields.Many2one('account.journal', string='Asal Jurnal', ondelete='restrict')
    dest_account_id = fields.Many2one('account.account', string='Dest. Cost Account', ondelete='restrict')
    deferred_cost = fields.Float('Deferred')
    new_deferred_cost = fields.Float('New Deferred')
    accumulated_cost = fields.Float('Consumed Cost')
    residual_deferred = fields.Float(compute='_compute_cost', store=True, string="Residual")
    pct_cost_to_post = fields.Float("Pct (%)")
    cost_to_post = fields.Float(compute='_compute_cost', store=True, string="Cost to Consume")
    new_residual_deferred = fields.Float(compute='_compute_cost', store=True, string="New Residual")

    @api.depends('new_deferred_cost', 
            'deferred_cost', 
            'accumulated_cost', 
            'pct_cost_to_post', 
            'closing_id.pct_deferred_to_cost')
    def _compute_cost(self):
        for line in self:
            line.residual_deferred = line.deferred_cost + line.new_deferred_cost - line.accumulated_cost
            line.cost_to_post = ((line.deferred_cost + line.new_deferred_cost) - line.accumulated_cost) * line.pct_cost_to_post / 100.0
            line.new_residual_deferred = line.residual_deferred - line.cost_to_post
    
    def _get_domain_deferred_move_lines(self):
        src_account_id = self.closing_id.project_id.categ_id.account_id
        if not src_account_id:
            raise ValidationError(_(f"Could not find defered account inside Blok Tanam {self.closing_id.project_id.plant_block_id.code}"))
        domain = [('plantation_location_type_id','=',self.closing_id.project_id.location_type_id.id),
                ('plantation_location_id','=',self.closing_id.project_id.location_id.id),
                ('parent_state','=','posted'),('date','<',self.closing_id.date_from),
                ('account_id','=',src_account_id)]
        return domain

    def action_view_deferred_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_deferred_move_lines()
        return action

class ClosingProjectPlantLine(models.Model):
    _name = 'closing.project.plant.line' 
    _description = 'Closing Project - Plantation Current Cost'

    closing_id = fields.Many2one('closing.project', string='Closing Plantation')
    date_from = fields.Date()
    date_to = fields.Date()
    plantation_location_type_id = fields.Many2one('lhm.location.type', string='Tipe Lokasi', ondelete='restrict')
    plantation_location_id = fields.Many2one('lhm.location', string='Lokasi', ondelete='restrict')
    plantation_activity_id = fields.Many2one('lhm.activity', string='Aktivitas', ondelete='restrict')
    plantation_src_journal_id = fields.Many2one('account.journal', string='Asal Jurnal', ondelete='restrict')
    to_be_deferred = fields.Boolean()
    dest_account_id = fields.Many2one('account.account', string='Dest. Cost Account', ondelete='restrict')
    total_cost = fields.Float()

    def _get_domain_source_move_lines(self):
        src_account_ids = self.closing_id.project_id.line_ids.activity_id.account_id.ids
        if not src_account_ids:
            raise ValidationError(_(f"Could not find accounts for all related activity inside Location Type {self.plant_block_id.location_id.type_id.code}"))
        domain = [('plantation_location_id','=',self.closing_id.project_id.location_id.id),
                ('parent_state','=','posted'),('date','>=',self.closing_id.date_from),('date','<=',self.closing_id.date_to)]
        if len(src_account_ids)==1:
            domain.append(('account_id','=',src_account_ids[0]))
        else:
            domain.append(('account_id','in',src_account_ids))
        return domain
    
    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_source_move_lines()
        return action

class ClosingProject(models.Model):
    _name = 'closing.project' 
    _description = 'Closing Project Procedure'
    _rec_name = 'project_id'

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    # domain="[('state','=', ['in_progress','done'])]"
    project_id = fields.Many2one('lhm.project', string='Project', ondelete='restrict', required=True)
    project_tanaman = fields.Boolean(related='project_id.project_tanaman', store=True)
    closing_account_id = fields.Many2one('account.account', string='Closing Account')
    dest_account_id = fields.Many2one('account.account', compute='_compute_dest_account', readonly=False, string='Dest. Account')
    total_cost = fields.Float()

    mark_project_period = fields.Selection([('none','None'),('inprogress','In Progress'),('done','Done'),('preharvest','Pre-Harvesting'),('harvesting','Harvesting')], compute='_compute_mark', string='Project Mark')

    cost_line_ids = fields.One2many('closing.project.plant.line', 'closing_id')
    cost_line_to_be_deferred_ids = fields.One2many('closing.project.plant.line', 'closing_id', domain=[('to_be_deferred','=',True)], string="Cost to be Deferred")
    cost_line_as_cost_ids = fields.One2many('closing.project.plant.line', 'closing_id', domain=[('to_be_deferred','=',False)], string="Cost to be Consumed")
    pct_deferred_to_cost = fields.Float()
    deferred_cost_line_ids = fields.One2many('closing.project.plant.deferred', 'closing_id')

    closing_move_id = fields.Many2one('account.move', string='Journal Entry')

    @api.depends('project_id')
    def _compute_dest_account(self):
        for closing in self:
            closing.dest_account_id = closing.project_id.categ_id.account_id.id
    
    @api.depends('project_id')
    def _compute_mark(self):
        for closing in self:
            new_mark_project_period = 'none'
            if closing.project_id.project_tanaman:
                if closing.date_to>=closing.project_id.harvest_date_schedule:
                    new_mark_project_period = 'harvesting'
                else:
                    new_mark_project_period = 'preharvest'
            else:
                if closing.project_id.state=='done':
                    new_mark_project_period = 'done'
                else:
                    new_mark_project_period = 'inprogress'
            closing.mark_project_period = new_mark_project_period
    
    @api.onchange('pct_deferred_to_cost')
    def onchange_pct_deferred_to_cost(self):
        self.deferred_cost_line_ids.write({'pct_cost_to_post': self.pct_deferred_to_cost})

    def init(self):
        _logger.info("Create SUMMARY CLOSING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.procedure_summerize_project_plant_cost(
                        p_closing_project_id integer, p_project_id integer, 
                        p_date_from date, p_date_to date, p_to_be_deferred boolean,
                        p_user_id integer, p_company_id integer) 
            RETURNS void AS
            $BODY$
            DECLARE
                v_location_type integer;
                v_location integer;
                sums_cost_aml record;
                v_current_period_cost numeric := 0.0;
            BEGIN
                select location_type_id from lhm_project where id=p_project_id INTO v_location_type;
                select location_id from lhm_project where id=p_project_id INTO v_location;
            
                FOR sums_cost_aml IN SELECT 
                                aml1.plantation_location_type_id,
                                aml1.plantation_location_id,
                                aml1.plantation_activity_id,
                                aml1.plantation_src_journal_id,
                                SUM(aml1.debit - aml1.credit) as cost 
                            FROM account_move_line aml1
                            WHERE 
                                aml1.date>=p_date_from 
                                and aml1.date<=p_date_to 
                                and aml1.parent_state='posted'
                                and aml1.plantation_location_type_id=v_location_type
                                and aml1.plantation_location_id=v_location
                                and aml1.account_id in (select account_id from lhm_activity where 
                                    id in (select activity_id from lhm_project_line where project_id=p_project_id))
                            GROUP BY aml1.plantation_location_type_id,
                                aml1.plantation_location_id,
                                aml1.plantation_activity_id,
                                aml1.plantation_src_journal_id
                LOOP
                    -- v_current_period_cost := v_current_period_cost + sums_cost_aml.cost;
                    INSERT INTO closing_project_plant_line
                            (id, closing_id,  
                            date_from, date_to, 
                            plantation_location_type_id, plantation_location_id, 
                            plantation_activity_id, plantation_src_journal_id, 
                            to_be_deferred, total_cost,
                            create_uid, write_uid, create_date, write_date) 
                        VALUES (
                            nextval('closing_project_plant_line_id_seq'),
                            p_closing_project_id,
                            p_date_from, 
                            p_date_to,
                            sums_cost_aml.plantation_location_type_id,
                            sums_cost_aml.plantation_location_id,
                            sums_cost_aml.plantation_activity_id,
                            sums_cost_aml.plantation_src_journal_id,
                            p_to_be_deferred,
                            sums_cost_aml.cost,
                            p_user_id, p_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
                END LOOP;                            

                UPDATE closing_project SET 
                        total_cost = v_current_period_cost,
                        write_uid=p_user_id, 
                        write_date=(now() at time zone 'UTC')
                    WHERE id=p_closing_project_id;
            END;
            $BODY$
            LANGUAGE plpgsql VOLATILE
            COST 100;
            """)
    
        _logger.info("Create SUMMARY CLOSING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.procedure_summerize_project_deferred_cost(
                        p_closing_project_id integer, p_project_id integer, 
                        p_user_id integer, p_company_id integer) 
            RETURNS void AS
            $BODY$
            DECLARE
                v_closing_project_date_from date;
                v_location_type integer;
                v_location integer;
                v_deferred_account integer;
                v_existing_move_id integer;
                sums_deferred_aml record;
                v_accumulated_cost numeric := 0.0;
            BEGIN
                select date_from from closing_project where id=p_closing_project_id INTO v_closing_project_date_from;
                select location_type_id from lhm_project where id=p_project_id INTO v_location_type;
                select location_id from lhm_project where id=p_project_id INTO v_location;
                select lpt.account_id from lhm_project lp, lhm_project_type lpt where lp.id=p_project_id and lp.categ_id=lpt.id INTO v_deferred_account;
                
                FOR sums_deferred_aml IN SELECT plantation_location_type_id,
                                sub.plantation_location_id,
                                sub.plantation_activity_id,
                                sub.plantation_src_journal_id,
                                sum(sub.deferred_cost) as deferred_cost,
                                sum(sub.new_deferred_cost) as new_deferred_cost,
                                sum(sub.accumulated_cost) as accumulated_cost
                            FROM (
                                SELECT 
                                    aml1.plantation_location_type_id,
                                    aml1.plantation_location_id,
                                    aml1.plantation_activity_id,
                                    aml1.plantation_src_journal_id,
                                    SUM(CASE WHEN aml1.debit>0 THEN aml1.debit ELSE 0 END) as deferred_cost,
                                    SUM(CASE WHEN aml1.credit>0 THEN aml1.credit ELSE 0 END) as accumulated_cost,
                                    SUM(0) as new_deferred_cost
                                FROM account_move_line aml1
                                WHERE 
                                    aml1.date<v_closing_project_date_from 
                                    and aml1.parent_state='posted'
                                    and aml1.plantation_location_type_id=v_location_type
                                    and aml1.plantation_location_id=v_location 
                                    and aml1.account_id=v_deferred_account
                                GROUP BY aml1.plantation_location_type_id,
                                    aml1.plantation_location_id,
                                    aml1.plantation_activity_id,
                                    aml1.plantation_src_journal_id
                                UNION ALL
                                SELECT 
                                    cpl1.plantation_location_type_id,
                                    cpl1.plantation_location_id,
                                    cpl1.plantation_activity_id,
                                    cpl1.plantation_src_journal_id,
                                    SUM(0) as deferred_cost,
                                    SUM(0) as accumulated_cost,
                                    sum(cpl1.total_cost) as new_deferred_cost
                                FROM closing_project_plant_line cpl1, closing_project cp1
                                WHERE 
                                    cp1.id=p_closing_project_id 
                                    and cp1.id=cpl1.closing_id
                                    and cpl1.to_be_deferred=true 
                                GROUP BY cpl1.plantation_location_type_id,
                                    cpl1.plantation_location_id,
                                    cpl1.plantation_activity_id,
                                    cpl1.plantation_src_journal_id
                                ) sub
                            GROUP BY
                                sub.plantation_location_type_id,
                                sub.plantation_location_id,
                                sub.plantation_activity_id,
                                sub.plantation_src_journal_id
                LOOP
                    -- v_accumulated_cost := v_accumulated_cost + sums_cost_aml.accumulated_cost;

                    INSERT INTO closing_project_plant_deferred
                            (id, closing_id,  
                            plantation_location_type_id, plantation_location_id, 
                            plantation_activity_id, plantation_src_journal_id,
                            deferred_cost, new_deferred_cost, 
                            accumulated_cost, residual_deferred, 
                            create_uid, write_uid, create_date, write_date) 
                        VALUES (
                            nextval('closing_project_plant_line_id_seq'),
                            p_closing_project_id,
                            sums_deferred_aml.plantation_location_type_id,
                            sums_deferred_aml.plantation_location_id,
                            sums_deferred_aml.plantation_activity_id,
                            sums_deferred_aml.plantation_src_journal_id,
                            sums_deferred_aml.deferred_cost,
                            sums_deferred_aml.new_deferred_cost,
                            sums_deferred_aml.accumulated_cost,
                            (sums_deferred_aml.deferred_cost + sums_deferred_aml.new_deferred_cost - sums_deferred_aml.accumulated_cost),
                            p_user_id, p_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
                END LOOP;

                UPDATE closing_project SET 
                        -- accumulated_cost = v_accumulated_cost,
                        write_uid=p_user_id, 
                        write_date=(now() at time zone 'UTC')
                    WHERE id=p_closing_project_id;
            END;
            $BODY$
            LANGUAGE plpgsql VOLATILE
            COST 100;
            """)

    def _get_domain_source_move_lines(self):
        src_account_ids = self.project_id.location_id.type_id.activity_ids.account_id.ids
        if not src_account_ids:
            raise ValidationError(_(f"Could not find accounts for all related activity inside Location Type {self.project_id.location_id.type_id.code}"))
        domain = [('plantation_location_id','=',self.project_id.location_id.id),
                ('parent_state','=','posted'),('date','>=',self.date_from),('date','<=',self.date_to)]
        if len(src_account_ids)==1:
            domain.append(('account_id','=',src_account_ids[0]))
        else:
            domain.append(('account_id','in',src_account_ids))
        return domain

    def summarize_move_line(self):
        for closing in self:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Summerize Project Cost", closing.id)
            if closing.project_id.project_tanaman and closing.project_id.plant_block_id:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Project Tanaman")
                closing.cost_line_ids.unlink()
                closing.deferred_cost_line_ids.unlink()
                if closing.project_id.harvest_date_schedule <= closing.date_from:
                    # Only Cost to be distributed as Cost
                    date_from = closing.date_from.strftime('%Y-%m-%d')
                    date_to = closing.project_id.date_finished.strftime('%Y-%m-%d') if closing.project_id.date_finished<=closing.date_to else closing.date_to.strftime('%Y-%m-%d')
                    self.env.cr.execute(f"select procedure_summerize_project_plant_cost({closing.id}, {closing.project_id.id}, to_date('{date_from}','YYYY-MM-DD'), to_date('{date_to}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")
                elif closing.project_id.harvest_date_schedule > closing.date_to:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> lebih besar", closing.id)
                    # Only Cost to be Accrued
                    date_from = closing.date_from.strftime('%Y-%m-%d')
                    date_to = closing.date_to.strftime('%Y-%m-%d')
                    self.env.cr.execute(f"select procedure_summerize_project_plant_cost({closing.id}, {closing.project_id.id}, to_date('{date_from}','YYYY-MM-DD'), to_date('{date_to}','YYYY-MM-DD'), true, {self.env.user.id}, {self.env.company.id})")
                else:
                    # Possible Cost to be Accrued
                    date_from1 = closing.date_from.strftime('%Y-%m-%d') if closing.project_id.date_start<closing.date_from else closing.project_id.date_start.strftime('%Y-%m-%d')
                    date_to1 = (closing.project_id.harvest_date_schedule - relativedelta(days=1)).strftime('%Y-%m-%d')
                    self.env.cr.execute(f"select procedure_summerize_project_plant_cost({closing.id}, {closing.project_id.id}, to_date('{date_from1}','YYYY-MM-DD'), to_date('{date_to1}','YYYY-MM-DD'), true, {self.env.user.id}, {self.env.company.id})")
                    
                    date_from2 = closing.project_id.harvest_date_schedule.strftime('%Y-%m-%d')
                    date_to2 = closing.project_id.date_finished.strftime('%Y-%m-%d') if closing.project_id.date_finished<=closing.date_to else closing.date_to.strftime('%Y-%m-%d')
                    self.env.cr.execute(f"select procedure_summerize_project_plant_cost({closing.id}, {closing.project_id.id}, to_date('{date_from2}','YYYY-MM-DD'), to_date('{date_to2}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")

                self.env.cr.execute(f"select procedure_summerize_project_deferred_cost({closing.id}, {closing.project_id.id}, {self.env.user.id}, {self.env.company.id})")
                closing.total_cost = sum(closing.cost_line_ids.mapped('total_cost')) if closing.cost_line_ids else 0.0
            else:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Project Aja")
                source_moves = self.env['account.move.line'].search(self._get_domain_source_move_lines())
                closing.total_cost = sum(source_moves.mapped('balance')) if source_moves else 0.0

    def _prepare_move_lines_for_project_tanaman(self):
        self.ensure_one()
        move_lines = []
        for line1 in self.cost_line_ids:
            dest_vals1 = {
                'name': 'Move Cost Driver to Cost Account',
                'plantation_varieties_id': self.project_id.varieties_id.id,
                'plantation_location_type_id': line1.plantation_location_type_id.id,
                'plantation_location_id': line1.plantation_location_id.id,
                'plantation_activity_id': line1.plantation_activity_id.id,
                'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                # 'account_id': self.project_id.categ_id.account_id.id if line1.to_be_deferred else (line1.plantation_activity_id.cost_account_id.id if self.project_id.plant_block_id.owner_type=='inti' else self.project_id.plant_block_id.plasma_account_id.id),
                'account_id': self.project_id.categ_id.account_id.id if line1.to_be_deferred else line1.plantation_activity_id.cost_account_id.id,
                'debit': line1.total_cost if line1.total_cost > 0 else 0.0,
                'credit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
            }
            move_lines.append([0,0,dest_vals1])
            src_vals1 = {
                'name': 'Close the Cost Driver Account',
                'plantation_varieties_id': self.project_id.varieties_id.id,
                'plantation_location_type_id': line1.plantation_location_type_id.id,
                'plantation_location_id': line1.plantation_location_id.id,
                'plantation_activity_id': False,
                'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                'account_id': self.closing_account_id.id,
                'debit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
                'credit': line1.total_cost if line1.total_cost > 0 else 0.0,
            }
            move_lines.append([0,0,src_vals1])
        
        for line2 in self.deferred_cost_line_ids:
            if line2.cost_to_post:
                dest_vals2 = {
                    'name': 'Move Deferred Cost to Cost Account',
                    'plantation_varieties_id': self.project_id.varieties_id.id,
                    'plantation_location_type_id': line2.plantation_location_type_id.id,
                    'plantation_location_id': line2.plantation_location_id.id,
                    'plantation_activity_id': line2.plantation_activity_id.id,
                    'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                    # 'account_id': (line2.plantation_activity_id.cost_account_id.id if self.project_id.plant_block_id.owner_type=='inti' else self.project_id.plant_block_id.plasma_account_id.id),
                    'account_id': line2.plantation_activity_id.cost_account_id.id,
                    'debit': line2.cost_to_post if line2.cost_to_post > 0 else 0.0,
                    'credit': abs(line2.cost_to_post) if line2.cost_to_post < 0 else 0.0,
                }
                move_lines.append([0,0,dest_vals2])
                src_vals2 = {
                    'name': 'Consumed the Deferred Cost',
                    'plantation_varieties_id': self.project_id.varieties_id.id,
                    'plantation_location_type_id': line2.plantation_location_type_id.id,
                    'plantation_location_id': line2.plantation_location_id.id,
                    'plantation_activity_id': line2.plantation_activity_id.id,
                    'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                    'account_id': self.project_id.categ_id.account_id.id,
                    'debit': abs(line2.cost_to_post) if line2.cost_to_post < 0 else 0.0,
                    'credit': line2.cost_to_post if line2.cost_to_post > 0 else 0.0,
                }
                move_lines.append([0,0,src_vals2])
        return move_lines
    
    def create_account_move(self):
        for closing in self:
            if closing.closing_move_id:
                if closing.closing_move_id.state=='posted':
                    closing.closing_move_id.button_draft()
            if closing.project_tanaman:
                move_lines = closing._prepare_move_lines_for_project_tanaman()
            else:
                move_lines = []
                vals = {
                    'name': 'Distribute Cost from Project Closing',
                    'plantation_location_type_id': closing.project_id.location_type_id.id,
                    'plantation_location_id': closing.project_id.location_id.id,
                    # 'plantation_activity_id': False,
                    'account_id': closing.dest_account_id.id,
                    'debit': closing.total_cost if closing.total_cost > 0 else 0.0,
                    'credit': abs(closing.total_cost) if closing.total_cost < 0 else 0.0,
                }
                move_lines.append((0,0,vals))
                vals = {
                    'name': 'Distribute Cost from Running Machine',
                    'plantation_location_type_id': closing.project_id.location_type_id.id,
                    'plantation_location_id': closing.project_id.location_id.id,
                    # 'plantation_activity_id': False,
                    'account_id': closing.closing_account_id.id,
                    'debit': abs(closing.total_cost) if closing.total_cost < 0 else 0.0,
                    'credit': closing.total_cost if closing.total_cost > 0 else 0.0,
                }
                move_lines.append((0,0,vals))
            
            values = {
                'date': closing.date_to,
                'journal_id': self.env['account.journal'].search([('type','=','general')], limit=1).id,
                'move_type': 'entry',
                'line_ids': move_lines,
            }
            if closing.closing_move_id:
                closing.closing_move_id.write(values)
            else:
                new_move = self.env['account.move'].create(values)
                closing.closing_move_id = new_move.id
        
        return True

    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_source_move_lines()
        return action
