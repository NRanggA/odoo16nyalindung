from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class RunningVehicleLine(models.Model):
    _name = 'running.vehicle.distribution.line'
    _description = 'Distribution Cost on Running Vehicle Procedure'

    running_line_id = fields.Many2one('running.vehicle.line', 'Running Line', ondelete='cascade')
    plantation_src_journal_id = fields.Many2one('account.journal', string='Source Journal', ondelete='restrict')
    distributed_cost = fields.Float()

class RunningVehicleLine(models.Model):
    _name = 'running.vehicle.line'
    _description = 'Summary Vehicle Log for Running Procedure'

    running_id = fields.Many2one('running.vehicle', 'Running Procedure', ondelete='cascade')
    vehicle_id = fields.Many2one(related='running_id.vehicle_id', store=True)
    plantation_location_type_id = fields.Many2one('lhm.location.type', string='Tipe Lokasi', ondelete='restrict')
    plantation_location_id = fields.Many2one('lhm.location', string='Lokasi', ondelete='restrict')
    plantation_activity_id = fields.Many2one('lhm.activity', string='Aktivitas', ondelete='restrict')
    dest_account_id = fields.Many2one('account.account', string='Account', ondelete='restrict')
    usage = fields.Float()
    distributed_cost = fields.Float()
    distribution_line_ids = fields.One2many('running.vehicle.distribution.line', 'running_line_id', string='Distribution Lines')

class RunningVehicle(models.Model):
    _name = 'running.vehicle' 
    _description = 'Running Vehicle Procedure'
    _rec_name = 'vehicle_id'

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')
    
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    vehicle_id = fields.Many2one('lhm.utility', string='Kendaraan', ondelete='restrict', domain="[('type','=', 'vh')]", required=True)
    closing_account_id = fields.Many2one('account.account', string='Closing Account')

    line_ids = fields.One2many('running.vehicle.line', 'running_id')
    total_usage = fields.Float()
    total_cost = fields.Float()

    running_move_id = fields.Many2one('account.move', string='Journal Entry')

    def init(self):
        _logger.info("Create SUMMARY RUNNING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.procedure_running_vehicle(
                                p_running_vehicle_id integer, p_vehicle_id integer,
                                p_user_id integer, p_company_id integer) 
            RETURNS void AS
            $BODY$
            DECLARE
                v_existing_move_id integer;
                v_running_vehicle_date_from date;
                v_running_vehicle_date_to date;
                v_total_usage numeric := 0.0;
                v_total_cost numeric := 0.0;
                sums_usage record;
                v_activity_account_id integer := 0;
                v_distributed_cost numeric := 0.0;
                v_running_vehicle_line_id integer;
                sums_aml_per_src record;
                v_distributed_cost_per_src numeric := 0.0;
            BEGIN
                select date_from from running_vehicle where id=p_running_vehicle_id INTO v_running_vehicle_date_from;
                select date_to from running_vehicle where id=p_running_vehicle_id INTO v_running_vehicle_date_to;

                DELETE FROM running_vehicle_line WHERE running_id=p_running_vehicle_id;
                     
                select running_move_id from running_vehicle where id=p_running_vehicle_id INTO v_existing_move_id;
                
                IF v_existing_move_id>0 THEN
                    DELETE FROM account_move_line WHERE move_id=v_existing_move_id;
                END IF;
                
                select sum(lvl.difference_value) from lhm_vehicle_line lvl, lhm_vehicle lv 
                    where lvl.lhm_vehicle_id=lv.id and lv.vehicle_id=p_vehicle_id 
                        and lvl.date>=v_running_vehicle_date_from and lvl.date<=v_running_vehicle_date_to 
                        and lv.state in ('confirmed','done') 
                    group by lv.vehicle_id 
                    INTO v_total_usage;

                select SUM(aml.balance) as total_cost
                    from lhm_utility lu, account_move_line aml, lhm_location ll
                    where lu.id=p_vehicle_id
                        and lu.location_id=ll.id
                        and aml.date>=v_running_vehicle_date_from and aml.date<=v_running_vehicle_date_to
                        and aml.parent_state='posted' 
                        and aml.plantation_location_type_id=ll.type_id
                        and aml.plantation_location_id=ll.id
                    group by lu.id INTO v_total_cost;
                            
                FOR sums_usage IN SELECT 
                                lvl2.location_type_id,
                                lvl2.location_id,
                                lvl2.activity_id,
                                SUM(lvl2.difference_value) as usage 
                            FROM lhm_vehicle_line lvl2, lhm_vehicle lv2
                                WHERE lv2.vehicle_id=p_vehicle_id and 
                                    lvl2.date>=v_running_vehicle_date_from and 
                                    lvl2.date<=v_running_vehicle_date_to 
                                    and lv2.state in ('confirmed','done')
                                GROUP BY lvl2.location_type_id, 
                                    lvl2.location_id, lvl2.activity_id
                LOOP
                    v_activity_account_id := 0;
                    select account_id from lhm_activity where id=sums_usage.activity_id INTO v_activity_account_id;
                    continue when v_activity_account_id=0;

                    v_distributed_cost := 0;
                    IF v_total_usage>0.0 THEN
                        v_distributed_cost := (v_total_cost/v_total_usage) * sums_usage.usage;
                    END IF;

                    INSERT INTO running_vehicle_line
                            (id, running_id, vehicle_id, 
                            plantation_location_type_id, plantation_location_id, 
                            plantation_activity_id, dest_account_id,
                            usage, distributed_cost,
                            create_uid, write_uid, create_date, write_date) 
                        VALUES (
                            nextval('running_vehicle_line_id_seq'),
                            p_running_vehicle_id,
                            p_vehicle_id,
                            sums_usage.location_type_id,
                            sums_usage.location_id,
                            sums_usage.activity_id,
                            v_activity_account_id,
                            sums_usage.usage,
                            v_distributed_cost,
                            p_user_id, p_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'))
                        returning "id" into v_running_vehicle_line_id;
                    
                    FOR sums_aml_per_src IN 
                            select aml.plantation_src_journal_id, SUM(aml.balance) as total_cost
                            from lhm_utility lu, account_move_line aml, lhm_location ll
                            where lu.id=p_vehicle_id
                                and lu.location_id=ll.id
                                and aml.date>=v_running_vehicle_date_from and aml.date<=v_running_vehicle_date_to
                                and aml.parent_state='posted' 
                                and aml.plantation_location_type_id=ll.type_id
                                and aml.plantation_location_id=ll.id
                            group by aml.plantation_src_journal_id
                    LOOP
                        v_distributed_cost_per_src := 0;
                        IF v_total_usage>0.0 THEN
                            v_distributed_cost_per_src := (v_total_cost/v_total_usage) * sums_usage.usage;
                        END IF;

                        INSERT INTO running_vehicle_distribution_line
                                (id, running_line_id, 
                                plantation_src_journal_id, distributed_cost, 
                                create_uid, write_uid, create_date, write_date) 
                            VALUES (
                                nextval('running_vehicle_distribution_line_id_seq'),
                                v_running_vehicle_line_id,
                                sums_aml_per_src.plantation_src_journal_id,
                                v_distributed_cost_per_src,
                                p_user_id, p_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
                    END LOOP;
                END LOOP;

                UPDATE running_vehicle SET 
                        total_usage = v_total_usage,
                        total_cost = v_total_cost,
                        write_uid=p_user_id, 
                        write_date=(now() at time zone 'UTC')
                    WHERE id=p_running_vehicle_id;
                UPDATE lhm_vehicle SET 
                        state='done', write_uid=p_user_id, write_date=(now() at time zone 'UTC')
                    WHERE id in (SELECT lv3.id 
                                    FROM lhm_vehicle_line lvl3, lhm_vehicle lv3
                                    WHERE lvl3.lhm_vehicle_id=lv3.id 
                                        and lv3.vehicle_id=p_vehicle_id 
                                        and lvl3.date>=v_running_vehicle_date_from 
                                        and lvl3.date<=v_running_vehicle_date_to);
            END;
            $BODY$
            LANGUAGE plpgsql VOLATILE
            COST 100;
            """)

    def summarize_move_line(self):
        for running in self:
            self.env.cr.execute(f"select procedure_running_vehicle({running.id}, {running.vehicle_id.id}, {self.env.user.id}, {self.env.company.id})")

    def create_account_move(self):
        running_journal = self.env.ref('ny_closing.plantation_running_vehicle_journal')
        for running in self:
            if not running.total_cost or not running.total_usage:
                continue
            if running.running_move_id:
                if running.running_move_id.state=='posted':
                    running.running_move_id.button_draft()
            move_lines = []
            for line in running.line_ids:
                if not line.dest_account_id:
                    raise ValidationError(_(f"Account not found for Vehicle {running.vehicle_id.code}"))
                for dline in line.distribution_line_ids:
                    vals_dest = {
                        'name': 'Distribute Cost from Running Vehicle',
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
                        'name': 'Distribute Cost from Running Vehicle',
                        'plantation_location_type_id': line.vehicle_id.location_id.type_id.id,
                        'plantation_location_id': line.vehicle_id.location_id.id,
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
            if running.running_move_id:
                running.running_move_id.write(values)
            else:
                new_move = self.env['account.move'].create(values)
                running.running_move_id = new_move.id

    def action_view_src_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_closing.plantation_closing_aml_action")
        action['domain'] = [('plantation_location_type_id','=',self.vehicle_id.location_id.type_id.id),
                            ('plantation_location_id','=',self.vehicle_id.location_id.id),
                            ('date','>=',self.date_from),('date','<=',self.date_to),
                            ('parent_state','=','posted')]
        return action

    # def action_view_src_log(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll_account.hr_payslip_cost_map_action")
    #     action['domain'] = [('payslip_run_id','=',self.id)]
    #     return action
