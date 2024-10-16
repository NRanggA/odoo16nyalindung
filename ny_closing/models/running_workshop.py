from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class RunningWorkshopLine(models.Model):
    _name = 'running.workshop.distribution.line'
    _description = 'Distribution Cost on Running Procedure'

    running_line_id = fields.Many2one('running.workshop.line', 'Running Line', ondelete='cascade')
    plantation_src_journal_id = fields.Many2one('account.journal', string='Source Journal', ondelete='restrict')
    distributed_cost = fields.Float()

class RunningWorkshopLine(models.Model):
    _name = 'running.workshop.line'
    _description = 'Summary Workshop Log for Running Procedure'

    running_id = fields.Many2one('running.workshop', 'Running Procedure', ondelete='cascade')
    workshop_id = fields.Many2one(related='running_id.workshop_id', store=True)
    plantation_location_type_id = fields.Many2one('lhm.location.type', string='Tipe Lokasi', ondelete='restrict')
    plantation_location_id = fields.Many2one('lhm.location', string='Lokasi', ondelete='restrict')
    plantation_activity_id = fields.Many2one('lhm.activity', string='Aktivitas', ondelete='restrict')
    dest_account_id = fields.Many2one('account.account', string='Dest. Account', ondelete='restrict')
    usage = fields.Float()
    distributed_cost = fields.Float()
    distribution_line_ids = fields.One2many('running.workshop.distribution.line', 'running_line_id', string='Distribution Lines')

class RunningWorkshop(models.Model):
    _name = 'running.workshop' 
    _description = 'Running Workshop Procedure'

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')
    
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    workshop_id = fields.Many2one('lhm.utility', string='Workshop', ondelete='restrict', domain="[('type','=', 'ws')]", required=True)
    closing_account_id = fields.Many2one('account.account', string='Account')

    line_ids = fields.One2many('running.workshop.line', 'running_id')
    total_usage = fields.Float()
    total_cost = fields.Float()

    running_move_id = fields.Many2one('account.move', string='Journal Entry')

    def init(self):
        _logger.info("Create SUMMARY RUNNING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.procedure_running_workshop(
                                p_running_workshop_id integer, p_workshop_id integer,
                                p_user_id integer, p_company_id integer) 
            RETURNS void AS
            $BODY$
            DECLARE
                v_existing_move_id integer;
                v_running_workshop_date_from date;
                v_running_workshop_date_to date;
                v_total_usage numeric := 0.0;
                v_total_cost numeric := 0.0;
                sums_usage record;
                v_activity_account_id integer := 0;
                v_distributed_cost numeric := 0.0;
                v_running_workshop_line_id integer;
                sums_aml_per_src record;
                v_distributed_cost_per_src numeric := 0.0;
            BEGIN
                select date_from from running_workshop where id=p_running_workshop_id INTO v_running_workshop_date_from;
                select date_to from running_workshop where id=p_running_workshop_id INTO v_running_workshop_date_to;

                DELETE FROM running_workshop_line WHERE running_id=p_running_workshop_id;
                     
                select running_move_id from running_workshop where id=p_running_workshop_id INTO v_existing_move_id;
                
                IF v_existing_move_id>0 THEN
                    DELETE FROM account_move_line WHERE move_id=v_existing_move_id;
                END IF;
                
                select sum(lwl.use_hours) from lhm_workshop_line lwl, lhm_workshop lw 
                    where lwl.lhm_workshop_id=lw.id and lw.workshop_id=p_workshop_id 
                        and lwl.date>=v_running_workshop_date_from and lwl.date<=v_running_workshop_date_to 
                        and lw.state in ('confirmed','done') 
                    group by lw.workshop_id 
                    INTO v_total_usage;

                select SUM(aml.balance) as total_cost
                    from lhm_utility lu, account_move_line aml, lhm_location ll
                    where lu.id=p_workshop_id
                        and lu.location_id=ll.id
                        and aml.date>=v_running_workshop_date_from and aml.date<=v_running_workshop_date_to
                        and aml.parent_state='posted' 
                        and aml.plantation_location_type_id=ll.type_id
                        and aml.plantation_location_id=ll.id
                    group by lu.id INTO v_total_cost;
                            
                FOR sums_usage IN SELECT 
                                lwl2.location_type_id,
                                lwl2.location_id,
                                lwl2.activity_id,
                                SUM(lwl2.use_hours) as usage 
                            FROM lhm_workshop_line lwl2, lhm_workshop lw2
                                WHERE lw2.workshop_id=p_workshop_id and 
                                    lwl2.date>=v_running_workshop_date_from and 
                                    lwl2.date<=v_running_workshop_date_to 
                                    and lw2.state in ('confirmed','done')
                                GROUP BY lwl2.location_type_id, 
                                    lwl2.location_id, lwl2.activity_id
                LOOP
                    v_activity_account_id := 0;
                    select account_id from lhm_activity where id=sums_usage.activity_id INTO v_activity_account_id;
                    continue when v_activity_account_id=0;

                    v_distributed_cost := 0;
                    IF v_total_usage>0.0 THEN
                        v_distributed_cost := (v_total_cost/v_total_usage) * sums_usage.usage;
                    END IF;

                    INSERT INTO running_workshop_line
                            (id, running_id, workshop_id, 
                            plantation_location_type_id, plantation_location_id, 
                            plantation_activity_id, dest_account_id,
                            usage, distributed_cost,
                            create_uid, write_uid, create_date, write_date) 
                        VALUES (
                            nextval('running_workshop_line_id_seq'),
                            p_running_workshop_id,
                            p_workshop_id,
                            sums_usage.location_type_id,
                            sums_usage.location_id,
                            sums_usage.activity_id,
                            v_activity_account_id,
                            sums_usage.usage,
                            v_distributed_cost,
                            p_user_id, p_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'))
                        returning "id" into v_running_workshop_line_id;
                    
                    FOR sums_aml_per_src IN 
                            select aml.plantation_src_journal_id, SUM(aml.balance) as total_cost
                            from lhm_utility lu, account_move_line aml, lhm_location ll
                            where lu.id=p_workshop_id
                                and lu.location_id=ll.id
                                and aml.date>=v_running_workshop_date_from and aml.date<=v_running_workshop_date_to
                                and aml.parent_state='posted' 
                                and aml.plantation_location_type_id=ll.type_id
                                and aml.plantation_location_id=ll.id
                            group by aml.plantation_src_journal_id
                    LOOP
                        v_distributed_cost_per_src := 0;
                        IF v_total_usage>0.0 THEN
                            v_distributed_cost_per_src := (v_total_cost/v_total_usage) * sums_usage.usage;
                        END IF;

                        INSERT INTO running_workshop_distribution_line
                                (id, running_line_id, 
                                plantation_src_journal_id, distributed_cost, 
                                create_uid, write_uid, create_date, write_date) 
                            VALUES (
                                nextval('running_workshop_distribution_line_id_seq'),
                                v_running_workshop_line_id,
                                sums_aml_per_src.plantation_src_journal_id,
                                v_distributed_cost_per_src,
                                p_user_id, p_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
                    END LOOP;
                END LOOP;

                UPDATE running_workshop SET 
                        total_usage = v_total_usage,
                        total_cost = v_total_cost,
                        write_uid=p_user_id, 
                        write_date=(now() at time zone 'UTC')
                    WHERE id=p_running_workshop_id;
                UPDATE lhm_workshop SET 
                        state='done', write_uid=p_user_id, write_date=(now() at time zone 'UTC')
                    WHERE id in (SELECT lw3.id 
                                    FROM lhm_workshop_line lwl3, lhm_workshop lw3
                                    WHERE lwl3.lhm_workshop_id=lw3.id 
                                        and lw3.workshop_id=p_workshop_id 
                                        and lwl3.date>=v_running_workshop_date_from 
                                        and lwl3.date<=v_running_workshop_date_to);
            END;
            $BODY$
            LANGUAGE plpgsql VOLATILE
            COST 100;
            """)

    def summarize_move_line(self):
        for running in self:
            self.env.cr.execute(f"select procedure_running_workshop({running.id}, {running.workshop_id.id}, {self.env.user.id}, {self.env.company.id})")

    def create_account_move(self):
        running_journal = self.env.ref('ny_closing.plantation_running_workshop_journal')
        for running in self:
            move_lines = []
            for line in running.line_ids:
                if not line.dest_account_id:
                    raise ValidationError(_(f"Account not found for workshop {running.workshop_id.code}"))
                for dline in line.distribution_line_ids:
                    vals_dest = {
                        'name': 'Distribute Cost from Running Machine',
                        'plantation_location_type_id': line.plantation_location_type_id.id,
                        'plantation_location_id': line.plantation_location_id.id,
                        'plantation_activity_id': line.plantation_activity_id.id,
                        'plantation_src_journal_id': running_journal.id,
                        'account_id': line.dest_account_id.id,
                        'debit': dline.distributed_cost if dline.distributed_cost > 0 else 0.0,
                        'credit': abs(dline.distributed_cost) if dline.distributed_cost < 0 else 0.0,
                    }
                    move_lines.append((0,0,vals_dest))
                
                    vals_src = {
                        'name': 'Distribute Cost from Running Machine',
                        'plantation_location_type_id': line.workshop_id.location_id.type_id.id,
                        'plantation_location_id': line.workshop_id.location_id.id,
                        'plantation_activity_id': False,
                        'plantation_src_journal_id': dline.plantation_src_journal_id.id,
                        'account_id': line.running_id.closing_account_id.id,
                        # 'debit': abs(running.total_cost) if running.total_cost < 0 else 0.0,
                        'debit': abs(dline.distributed_cost) if dline.distributed_cost < 0 else 0.0,
                        # 'credit': running.total_cost if running.total_cost > 0 else 0.0,
                        'credit': dline.distributed_cost if dline.distributed_cost > 0 else 0.0,
                    }
                    move_lines.append((0,0,vals_src))
            
            values = {
                'date': running.date_to,
                'journal_id': running_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines,
            }
            new_move = self.env['account.move'].create(values)
            
            running.running_move_id = new_move.id

    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = [('plantation_location_type_id','=',self.workshop_id.location_id.type_id.id),
                            ('plantation_location_id','=',self.workshop_id.location_id.id),
                            ('date','>=',self.date_from),('date','<=',self.date_to),
                            ('parent_state','=','posted')]
        return action
