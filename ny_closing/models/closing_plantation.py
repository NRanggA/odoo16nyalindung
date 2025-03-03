from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class ClosingPlantationDeferred(models.Model):
    _name = 'closing.plantation.deferred' 
    _description = 'Closing Plantation - Deffered Cost'

    closing_id = fields.Many2one('closing.plantation', string='Closing Plantation')
    plantation_location_type_id = fields.Many2one('lhm.location.type', string='Tipe Lokasi', ondelete='restrict')
    plantation_location_id = fields.Many2one('lhm.location', string='Lokasi', ondelete='restrict')
    plantation_activity_id = fields.Many2one('lhm.activity', string='Aktivitas', ondelete='restrict')
    plantation_src_journal_id = fields.Many2one('account.journal', string='Asal Jurnal', ondelete='restrict')
    # plantation_season_id = fields.Many2one('plantation.season', string='Season', ondelete='restrict')
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
        src_account_id = self.plant_block_id.deferred_account_id
        if not src_account_id:
            raise ValidationError(_(f"Could not find defered account inside Blok Tanam {self.plant_block_id.code}"))
        domain = [('plantation_location_type_id','=',self.plant_block_id.location_type_id.id),
                ('plantation_location_id','=',self.plant_block_id.location_id.id),
                ('parent_state','=','posted'),('date','<',self.date_from),
                ('account_id','=',src_account_id)]
        return domain

    def action_view_deferred_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_deferred_move_lines()
        return action

class ClosingPlantationLine(models.Model):
    _name = 'closing.plantation.line' 
    _description = 'Closing Plantation - Current Cost'

    closing_id = fields.Many2one('closing.plantation', string='Closing Plantation')
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
        src_account_ids = self.plant_block_id.location_id.type_id.activity_ids.account_id.ids
        if not src_account_ids:
            raise ValidationError(_(f"Could not find accounts for all related activity inside Location Type {self.plant_block_id.location_id.type_id.code}"))
        domain = [('plantation_location_id','=',self.plant_block_id.location_id.id),
                ('parent_state','=','posted'),('date','>=',self.date_from),('date','<=',self.date_to)]
        if len(src_account_ids)==1:
            domain.append(('account_id','=',src_account_ids[0]))
        else:
            domain.append(('account_id','in',src_account_ids))
        return domain
    
    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_source_move_lines()
        return action

class ClosingPlantation(models.Model):
    _name = 'closing.plantation' 
    _description = 'Closing Plantation'
    _rec_name = 'plant_block_id'

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')
    
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    plant_block_id = fields.Many2one('lhm.plant.block', string='Blok Tanam', ondelete='restrict', required=True)
    type_of_plant = fields.Selection(related='plant_block_id.type_of_plant', store=True)
    status = fields.Selection(related='plant_block_id.status', store=True)
    plant_season_ids = fields.Many2many('plantation.season', 'closing_plantation_season_rel', string='Season', ondelete='restrict')
    mark_plant_block_period = fields.Selection([('none','None'),('tm','TM'),('tbm','TBM'),('preharvest','Pre-Harvesting'),('harvesting','Harvesting')], compute='_compute_mark', string='Block Mark')

    tbm_account_id = fields.Many2one(related="plant_block_id.tbm_account_id", string='Immature Plant Cost Account', help="Usually used for Immature Plant to accumulate Cost to Asset")
    deferred_account_id = fields.Many2one(related="plant_block_id.deferred_account_id", string='Deferred Account', help="Usually used for Pra Harvesting Period")
    
    closing_account_id = fields.Many2one('account.account', string='Closing Account')

    accumulated_tbm_cost = fields.Float('Accumulated TBM Cost')
    accumulated_deferred_cost = fields.Float('Accumulated Deferred Cost')
    current_period_cost = fields.Float('Cost on Current Period')
    
    cost_line_ids = fields.One2many('closing.plantation.line', 'closing_id')
    cost_line_to_be_deferred_ids = fields.One2many('closing.plantation.line', 'closing_id', domain=[('to_be_deferred','=',True)], string="Cost to be Deferred")
    cost_line_as_cost_ids = fields.One2many('closing.plantation.line', 'closing_id', domain=[('to_be_deferred','=',False)], string="Cost to be Consumed")
    deferred_cost_line_ids = fields.One2many('closing.plantation.deferred', 'closing_id')
    pct_deferred_to_cost = fields.Float()

    closing_move_id = fields.Many2one('account.move', string='Journal Entry')

    @api.depends('plant_block_id','type_of_plant','status','plant_season_ids','plant_season_ids.harvest_date_schedule')
    def _compute_mark(self):
        for closing in self:
            new_mark_plant_block_period = 'none'
            if closing.type_of_plant=='shorterm' and closing.plant_season_ids:
                if any([closing.date_to>=s.harvest_date_schedule for s in closing.plant_season_ids]):
                    new_mark_plant_block_period = 'harvesting'
                else:
                    new_mark_plant_block_period = 'preharvest'
            elif closing.type_of_plant=='longterm_seasonal':
                if closing.status=='tbm':
                    new_mark_plant_block_period = 'tbm'
                else:
                    if closing.plant_season_ids:
                        if any([closing.date_to>=s.harvest_date_schedule for s in closing.plant_season_ids]):
                            new_mark_plant_block_period = 'harvesting'
                        else:
                            new_mark_plant_block_period = 'preharvest'
                    else:
                        new_mark_plant_block_period = 'tm'
            else:
                if closing.status=='tbm':
                    new_mark_plant_block_period = 'tbm'
                else:
                    new_mark_plant_block_period = 'tm'

            closing.mark_plant_block_period = new_mark_plant_block_period

    def init(self):
        _logger.info("Create SUMMARY CLOSING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.procedure_summerize_cost(
                        p_closing_plantation_id integer, p_planted_block_id integer, 
                        p_date_from date, p_date_to date, p_to_be_deferred boolean,
                        p_user_id integer, p_company_id integer) 
            RETURNS void AS
            $BODY$
            DECLARE
                v_closing_plantation_date_from date;
                v_closing_plantation_date_to date;
                v_location_type integer;
                v_location integer;
                sums_cost_aml record;
                v_current_period_cost numeric := 0.0;
            BEGIN
                v_closing_plantation_date_from := p_date_from;
                v_closing_plantation_date_to := p_date_to;
                           
                select location_type_id from lhm_plant_block where id=p_planted_block_id INTO v_location_type;
                select location_id from lhm_plant_block where id=p_planted_block_id INTO v_location;
            
                FOR sums_cost_aml IN SELECT 
                                aml1.plantation_location_type_id,
                                aml1.plantation_location_id,
                                aml1.plantation_activity_id,
                                coalesce(aml1.plantation_src_journal_id, aml1.journal_id) as plantation_src_journal_id,
                                SUM(aml1.debit - aml1.credit) as cost 
                            FROM account_move_line aml1
                            WHERE 
                                aml1.date>=v_closing_plantation_date_from 
                                and aml1.date<=v_closing_plantation_date_to 
                                and aml1.parent_state='posted'
                                and aml1.plantation_location_type_id=v_location_type
                                and aml1.plantation_location_id=v_location
                                and aml1.account_id in (select account_id from lhm_activity where type_id=v_location_type)
                            GROUP BY aml1.plantation_location_type_id,
                                aml1.plantation_location_id,
                                aml1.plantation_activity_id,
                                aml1.plantation_src_journal_id,
                                aml1.journal_id
                LOOP
                    -- v_current_period_cost := v_current_period_cost + sums_cost_aml.cost;
                    INSERT INTO closing_plantation_line
                            (id, closing_id,  
                            date_from, date_to, 
                            plantation_location_type_id, plantation_location_id, 
                            plantation_activity_id, plantation_src_journal_id, 
                            to_be_deferred, total_cost,
                            create_uid, write_uid, create_date, write_date) 
                        VALUES (
                            nextval('closing_plantation_line_id_seq'),
                            p_closing_plantation_id,
                            v_closing_plantation_date_from, 
                            v_closing_plantation_date_to,
                            sums_cost_aml.plantation_location_type_id,
                            sums_cost_aml.plantation_location_id,
                            sums_cost_aml.plantation_activity_id,
                            sums_cost_aml.plantation_src_journal_id,
                            p_to_be_deferred,
                            sums_cost_aml.cost,
                            p_user_id, p_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
                END LOOP;                            

                UPDATE closing_plantation SET 
                        current_period_cost = v_current_period_cost,
                        write_uid=p_user_id, 
                        write_date=(now() at time zone 'UTC')
                    WHERE id=p_closing_plantation_id;
            END;
            $BODY$
            LANGUAGE plpgsql VOLATILE
            COST 100;
            """)

        _logger.info("Create SUMMARY CLOSING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.procedure_summerize_deferred_cost(
                        p_closing_plantation_id integer, p_planted_block_id integer, 
                        p_user_id integer, p_company_id integer) 
            RETURNS void AS
            $BODY$
            DECLARE
                v_closing_plantation_date_from date;
                v_location_type integer;
                v_location integer;
                v_deferred_account integer;
                v_existing_move_id integer;
                sums_deferred_aml record;
                v_accumulated_cost numeric := 0.0;
            BEGIN
                select date_from from closing_plantation where id=p_closing_plantation_id INTO v_closing_plantation_date_from;
                select location_type_id from lhm_plant_block where id=p_planted_block_id INTO v_location_type;
                select location_id from lhm_plant_block where id=p_planted_block_id INTO v_location;
                select deferred_account_id from lhm_plant_block where id=p_planted_block_id INTO v_deferred_account;
                
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
                                    coalesce(aml1.plantation_src_journal_id, aml1.journal_id) as plantation_src_journal_id,
                                    SUM(CASE WHEN aml1.debit>0 THEN aml1.debit ELSE 0 END) as deferred_cost,
                                    SUM(CASE WHEN aml1.credit>0 THEN aml1.credit ELSE 0 END) as accumulated_cost,
                                    SUM(0) as new_deferred_cost
                                FROM account_move_line aml1
                                WHERE 
                                    aml1.date<v_closing_plantation_date_from 
                                    and aml1.parent_state='posted'
                                    and aml1.plantation_location_type_id=v_location_type
                                    and aml1.plantation_location_id=v_location 
                                    and aml1.account_id=v_deferred_account
                                GROUP BY aml1.plantation_location_type_id,
                                    aml1.plantation_location_id,
                                    aml1.plantation_activity_id,
                                    aml1.plantation_src_journal_id,
                                    aml1.journal_id
                                UNION ALL
                                SELECT 
                                    cpl1.plantation_location_type_id,
                                    cpl1.plantation_location_id,
                                    cpl1.plantation_activity_id,
                                    cpl1.plantation_src_journal_id,
                                    SUM(0) as deferred_cost,
                                    SUM(0) as accumulated_cost,
                                    sum(cpl1.total_cost) as new_deferred_cost
                                FROM closing_plantation_line cpl1, closing_plantation cp1
                                WHERE 
                                    cp1.id=p_closing_plantation_id 
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

                    INSERT INTO closing_plantation_deferred
                            (id, closing_id,  
                            plantation_location_type_id, plantation_location_id, 
                            plantation_activity_id, plantation_src_journal_id,
                            deferred_cost, new_deferred_cost, 
                            accumulated_cost, residual_deferred, 
                            create_uid, write_uid, create_date, write_date) 
                        VALUES (
                            nextval('closing_plantation_line_id_seq'),
                            p_closing_plantation_id,
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

                UPDATE closing_plantation SET 
                        -- accumulated_cost = v_accumulated_cost,
                        write_uid=p_user_id, 
                        write_date=(now() at time zone 'UTC')
                    WHERE id=p_closing_plantation_id;
            END;
            $BODY$
            LANGUAGE plpgsql VOLATILE
            COST 100;
            """)

    @api.onchange('pct_deferred_to_cost')
    def onchange_pct_deferred_to_cost(self):
        self.deferred_cost_line_ids.write({'pct_cost_to_post': self.pct_deferred_to_cost})

    def _get_domain_deferred_move_lines(self):
        src_account_id = self.plant_block_id.deferred_account_id.id
        if not src_account_id:
            raise ValidationError(_(f"Could not find defered account inside Blok Tanam {self.plant_block_id.code}"))
        domain = [('plantation_location_type_id','=',self.plant_block_id.location_type_id.id),
                ('plantation_location_id','=',self.plant_block_id.location_id.id),
                ('parent_state','=','posted'),('date','<',self.date_from),
                ('account_id','=',src_account_id)]
        return domain

    def _get_domain_source_move_lines(self):
        src_account_ids = self.plant_block_id.location_id.type_id.activity_ids.account_id.ids
        if not src_account_ids:
            raise ValidationError(_(f"Could not find accounts for all related activity inside Location Type {self.plant_block_id.location_id.type_id.code}"))
        domain = [('plantation_location_id','=',self.plant_block_id.location_id.id),
                ('parent_state','=','posted'),('date','>=',self.date_from),('date','<=',self.date_to)]
        if len(src_account_ids)==1:
            domain.append(('account_id','=',src_account_ids[0]))
        else:
            domain.append(('account_id','in',src_account_ids))
        return domain

    def summarize_move_line(self):
        for closing in self:
            closing.cost_line_ids.unlink()
            closing.deferred_cost_line_ids.unlink()
            # source_moves_cost = self.env['account.move.line'].search(self._get_domain_source_move_lines())
            # closing.current_period_cost = sum(source_moves_cost.mapped('balance')) if source_moves_cost else 0.0
            # deferred_moves_cost = self.env['account.move.line'].search(self._get_domain_deferred_move_lines())
            # closing.accumulated_cost = sum(deferred_moves_cost.mapped('balance')) if deferred_moves_cost else 0.0
            if closing.type_of_plant in ['shorterm','longterm_seasonal']:
                if not closing.deferred_account_id:
                    raise ValidationError(_(f"Account Deferred Cost is not yet defined on Master Blok Tanam for Blok with No. {closing.plant_block_id.code}"))

                if closing.type_of_plant=='shorterm':
                    query_season = f"""Select seas.id from season_plant_block_rel rel 
                        inner join plantation_season seas on seas.id=rel.season_id 
                        where rel.plant_block_id={closing.plant_block_id.id} 
                            and seas.date_start<='{closing.date_to.strftime('%Y-%m-%d')}' 
                            and seas.date_end>='{closing.date_from.strftime('%Y-%m-%d')}' 
                        """
                    self.env.cr.execute(query_season)
                    season_ids = []
                    for lres in self.env.cr.fetchall():
                        season_ids.append(lres[0])
                    if not season_ids:
                        raise ValidationError(_(f"Could not find a Plantation Season for Block No. {closing.plant_block_id.code}"))
                    closing.plant_season_ids = [(6,0,season_ids)]
                    # Menghitung Summery Deferred Cost sampai dengan saat itu dan Summery Cost diperiode itu
                    # Jika Opsi Deferred di Centang, maka Cost akan diakumulasikan ke Akun Deferred(Aset)
                    # Jika Tidak, maka Cost akan didistribusikan ke Akun Masing2 ditambah Deferred Cost yang ingin didistribusikan dibulan itu
                    for season in closing.plant_season_ids.sorted(lambda s: s.date_start):
                        if season.harvest_date_schedule <= closing.date_from:
                            # Only Cost to be distributed as Cost
                            date_from = closing.date_from.strftime('%Y-%m-%d')
                            date_to = season.date_stop.strftime('%Y-%m-%d') if season.date_stop<=closing.date_to else closing.date_to.strftime('%Y-%m-%d')
                            self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from}','YYYY-MM-DD'), to_date('{date_to}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")
                        elif season.harvest_date_schedule > closing.date_to:
                            # Only Cost to be Accrued
                            date_from = closing.date_from.strftime('%Y-%m-%d')
                            date_to = closing.date_to.strftime('%Y-%m-%d')
                            self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from}','YYYY-MM-DD'), to_date('{date_to}','YYYY-MM-DD'), true, {self.env.user.id}, {self.env.company.id})")
                        else:
                            # Possible Cost to be Accrued
                            date_from1 = closing.date_from.strftime('%Y-%m-%d') if season.date_start<closing.date_from else season.date_start.strftime('%Y-%m-%d')
                            date_to1 = (season.harvest_date_schedule - relativedelta(days=1)).strftime('%Y-%m-%d')
                            self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from1}','YYYY-MM-DD'), to_date('{date_to1}','YYYY-MM-DD'), true, {self.env.user.id}, {self.env.company.id})")
                            
                            date_from2 = season.harvest_date_schedule.strftime('%Y-%m-%d')
                            date_to2 = season.date_end.strftime('%Y-%m-%d') if season.date_end<=closing.date_to else closing.date_to.strftime('%Y-%m-%d')
                            self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from2}','YYYY-MM-DD'), to_date('{date_to2}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")

                        self.env.cr.execute(f"select procedure_summerize_deferred_cost({closing.id}, {closing.plant_block_id.id}, {self.env.user.id}, {self.env.company.id})")
                elif closing.type_of_plant=='longterm_seasonal':
                    # Menghitung Summery Cost diperiode itu
                    # Jika masih fase TBM, maka Cost akan diakumulasikan ke Aset
                    # Jika sudah TM, maka
                    #   Hitung Deferred Cost sampai dengan saat itu dan Summery Cost diperiode itu
                    #   Jika Opsi Deferred (transfer_cost_to_deferred=True) di Centang, maka Cost akan diakumulasikan ke Akun Deferred(Aset)
                    #   Jika Tidak (transfer_cost_to_deferred=False), maka Cost akan didistribusikan ke Akun Masing2 ditambah Deferred Cost yang ingin didistribusikan dibulan itu
                    if closing.status=='tm':
                        query_season = f"""Select seas.id from season_plant_block_rel rel 
                            inner join plantation_season seas on seas.id=rel.season_id 
                            where rel.plant_block_id={closing.plant_block_id.id} 
                                and seas.date_start<='{closing.date_to.strftime('%Y-%m-%d')}' 
                                and seas.date_end>='{closing.date_from.strftime('%Y-%m-%d')}' 
                            """
                        self.env.cr.execute(query_season)
                        season_ids = []
                        for lres in self.env.cr.fetchall():
                            season_ids.append(lres[0])
                        if not season_ids:
                            raise ValidationError(_(f"Could not find a Plantation Season for Block No. {closing.plant_block_id.code}"))
                        closing.plant_season_ids = [(6,0,season_ids)]
                        for season in closing.plant_season_ids.sorted(lambda s: s.date_start):
                            if season.harvest_date_schedule <= closing.date_from:
                                # Only Cost to be distributed as Cost
                                date_from = closing.date_from.strftime('%Y-%m-%d')
                                date_to = season.date_end.strftime('%Y-%m-%d') if season.date_end<=closing.date_to else closing.date_to.strftime('%Y-%m-%d')
                                self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from}','YYYY-MM-DD'), to_date('{date_to}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")
                            elif season.harvest_date_schedule > closing.date_to:
                                # Only Cost to be Accrued
                                date_from = closing.date_from.strftime('%Y-%m-%d')
                                date_to = closing.date_to.strftime('%Y-%m-%d')
                                self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from}','YYYY-MM-DD'), to_date('{date_to}','YYYY-MM-DD'), true, {self.env.user.id}, {self.env.company.id})")
                            else:
                                # Possible Cost to be Accrued
                                date_from1 = closing.date_from.strftime('%Y-%m-%d') if season.date_start<closing.date_from else season.date_start.strftime('%Y-%m-%d')
                                date_to1 = (season.harvest_date_schedule - relativedelta(days=1)).strftime('%Y-%m-%d')
                                self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from1}','YYYY-MM-DD'), to_date('{date_to1}','YYYY-MM-DD'), true, {self.env.user.id}, {self.env.company.id})")
                                
                                date_from2 = season.harvest_date_schedule.strftime('%Y-%m-%d')
                                date_to2 = season.date_end.strftime('%Y-%m-%d') if season.date_end<=closing.date_to else closing.date_to.strftime('%Y-%m-%d')
                                self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{date_from2}','YYYY-MM-DD'), to_date('{date_to2}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")

                            self.env.cr.execute(f"select procedure_summerize_deferred_cost({closing.id}, {closing.plant_block_id.id}, {self.env.user.id}, {self.env.company.id})")
                    else:
                        self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{closing.date_from.strftime('%Y-%m-%d')}','YYYY-MM-DD'), to_date('{closing.date_to.strftime('%Y-%m-%d')}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")
            else: # closing.type_of_plant=='longterm_tbm_tm':
                # Hanya menghitung Summery Cost diperiode itu
                # Jika masih fase TBM, maka Cost akan diakumulasikan ke Aset
                # Jika sudah TM, maka Cost akan didistribusikan ke Akun Masing2
                self.env.cr.execute(f"select procedure_summerize_cost({closing.id}, {closing.plant_block_id.id}, to_date('{closing.date_from.strftime('%Y-%m-%d')}','YYYY-MM-DD'), to_date('{closing.date_to.strftime('%Y-%m-%d')}','YYYY-MM-DD'), false, {self.env.user.id}, {self.env.company.id})")
            closing.current_period_cost = sum(closing.cost_line_ids.mapped('total_cost')) if closing.cost_line_ids else 0.0

    def _prepare_move_lines_for_shorterm_block(self):
        self.ensure_one()
        move_lines = []
        for line1 in self.cost_line_ids:
            if line1.to_be_deferred and not self.deferred_account_id:
                raise ValidationError(f"Akun Deferred pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
            else:
                if self.plant_block_id.owner_type!='inti' and not self.plant_block_id.plasma_account_id:
                    raise ValidationError(f"Akun Plasma pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                elif not line1.plantation_activity_id:
                    raise ValidationError(f"Ditemukan transaksi dengan Aktifitas kosong") 
                # if not line1.plantation_activity_id.cost_account_id:
                elif not line1.plantation_activity_id.get_plantation_cost_account(line1.plantation_src_journal_id):
                    raise ValidationError(f"Plantation Cost pada Aktifitas {line1.plantation_activity_id.code} {line1.plantation_activity_id.name} kosong. Silahkan diisi terlebih dahulu") 
            
            cost_account_id = False
            if line1.to_be_deferred:
                cost_account_id = self.deferred_account_id.id 
            else:
                if self.plant_block_id.owner_type=='inti':
                    cost_account_id = line1.plantation_activity_id.get_plantation_cost_account(line1.plantation_src_journal_id)
                else:
                    cost_account_id = self.plant_block_id.plasma_account_id.id
            
            dest_vals1 = {
                'name': 'Move Cost Driver to Cost Account',
                'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                'plantation_location_type_id': line1.plantation_location_type_id.id,
                'plantation_location_id': line1.plantation_location_id.id,
                'plantation_activity_id': line1.plantation_activity_id.id,
                'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                # 'account_id': self.deferred_account_id.id if line1.to_be_deferred else (line1.plantation_activity_id.cost_account_id.id if self.plant_block_id.owner_type=='inti' else self.plant_block_id.plasma_account_id.id),
                'account_id': cost_account_id,
                'debit': line1.total_cost if line1.total_cost > 0 else 0.0,
                'credit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
            }
            
            move_lines.append([0,0,dest_vals1])
            src_vals1 = {
                'name': 'Close the Cost Driver Account',
                'plantation_varieties_id': self.plant_block_id.varieties_id.id,
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
            if not self.deferred_account_id:
                raise ValidationError(f"Akun Deferred pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
            
            if self.plant_block_id.owner_type!='inti' and not self.plant_block_id.plasma_account_id:
                raise ValidationError(f"Akun Plasma pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
            elif not line2.plantation_activity_id:
                raise ValidationError(f"Ditemukan transaksi dengan Aktifitas kosong") 
            elif not line2.plantation_activity_id.cost_account_id:
                raise ValidationError(f"Plantation Cost pada Aktifitas {line2.plantation_activity_id.code} {line2.plantation_activity_id.name} kosong. Silahkan diisi terlebih dahulu") 
            
            cost_account_id = False
            if self.plant_block_id.owner_type=='inti':
                cost_account_id = line2.plantation_activity_id.get_plantation_cost_account(line2.plantation_src_journal_id)
            else:
                cost_account_id = self.plant_block_id.plasma_account_id.id
            
            if line2.cost_to_post:
                dest_vals2 = {
                    'name': 'Move Deferred Cost to Cost Account',
                    'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                    'plantation_location_type_id': line2.plantation_location_type_id.id,
                    'plantation_location_id': line2.plantation_location_id.id,
                    'plantation_activity_id': line2.plantation_activity_id.id,
                    'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                    # 'account_id': (line2.plantation_activity_id.cost_account_id.id if self.plant_block_id.owner_type=='inti' else self.plant_block_id.plasma_account_id.id),
                    'account_id': cost_account_id,
                    'debit': line2.cost_to_post if line2.cost_to_post > 0 else 0.0,
                    'credit': abs(line2.cost_to_post) if line2.cost_to_post < 0 else 0.0,
                }
                move_lines.append([0,0,dest_vals2])
                src_vals2 = {
                    'name': 'Consumed the Deferred Cost',
                    'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                    'plantation_location_type_id': line2.plantation_location_type_id.id,
                    'plantation_location_id': line2.plantation_location_id.id,
                    'plantation_activity_id': line2.plantation_activity_id.id,
                    'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                    'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                    'account_id': self.deferred_account_id.id,
                    'debit': abs(line2.cost_to_post) if line2.cost_to_post < 0 else 0.0,
                    'credit': line2.cost_to_post if line2.cost_to_post > 0 else 0.0,
                }
                move_lines.append([0,0,src_vals2])
        return move_lines
    
    def _prepare_move_lines_for_longterm_seasonal_block(self):
        self.ensure_one()
        move_lines = []
        for line1 in self.cost_line_ids:
            if self.status=='tbm':
                if not self.tbm_account_id:
                    raise ValidationError(f"Akun TBM pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                dest_vals1 = {
                    'name': 'Move Cost Driver to Asset',
                    'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                    'plantation_location_type_id': line1.plantation_location_type_id.id,
                    'plantation_location_id': line1.plantation_location_id.id,
                    'plantation_activity_id': line1.plantation_activity_id.id,
                    'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                    'account_id': self.tbm_account_id.id,
                    'debit': line1.total_cost if line1.total_cost > 0 else 0.0,
                    'credit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
                }
                move_lines.append([0,0,dest_vals1])
            else:
                if line1.to_be_deferred and not self.deferred_account_id:
                    raise ValidationError(f"Akun Deferred pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                else:
                    if self.plant_block_id.owner_type!='inti' and not self.plant_block_id.plasma_account_id:
                        raise ValidationError(f"Akun Plasma pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                    elif not line1.plantation_activity_id:
                        raise ValidationError(f"Ditemukan transaksi dengan Aktifitas kosong") 
                    elif not line1.plantation_activity_id.cost_account_id:
                        raise ValidationError(f"Plantation Cost pada Aktifitas {line1.plantation_activity_id.code} {line1.plantation_activity_id.name} kosong. Silahkan diisi terlebih dahulu") 
                dest_vals1 = {
                    'name': 'Move Cost Driver to Cost Account',
                    'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                    'plantation_location_type_id': line1.plantation_location_type_id.id,
                    'plantation_location_id': line1.plantation_location_id.id,
                    'plantation_activity_id': line1.plantation_activity_id.id,
                    'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                    'account_id': self.deferred_account_id.id if line1.to_be_deferred else (line1.plantation_activity_id.cost_account_id.id if self.plant_block_id.owner_type=='inti' else self.plant_block_id.plasma_account_id.id),
                    'debit': line1.total_cost if line1.total_cost > 0 else 0.0,
                    'credit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
                }
                move_lines.append([0,0,dest_vals1])
            src_vals1 = {
                'name': 'Move Cost Driver to Account Nursery',
                'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                'plantation_location_type_id': line1.plantation_location_type_id.id,
                'plantation_location_id': line1.plantation_location_id.id,
                'plantation_activity_id': False,
                'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                'account_id': self.closing_account_id.id,
                'debit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
                'credit': line1.total_cost if line1.total_cost > 0 else 0.0,
            }
            move_lines.append([0,0,src_vals1])
        
        if self.status=='tm' and self.deferred_cost_line_ids:
            for line2 in self.deferred_cost_line_ids:
                if not self.deferred_account_id:
                    raise ValidationError(f"Akun Deferred pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                else:
                    if self.plant_block_id.owner_type!='inti' and not self.plant_block_id.plasma_account_id:
                        raise ValidationError(f"Akun Plasma pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                    elif not line2.plantation_activity_id:
                        raise ValidationError(f"Ditemukan transaksi dengan Aktifitas kosong") 
                    elif not line2.plantation_activity_id.cost_account_id:
                        raise ValidationError(f"Plantation Cost pada Aktifitas {line2.plantation_activity_id.code} {line2.plantation_activity_id.name} kosong. Silahkan diisi terlebih dahulu") 
                if line2.cost_to_post:
                    dest_vals2 = {
                        'name': 'Move Deferred Cost to Cost Account',
                        'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                        'plantation_location_type_id': line2.plantation_location_type_id.id,
                        'plantation_location_id': line2.plantation_location_id.id,
                        'plantation_activity_id': line2.plantation_activity_id.id,
                        'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                        'account_id': (line2.plantation_activity_id.cost_account_id.id if self.plant_block_id.owner_type=='inti' else self.plant_block_id.plasma_account_id.id),
                        'debit': line2.cost_to_post if line2.cost_to_post > 0 else 0.0,
                        'credit': abs(line2.cost_to_post) if line2.cost_to_post < 0 else 0.0,
                    }
                    move_lines.append([0,0,dest_vals2])
                    src_vals2 = {
                        'name': 'Consumed the Deferred Cost',
                        'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                        'plantation_location_type_id': line2.plantation_location_type_id.id,
                        'plantation_location_id': line2.plantation_location_id.id,
                        'plantation_activity_id': line2.plantation_activity_id.id,
                        'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                        'plantation_src_journal_id': line2.plantation_src_journal_id.id,
                        'account_id': self.deferred_account_id.id,
                        'debit': abs(line2.cost_to_post) if line2.cost_to_post < 0 else 0.0,
                        'credit': line2.cost_to_post if line2.cost_to_post > 0 else 0.0,
                    }
                    move_lines.append([0,0,src_vals2])
        return move_lines
        
    def _prepare_move_lines_for_longterm_tbm_tm_block(self):
        self.ensure_one()
        move_lines = []
        for line1 in self.cost_line_ids:
            if self.status=='tbm':
                if not self.tbm_account_id:
                    raise ValidationError(f"Akun TBM pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                dest_vals1 = {
                    'name': 'Move Cost Driver to Asset',
                    'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                    'plantation_location_type_id': line1.plantation_location_type_id.id,
                    'plantation_location_id': line1.plantation_location_id.id,
                    'plantation_activity_id': line1.plantation_activity_id.id,
                    'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                    'account_id': self.tbm_account_id.id,
                    'debit': line1.total_cost if line1.total_cost > 0 else 0.0,
                    'credit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
                }
                move_lines.append([0,0,dest_vals1])
            else:
                if self.plant_block_id.owner_type!='inti' and not self.plant_block_id.plasma_account_id:
                    raise ValidationError(f"Akun Plasma pada Blok Tanam {self.plant_block_id.code} {self.plant_block_id.name} kosong. Silahkan diisi terlebih dahulu") 
                elif not line1.plantation_activity_id:
                    raise ValidationError(f"Ditemukan transaksi dengan Aktifitas kosong") 
                # elif not line1.plantation_activity_id.cost_account_id:
                elif not line1.plantation_activity_id.get_plantation_cost_account(line1.plantation_src_journal_id):
                    raise ValidationError(f"Plantation Cost pada Aktifitas {line1.plantation_activity_id.code} {line1.plantation_activity_id.name} kosong. Silahkan diisi terlebih dahulu") 
                cost_account_id = False
                if self.plant_block_id.owner_type=='inti':
                    cost_account_id = line1.plantation_activity_id.get_plantation_cost_account(line1.plantation_src_journal_id) 
                else:
                    cost_account_id = self.plant_block_id.plasma_account_id.id

                dest_vals1 = {
                    'name': 'Move Cost Driver to Account Cost / Plasma',
                    'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                    'plantation_location_type_id': line1.plantation_location_type_id.id,
                    'plantation_location_id': line1.plantation_location_id.id,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                    # 'account_id': line1.plantation_activity_id.cost_account_id.id if self.plant_block_id.owner_type=='inti' else self.plant_block_id.plasma_account_id.id,
                    'account_id': cost_account_id,
                    'debit': line1.total_cost if line1.total_cost > 0 else 0.0,
                    'credit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
                }
                move_lines.append([0,0,dest_vals1])
            src_vals1 = {
                'name': 'Closing Cost Driver Plantation',
                'plantation_varieties_id': self.plant_block_id.varieties_id.id,
                'plantation_location_type_id': line1.plantation_location_type_id.id,
                'plantation_location_id': line1.plantation_location_id.id,
                'plantation_activity_id': False,
                'plantation_src_journal_id': line1.plantation_src_journal_id.id,
                'account_id': self.closing_account_id.id,
                'debit': abs(line1.total_cost) if line1.total_cost < 0 else 0.0,
                'credit': line1.total_cost if line1.total_cost > 0 else 0.0,
            }
            move_lines.append([0,0,src_vals1])
        return move_lines

    def create_account_move(self):
        closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
        for closing in self:
            if closing.closing_move_id:
                if closing.closing_move_id.state!='posted':
                    closing.closing_move_id.write({'name': ''})
                    closing.closing_move_id.unlink()
                else:
                    closing.closing_move_id.button_draft()
                    closing.closing_move_id.write({'name': ''})
                    closing.closing_move_id.unlink()
            if closing.type_of_plant=='shorterm':
                move_lines = closing._prepare_move_lines_for_shorterm_block()
            elif closing.type_of_plant=='longterm_seasonal':
                move_lines = closing._prepare_move_lines_for_longterm_seasonal_block()
            else: # closing.type_of_plant=='shorterm':
                move_lines = closing._prepare_move_lines_for_longterm_tbm_tm_block()
            if move_lines:
                move_values = {
                    'date': closing.date_to,
                    'journal_id': closing_journal.id,
                    'move_type': 'entry',
                    'line_ids': move_lines,
                }
                new_move = self.env['account.move'].create(move_values)
                
                closing.closing_move_id = new_move.id
        return True

    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_source_move_lines()
        return action

    def action_view_deferred_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = self._get_domain_deferred_move_lines()
        return action