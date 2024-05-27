from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

SELECTION_STATE = [('draft', 'New'),
            ('inventory', 'Inventory'),
            ('payroll', 'Payroll'),
            ('running_ws', 'Running Account Workshop'),
            ('running_vh', 'Running Account Vehicle'),
            ('running_ma', 'Running Account Machine'),
            ('infrastructure', 'Infrastructure'),
            ('nursery', 'Nursery'),
            ('cip', 'Construction in Progress'),
            ('plasma', 'Plasma'),
            ('inti', 'Mature/Immature Plant'),
            ('mill', 'Mill Cost Valuation'),
            ('close_period', 'Closing Period'),
            ('done', 'Completed')
            ]

class ClosingSequenceRunningAccount(models.Model):
    _name = "plantation.closing.running.account"
    _description = "Closing Running Account"
    _rec_name = 'running_id'

    closing_sequence_id = fields.Many2one('plantation.closing.sequence', string='Closing Entry', ondelete='cascade')
    running_id = fields.Many2one('plantation.running', string='Running Utilities')
    cost_allocation_id = fields.Many2one(related='running_id.cost_allocation_id', store=True)
    cost_center_id = fields.Many2one(related='running_id.cost_center_id', store=True)
    type = fields.Selection(related='running_id.type', string='Utilities Type', store=True)
    currency_id = fields.Many2one(related='closing_sequence_id.currency_id', store=True, string='Currency')
    total_usage = fields.Float()
    total_cost = fields.Monetary()

    line_ids = fields.One2many('plantation.closing.running.account.summary', 'closing_running_line_id', string='Detail Summary')

class ClosingSequenceRunningAccountSummary(models.Model):
    _name = "plantation.closing.running.account.summary"
    _description = "Closing Running Account Summary"

    closing_running_line_id = fields.Many2one('plantation.closing.running.account', string='Running Account', ondelete='cascade')
    running_id = fields.Many2one(related='closing_running_line_id.running_id', store=True, string='Running Utilities')
    currency_id = fields.Many2one(related='closing_running_line_id.currency_id', store=True, string='Currency')
    cost_allocation_id = fields.Many2one('plantation.cost.type')
    cost_center_id = fields.Many2one('plantation.cost.center')
    cost_activity_id = fields.Many2one('plantation.cost.activity')
    dest_account_id = fields.Many2one('account.account')
    usage = fields.Float()
    distributed_cost = fields.Monetary()

class ClosingSequenceAllocation(models.Model):
    _name = "plantation.closing.account.allocation"
    _description = "Closing Account Allocation"
    
    closing_sequence_id = fields.Many2one('plantation.closing.sequence', string='Closing Entry', ondelete='cascade')
    type = fields.Selection([('infras','Infrastructure'),('project_cip','Project CIP')], string='Allocation Type', required=True)
    infrastructure_id = fields.Many2one('plantation.infrastructure', string='Infrastructure', ondelete='restrict')
    project_cip_id = fields.Many2one('plantation.project', string='Project CIP', ondelete='restrict')
    # nursery_block_id = fields.Many2one('plantation.infrastructure', string='Infrastructure', ondelete='restrict')
    # planted_block_id = fields.Many2one('plantation.infrastructure', string='Infrastructure', ondelete='restrict')

    currency_id = fields.Many2one(related='closing_sequence_id.currency_id', store=True, string='Currency')
    cost_allocation_id = fields.Many2one('plantation.cost.type')
    cost_center_id = fields.Many2one('plantation.cost.center')
    # cost_activity_id = fields.Many2one('plantation.cost.activity')
    
    total_cost = fields.Monetary()

    line_ids = fields.One2many('plantation.closing.account.allocation.summary', 'closing_account_allocation_id', string='Detail Summary')

class ClosingSequenceAllocationSummary(models.Model):
    _name = "plantation.closing.account.allocation.summary"
    _description = "Closing Account Allocation Summary"

    closing_account_allocation_id = fields.Many2one('plantation.closing.account.allocation', string='Running Account', ondelete='cascade')

    cost_allocation_id = fields.Many2one('plantation.cost.type')
    cost_center_id = fields.Many2one('plantation.cost.center')
    cost_activity_id = fields.Many2one('plantation.cost.activity')
    dest_account_id = fields.Many2one('account.account')
    
    cost = fields.Monetary()
    currency_id = fields.Many2one(related='closing_account_allocation_id.currency_id', store=True, string='Currency')

class ClosingSequence(models.Model):
    _name = "plantation.closing.sequence"
    _description = "Closing Sequence"

    name = fields.Char('Number')
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda s: s.env.company.currency_id.id)

    state = fields.Selection(SELECTION_STATE, string='State', default='draft')
    company_id = fields.Many2one('res.company', string='Company', default=lambda s: s.env.company)

    def init(self):
        _logger.info("Create SUMMARY RUNNING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.closing_running_summary(p_closing_seq_id integer, p_type varchar(2), p_user integer)
RETURNS void AS
$BODY$
DECLARE
    plr record;
    sts record;
    v_existing_move_id integer;
    v_closing_seq_date_from date;
    v_closing_seq_date_to date;
    v_company_id integer;
    v_currency_id integer;
    v_closing integer;
    v_closing_running_line_id integer;
    v_total_usage numeric := 0.0;
    v_activity_account_id integer := 0;
    v_distributed_cost numeric := 0.0;
BEGIN
    select date_from from plantation_closing_sequence where id=p_closing_seq_id INTO v_closing_seq_date_from;
    select date_to from plantation_closing_sequence where id=p_closing_seq_id INTO v_closing_seq_date_to;
    select company_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_company_id;
    select currency_id from res_company where id=v_company_id INTO v_currency_id;

    IF p_type='ws' THEN
        select running_ws_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
    ELSIF p_type='vh' THEN
        select running_vh_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
    ELSE
        select running_ma_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
    END IF;

    IF v_existing_move_id>0 THEN
        DELETE FROM account_move_line WHERE move_id=v_existing_move_id;
    END IF;
    
    FOR plr IN 
        SELECT 
            plantation_running.id as running_id,
            plantation_running.cost_allocation_id as running_ca_id,
            plantation_running.cost_center_id as running_cc_id,
            plantation_running.type as type,
            SUM(account_move_line.balance) as total_cost
        FROM plantation_running,account_move_line
        WHERE plantation_running.company_id=v_company_id and plantation_running.active=true 
            and plantation_running.type=p_type
            and account_move_line.date>=v_closing_seq_date_from and account_move_line.date<=v_closing_seq_date_to
            and account_move_line.parent_state='posted' 
            and account_move_line.cost_allocation_id=plantation_running.cost_allocation_id
            and account_move_line.cost_center_id=plantation_running.cost_center_id
        GROUP BY plantation_running.id,plantation_running.type
        ORDER BY plantation_running.id DESC
    LOOP
        select sum(running_usage_value) from plantation_running_timesheet where running_id=plr.running_id and date>=v_closing_seq_date_from and date<=v_closing_seq_date_to and state in ('confirm','done') group by running_id INTO v_total_usage;

        INSERT INTO plantation_closing_running_account 
                (id,closing_sequence_id, running_id, cost_allocation_id, cost_center_id,
                type, currency_id, total_usage, total_cost, 
                create_uid, write_uid, create_date, write_date) 
            VALUES (
                nextval('plantation_closing_running_account_id_seq'),
                p_closing_seq_id,
                plr.running_id,
                plr.running_ca_id,
                plr.running_cc_id,
                plr.type,
                v_currency_id,
                v_total_usage,
                plr.total_cost,
                p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC')) 
            RETURNING id INTO v_closing_running_line_id;

        FOR sts IN SELECT cost_allocation_id,cost_center_id,cost_activity_id,SUM(running_usage_value) as usage FROM plantation_running_timesheet 
                WHERE running_id=plr.running_id and date>=v_closing_seq_date_from and date<=v_closing_seq_date_to and state in ('confirm','done')
                GROUP BY cost_allocation_id,cost_center_id,cost_activity_id
        LOOP
            v_activity_account_id := 0;
            select account_allocation_id from plantation_cost_activity where id=sts.cost_activity_id into v_activity_account_id;
            continue when v_activity_account_id=0;

            v_distributed_cost := 0;
            IF v_total_usage>0.0 THEN
                v_distributed_cost := (plr.total_cost/v_total_usage) * sts.usage;
            END IF;

            INSERT INTO plantation_closing_running_account_summary
                    (id, closing_running_line_id, running_id, currency_id, 
                    cost_allocation_id, cost_center_id, cost_activity_id, dest_account_id,
                    usage, distributed_cost,
                    create_uid, write_uid, create_date, write_date) 
                VALUES (
                    nextval('plantation_closing_running_account_summary_id_seq'),
                    v_closing_running_line_id,
                    plr.running_id,
                    v_currency_id,
                    sts.cost_allocation_id,
                    sts.cost_center_id,
                    sts.cost_activity_id,
                    v_activity_account_id,
                    sts.usage,
                    v_distributed_cost,
                    p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
        END LOOP;
    END LOOP;

    UPDATE plantation_running_activity SET 
            state='done', write_uid=p_user, write_date=(now() at time zone 'UTC')
        WHERE id in (SELECT  plantation_running_activity.id 
                        FROM plantation_running_activity,plantation_running_timesheet
                        WHERE plantation_running_activity.type=p_type 
                            and plantation_running_timesheet.date>=v_closing_seq_date_from 
                            and plantation_running_timesheet.date<=v_closing_seq_date_to
                        GROUP BY plantation_running_activity.id);
    UPDATE plantation_running_timesheet SET 
            state='done', write_uid=p_user, write_date=(now() at time zone 'UTC')
        WHERE id in (SELECT plantation_running_timesheet.id 
                        FROM plantation_running_timesheet,plantation_running_activity
                        WHERE plantation_running_activity.type=p_type 
                            and plantation_running_timesheet.date>=v_closing_seq_date_from 
                            and plantation_running_timesheet.date<=v_closing_seq_date_to);
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
""")

        _logger.info("Create JOURNAL CLOSING RUNNING function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.create_journal_closing_running_summary(p_closing_seq_id integer, p_type varchar(2), p_user integer)
RETURNS void AS
$BODY$
DECLARE
    cra record;
    cras record;
    v_closing_seq_date_from date;
    v_closing_seq_date_to date;
    v_company_id integer;
    v_currency_id integer;
    v_journal_id integer;
    v_existing_move_id integer;
    v_am_id integer;
    v_account_id integer;
    v_src_running_name varchar;
    v_src_running_code varchar;
    v_debit numeric := 0.0;
    v_credit numeric := 0.0;
    v_debit_ct numeric := 0.0;
    v_credit_ct numeric := 0.0;
BEGIN
    select date_from from plantation_closing_sequence where id=p_closing_seq_id into v_closing_seq_date_from;
    select date_to from plantation_closing_sequence where id=p_closing_seq_id into v_closing_seq_date_to;
    select company_id from plantation_closing_sequence where id=p_closing_seq_id into v_company_id;
    select currency_id from res_company where id=v_company_id into v_currency_id;
    select id from account_journal where type='general' into v_journal_id;

    IF p_type='ws' THEN
        select running_ws_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
        select ws_running_account_id from plantation_closing_sequence where id=p_closing_seq_id into v_account_id;
    ELSIF p_type='vh' THEN
        select running_vh_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
        select vh_running_account_id from plantation_closing_sequence where id=p_closing_seq_id into v_account_id;
    ELSE
        select running_ma_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
        select ma_running_account_id from plantation_closing_sequence where id=p_closing_seq_id into v_account_id;
    END IF;

    IF v_existing_move_id>0 THEN
        DELETE FROM account_move_line WHERE move_id=v_existing_move_id;
        v_am_id := v_existing_move_id;
    ELSE
        INSERT INTO account_move 
                (id, move_type, name, company_id, journal_id, state, date, currency_id, extract_state, 
                create_uid, write_uid, create_date, write_date) 
            VALUES (
                nextval('account_move_id_seq'), 
                'entry',
                NULL,
                v_company_id,
                v_journal_id, 
                'draft',
                v_closing_seq_date_to,
                v_currency_id,
                'no_extract_requested',
                1, 
                1, 
                (now() at time zone 'UTC'), 
                (now() at time zone 'UTC')) RETURNING id into v_am_id;
    END IF;

    FOR cra IN SELECT * FROM plantation_closing_running_account 
            WHERE closing_sequence_id=p_closing_seq_id and type=p_type 
                and plantation_closing_running_account.total_cost>0
    LOOP
        select name from plantation_running where id=cra.running_id into v_src_running_name;
        select code from plantation_running where id=cra.running_id into v_src_running_code;

        continue when cra.total_cost=0.0;
        v_debit := 0.0;
        v_credit := 0.0;

        IF cra.total_cost>0.0 THEN
            v_credit := cra.total_cost;
        ELSE
            v_debit := -1*cra.total_cost;
        END IF;

        IF v_debit>0.0 THEN
            INSERT INTO account_move_line 
                    (id, operating_unit_id, name, date_maturity, currency_id, date,
                    account_id, cost_allocation_id, cost_center_id, cost_activity_id,
                    debit, credit, amount_currency, move_id, 
                    create_uid, write_uid, create_date, write_date) 
                VALUES(
                    nextval('account_move_line_id_seq'), 
                    NULL, 
                    v_src_running_name, 
                    v_closing_seq_date_to,
                    v_currency_id, 
                    v_closing_seq_date_to,
                    v_account_id,
                    cra.cost_allocation_id,
                    cra.cost_center_id,
                    NULL,
                    v_debit, 
                    v_credit, 
                    0.0, 
                    v_am_id, 
                    p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
        END IF;


        FOR cras IN SELECT * FROM plantation_closing_running_account_summary WHERE closing_running_line_id=cra.id
        LOOP
            continue when cras.distributed_cost=0.0;
            v_debit_ct := 0.0;
            v_credit_ct := 0.0;

            IF cras.distributed_cost>0.0 THEN
                v_debit_ct := cras.distributed_cost;
            ELSE
                v_credit_ct := -1*cras.distributed_cost;
            END IF;

            INSERT INTO account_move_line 
                (id, operating_unit_id, name, date_maturity, currency_id, date,
                account_id, cost_allocation_id, cost_center_id, cost_activity_id, 
                debit, credit, amount_currency, move_id, 
                create_uid, write_uid, create_date, write_date) 
            VALUES(
                nextval('account_move_line_id_seq'), 
                NULL,
                v_src_running_name, 
                v_closing_seq_date_to,
                v_currency_id, 
                v_closing_seq_date_to,
                cras.dest_account_id,
                cras.cost_allocation_id,
                cras.cost_center_id,
                cras.cost_activity_id,
                v_debit_ct, 
                v_credit_ct, 
                0.0, 
                v_am_id, 
                p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
        END LOOP;

        IF v_credit>0.0 THEN
            INSERT INTO account_move_line 
                    (id, operating_unit_id, name, date_maturity, currency_id, date,
                    account_id, cost_allocation_id, cost_center_id, cost_activity_id,
                    debit, credit, amount_currency, move_id, 
                    create_uid, write_uid, create_date, write_date) 
                VALUES(
                    nextval('account_move_line_id_seq'), 
                    NULL, 
                    v_src_running_name, 
                    v_closing_seq_date_to,
                    v_currency_id, 
                    v_closing_seq_date_to,
                    v_account_id,
                    cra.cost_allocation_id,
                    cra.cost_center_id,
                    NULL,
                    v_debit, 
                    v_credit, 
                    0.0, 
                    v_am_id, 
                    p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
        END IF;
    END LOOP;

    IF p_type='ws' THEN
        UPDATE plantation_closing_sequence SET 
                running_ws_move_id=v_am_id, write_uid=p_user, write_date=(now() at time zone 'UTC')
            WHERE id=p_closing_seq_id;
    ELSIF p_type='vh' THEN
        UPDATE plantation_closing_sequence SET 
                running_vh_move_id=v_am_id, write_uid=p_user, write_date=(now() at time zone 'UTC')
            WHERE id=p_closing_seq_id;
    ELSE
        UPDATE plantation_closing_sequence SET 
                running_ma_move_id=v_am_id, write_uid=p_user, write_date=(now() at time zone 'UTC')
            WHERE id=p_closing_seq_id;
    END IF;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
""")
        
        _logger.info("Create JOURNAL ALLOCATION function...")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION public.create_journal_allocation_summary(p_closing_seq_id integer, p_type varchar(2), p_user integer)
RETURNS void AS
$BODY$
DECLARE
    caa record;
    caas record;
    v_closing_seq_date_from date;
    v_closing_seq_date_to date;
    v_company_id integer;
    v_currency_id integer;
    v_journal_id integer;
    v_existing_move_id integer;
    v_am_id integer;
    v_account_id integer;
    v_src_allocation_name varchar;
    v_src_allocation_code varchar;
    v_debit numeric := 0.0;
    v_credit numeric := 0.0;
    v_debit_ct numeric := 0.0;
    v_credit_ct numeric := 0.0;
BEGIN
    select date_from from plantation_closing_sequence where id=p_closing_seq_id into v_closing_seq_date_from;
    select date_to from plantation_closing_sequence where id=p_closing_seq_id into v_closing_seq_date_to;
    select company_id from plantation_closing_sequence where id=p_closing_seq_id into v_company_id;
    select currency_id from res_company where id=v_company_id into v_currency_id;
    select id from account_journal where type='general' into v_journal_id;

    IF p_type='infras' THEN
        select infras_allocation_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
        select infras_allocation_account_id from plantation_closing_sequence where id=p_closing_seq_id into v_account_id;
    ELSIF p_type='project_cip' THEN
        select project_allocation_move_id from plantation_closing_sequence where id=p_closing_seq_id INTO v_existing_move_id;
        select project_allocation_account_id from plantation_closing_sequence where id=p_closing_seq_id into v_account_id;
    END IF;

    IF v_existing_move_id>0 THEN
        DELETE FROM account_move_line WHERE move_id=v_existing_move_id;
        v_am_id := v_existing_move_id;
    ELSE
        INSERT INTO account_move 
                (id, move_type, name, company_id, journal_id, state, date, currency_id, extract_state, 
                create_uid, write_uid, create_date, write_date) 
            VALUES (
                nextval('account_move_id_seq'), 
                'entry',
                NULL,
                v_company_id,
                v_journal_id, 
                'draft',
                v_closing_seq_date_to,
                v_currency_id,
                'no_extract_requested',
                1, 
                1, 
                (now() at time zone 'UTC'), 
                (now() at time zone 'UTC')) RETURNING id into v_am_id;
    END IF;

    FOR caa IN SELECT * FROM plantation_closing_account_allocation 
            WHERE closing_sequence_id=p_closing_seq_id and type=p_type 
                and plantation_closing_account_allocation.total_cost>0
    LOOP
        IF p_type='infras' THEN
            select name from plantation_infrastructure where id=caa.infrastructure_id into v_src_allocation_name;
            select code from plantation_infrastructure where id=caa.infrastructure_id into v_src_allocation_code;
        ELSIF p_type='project_cip' THEN
            select name from plantation_project where id=caa.project_cip_id into v_src_allocation_name;
            select code from plantation_project where id=caa.project_cip_id into v_src_allocation_code;
        END IF;

        continue when caa.total_cost=0.0;
        v_debit := 0.0;
        v_credit := 0.0;

        IF caa.total_cost>0.0 THEN
            v_credit := caa.total_cost;
        ELSE
            v_debit := -1*caa.total_cost;
        END IF;

        IF v_debit>0.0 THEN
            INSERT INTO account_move_line 
                    (id, operating_unit_id, name, date_maturity, currency_id, date,
                    account_id, cost_allocation_id, cost_center_id, cost_activity_id,
                    debit, credit, amount_currency, move_id, 
                    create_uid, write_uid, create_date, write_date) 
                VALUES(
                    nextval('account_move_line_id_seq'), 
                    NULL, 
                    v_src_allocation_name, 
                    v_closing_seq_date_to,
                    v_currency_id, 
                    v_closing_seq_date_to,
                    v_account_id,
                    caa.cost_allocation_id,
                    caa.cost_center_id,
                    NULL,
                    v_debit, 
                    v_credit, 
                    0.0, 
                    v_am_id, 
                    p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
        END IF;


        FOR caas IN SELECT * FROM plantation_closing_account_allocation_summary WHERE closing_account_allocation_id=caa.id
        LOOP
            continue when caas.cost=0.0;
            v_debit_ct := 0.0;
            v_credit_ct := 0.0;

            IF caas.cost>0.0 THEN
                v_debit_ct := caas.cost;
            ELSE
                v_credit_ct := -1*caas.cost;
            END IF;

            INSERT INTO account_move_line 
                (id, operating_unit_id, name, date_maturity, currency_id, date,
                account_id, cost_allocation_id, cost_center_id, cost_activity_id, 
                debit, credit, amount_currency, move_id, 
                create_uid, write_uid, create_date, write_date) 
            VALUES(
                nextval('account_move_line_id_seq'), 
                NULL,
                v_src_allocation_name, 
                v_closing_seq_date_to,
                v_currency_id, 
                v_closing_seq_date_to,
                caas.dest_account_id,
                caas.cost_allocation_id,
                caas.cost_center_id,
                caas.cost_activity_id,
                v_debit_ct, 
                v_credit_ct, 
                0.0, 
                v_am_id, 
                p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
        END LOOP;

        IF v_credit>0.0 THEN
            INSERT INTO account_move_line 
                    (id, operating_unit_id, name, date_maturity, currency_id, date,
                    account_id, cost_allocation_id, cost_center_id, cost_activity_id,
                    debit, credit, amount_currency, move_id, 
                    create_uid, write_uid, create_date, write_date) 
                VALUES(
                    nextval('account_move_line_id_seq'), 
                    NULL, 
                    v_src_allocation_name, 
                    v_closing_seq_date_to,
                    v_currency_id, 
                    v_closing_seq_date_to,
                    v_account_id,
                    caa.cost_allocation_id,
                    caa.cost_center_id,
                    NULL,
                    v_debit, 
                    v_credit, 
                    0.0, 
                    v_am_id, 
                    p_user, p_user, (now() at time zone 'UTC'), (now() at time zone 'UTC'));
        END IF;
    END LOOP;

    IF p_type='infras' THEN
        UPDATE plantation_closing_sequence SET 
                infras_allocation_move_id=v_am_id, write_uid=p_user, write_date=(now() at time zone 'UTC')
            WHERE id=p_closing_seq_id;
    ELSIF p_type='project_cip' THEN
        UPDATE plantation_closing_sequence SET 
                project_allocation_move_id=v_am_id, write_uid=p_user, write_date=(now() at time zone 'UTC')
            WHERE id=p_closing_seq_id;
    END IF;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
""")

    def action_start(self):
        for rec in self:
            rec.state = 'inventory'

    # Sequence 1 : Inventory. Next : Payroll
    def action_close_inventory(self):
        for rec in self:
            rec.state = 'payroll'

    # Sequence 2 : Payroll. Next : Running Workshop
    def action_close_payroll(self):
        for rec in self:
            rec.state = 'running_ws'

    # Sequence 3 : Running Account Workshop. Next : Running VH
    running_ws_move_id = fields.Many2one('account.move', string='Journal Running Workshop')
    ws_running_account_id = fields.Many2one('account.account', 'Running Account Counterpart')
    def action_close_running_ws(self):
        for rec in self:
            if not rec.running_ws_move_id:
                raise ValidationError(_("Journal Running WS not found!. \nPlease create the journal running WS"))
            if rec.running_ws_move_id.state!='posted':
                raise ValidationError(_("Please post Running Journal Workshop"))
            rec.running_ws_move_id._post()
            rec.state = 'running_vh'

    def account_move_create_running_ws(self):
        for rec in self:
            if rec.running_ws_move_id and rec.running_ws_move_id.state!='draft':
                raise ValidationError(_('Journal Running Workshop Found. \nPlease set to draft those journal before Re-Compute Running Workshop Summary'))
            self.env.cr.execute(f"select create_journal_closing_running_summary({rec.id}, '{'ws'}', {self.env.user.id})")

    def action_summerize_running_ws(self):
        for rec in self:
            # Validation
            if rec.running_ws_move_id and rec.running_ws_move_id.state!='draft':
                raise ValidationError(_('Journal Running Workshop Found. \nPlease set to draft those journal before Re-Compute Running Workshop Summary'))
            # Delete existing Summary
            existing_summary = self.env['plantation.closing.running.account'].search([('closing_sequence_id','=',rec.id),
                ('type','=','ws')])
            if existing_summary:
                existing_summary.unlink()
            # Create summary baru
            self.env.cr.execute(f"select closing_running_summary({rec.id}, '{'ws'}', {self.env.user.id})")

    def action_summerize_and_create_move_running_ws(self):
        self.action_summerize_running_ws()
        self.account_move_create_running_ws()

    def action_view_closing_running_ws_summary(self):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_plantation_closing_running_account')
        result['domain'] = "[('closing_sequence_id','=',%s),('type','=','ws')]" % (self.id)
        return result

    def action_view_coresponding_ws_move_line(self):
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('parent_state','=','posted'),
            ('cost_allocation_id.code','=','WS')], order='date asc')
        if self.running_ws_move_id:
            move_lines += self.running_ws_move_id.line_ids
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_account_moves_journal_running_account')
        if len(move_lines) > 1:
            result['domain'] = "[('id','in',%s)]" % (move_lines.ids)
        elif len(move_lines)==1:
            result['domain'] = "[('id','=',%s)]" % (move_lines.id)
        else:
            result['domain'] = "[('id','=',0)]"
        return result

    # Sequence 4 : Running Account Kendaraan
    running_vh_move_id = fields.Many2one('account.move', string='Journal Running Vehicle')
    vh_running_account_id = fields.Many2one('account.account', 'Running Account Counterpart')
    def action_close_running_vh(self):
        for rec in self:
            if not rec.running_vh_move_id:
                raise ValidationError(_("Journal Running VH not found!. \nPlease create the journal running VH"))
            if rec.running_vh_move_id.state!='posted':
                raise ValidationError(_("Please post Running Journal Vehicle"))
            rec.running_vh_move_id._post()
            rec.state = 'running_ma'

    def account_move_create_running_vh(self):
        for rec in self:
            if rec.running_vh_move_id and rec.running_vh_move_id.state!='draft':
                raise ValidationError(_('Journal Running Vehicle Found. \nPlease set to draft those journal before Re-Compute Running Vehicle Summary'))
            self.env.cr.execute(f"select create_journal_closing_running_summary({rec.id}, '{'vh'}', {self.env.user.id})")

    def action_summerize_running_vh(self):
        for rec in self:
            # Validation
            if rec.running_vh_move_id and rec.running_vh_move_id.state!='draft':
                raise ValidationError(_('Journal Running Vehicle Found. \nPlease set to draft those journal before Re-Compute Running Vehicle Summary'))
            # Delete existing Summary
            existing_summary = self.env['plantation.closing.running.account'].search([('closing_sequence_id','=',rec.id),
                ('type','=','vh')])
            if existing_summary:
                existing_summary.unlink()
            # Create summary baru
            self.env.cr.execute(f"select closing_running_summary({rec.id}, '{'vh'}', {self.env.user.id})")

    def action_summerize_and_create_move_running_vh(self):
        self.action_summerize_running_vh()
        self.account_move_create_running_vh()

    def action_view_closing_running_vh_summary(self):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_plantation_closing_running_account')
        result['domain'] = "[('closing_sequence_id','=',%s),('type','=','vh')]" % (self.id)
        return result

    def action_view_coresponding_vh_move_line(self):
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('parent_state','=','posted'),
            ('cost_allocation_id.code','=','VH')], order='date asc')
        if self.running_vh_move_id:
            move_lines += self.running_vh_move_id.line_ids
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_account_moves_journal_running_account')
        if len(move_lines) > 1:
            result['domain'] = "[('id','in',%s)]" % (move_lines.ids)
        elif len(move_lines)==1:
            result['domain'] = "[('id','=',%s)]" % (move_lines.id)
        else:
            result['domain'] = "[('id','=',0)]"
        return result

    # Sequence 5 : Running Account Mesin
    running_ma_move_id = fields.Many2one('account.move', string='Journal Running Machine')
    ma_running_account_id = fields.Many2one('account.account', 'Running Account Counterpart')
    def action_close_running_ma(self):
        for rec in self:
            if not rec.running_ma_move_id:
                raise ValidationError(_("Journal Running VH not found!. \nPlease create the journal running VH"))
            if rec.running_ma_move_id.state!='posted':
                raise ValidationError(_("Please post Running Journal Vehicle"))
            rec.running_ma_move_id._post()
            rec.state = 'infrastructure'

    def account_move_create_running_ma(self):
        for rec in self:
            if rec.running_ma_move_id and rec.running_ma_move_id.state!='draft':
                raise ValidationError(_('Journal Running Machine Found. \nPlease set to draft those journal before Re-Compute Running Machine Summary'))
            self.env.cr.execute(f"select create_journal_closing_running_summary({rec.id}, '{'ma'}', {self.env.user.id})")

    def action_summerize_running_ma(self):
        for rec in self:
            # Validation
            if rec.running_ma_move_id and rec.running_ma_move_id.state!='draft':
                raise ValidationError(_('Journal Running Machine Found. \nPlease set to draft those journal before Re-Compute Running Machine Summary'))
            # Delete existing Summary
            existing_summary = self.env['plantation.closing.running.account'].search([('closing_sequence_id','=',rec.id),
                ('type','=','ma')])
            if existing_summary:
                existing_summary.unlink()
            # Create summary baru
            self.env.cr.execute(f"select closing_running_summary({rec.id}, '{'ma'}', {self.env.user.id})")

    def action_summerize_and_create_move_running_ma(self):
        self.action_summerize_running_ma()
        self.account_move_create_running_ma()

    def action_view_closing_running_ma_summary(self):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_plantation_closing_running_account')
        result['domain'] = "[('closing_sequence_id','=',%s),('type','=','ma')]" % (self.id)
        return result

    def action_view_coresponding_ma_move_line(self):
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('parent_state','=','posted'),
            ('cost_allocation_id.code','=','MA')], order='date asc')
        if self.running_ma_move_id:
            move_lines += self.running_ma_move_id.line_ids
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_account_moves_journal_running_account')
        if len(move_lines) > 1:
            result['domain'] = "[('id','in',%s)]" % (move_lines.ids)
        elif len(move_lines)==1:
            result['domain'] = "[('id','=',%s)]" % (move_lines.id)
        else:
            result['domain'] = "[('id','=',0)]"
        return result

    # Sequence 6 : Infrastruktur
    infras_allocation_move_id = fields.Many2one('account.move', string='Journal Infrastructure Allocation')
    src_infras_account_id = fields.Many2one('account.account', 'Source Infrastructure Account')
    infras_allocation_account_id = fields.Many2one('account.account', 'Infrastructure Allocation Counterpart')
    
    def action_close_infras(self):
        for rec in self:
            if not rec.infras_allocation_move_id:
                raise ValidationError(_("Journal Infrastructure Allocation not found!. \nPlease create the journal Infrastructure Allocation"))
            if rec.infras_allocation_move_id.state!='posted':
                raise ValidationError(_("Please post Running Infrastructure Allocation"))
            rec.infras_allocation_move_id._post()
            rec.state = 'nursery'

    def action_summerize_infras_move_line(self):
        # Validation
        if self.infras_allocation_move_id and self.infras_allocation_move_id.state!='draft':
            raise ValidationError(_('Journal Infrastructure Allocation Found. \nPlease set to draft those journal before Re-Compute Infras Allocation Summary'))
        # Delete existing Summary
        existing_summary = self.env['plantation.closing.account.allocation'].search([('closing_sequence_id','=',self.id),
            ('type','=','infras')])
        if existing_summary:
            existing_summary.unlink()

        all_infrastructures = self.env['plantation.infrastructure'].search([])
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),
                ('account_id', '=', self.src_infras_account_id.id),
                ('cost_allocation_id', 'in', all_infrastructures.mapped('cost_allocation_id').ids),
                ('cost_center_id', '!=', False)])
        
        for infras in all_infrastructures:
            if not infras.closing_allocation_to_cost_account_id:
                raise ValidationError(_('Infrastruktur %s tidak memiliki Akun Beban Infrastruktur (Default). \
                    \nSilahkan diisi melalui menu Infrastruktur') %(infras.code))
            # Create Header
            infras_moves = move_lines.filtered(lambda l: l.cost_center_id.id==infras.cost_center_id.id)
            header_dict_vals = {
                'closing_sequence_id': self.id,
                'type': 'infras',
                'infrastructure_id': infras.id,
                'cost_allocation_id': infras.cost_allocation_id.id,
                'cost_center_id': infras.cost_center_id.id,
                'total_cost': sum([(x.debit-x.credit) for x in infras_moves]),
                'line_ids': [],
            }
            line_values = {}
            if infras.closing_allocation_type=='to_land_block' and infras.closing_allocation_to_planted_block_id:
                line_values = {
                    'cost_allocation_id': infras.closing_allocation_to_planted_block_id.cost_allocation_id.id,
                    'cost_center_id': infras.closing_allocation_to_planted_block_id.cost_center_id.id,
                    'cost_activity_id': False, # TODO : input OP activity jika memang perlu dibebankan ke OP Activity
                    'dest_account_id': infras.closing_allocation_to_block_account_id.id if infras.closing_allocation_to_block_account_id else infras.closing_allocation_to_cost_account_id.id,
                    'cost': header_dict_vals['total_cost'],
                }
            elif infras.closing_allocation_type=='to_indirect_cost' and infras.closing_allocation_to_cost_center_idc_id:
                line_values = {
                    'cost_allocation_id': infras.closing_allocation_to_cost_center_idc_id.type_id.id,
                    'cost_center_id': infras.closing_allocation_to_cost_center_idc_id.id,
                    'cost_activity_id': False, # TODO : input OP activity jika memang perlu dibebankan ke OP Activity
                    'dest_account_id': infras.closing_allocation_to_cost_account_id.id,
                    'cost': header_dict_vals['total_cost'],
                }
            elif infras.closing_allocation_type=='to_general_charge' and infras.closing_allocation_to_cost_center_gc_id:
                line_values = {
                    'cost_allocation_id': infras.closing_allocation_to_cost_center_gc_id.type_id.id,
                    'cost_center_id': infras.closing_allocation_to_cost_center_gc_id.id,
                    'cost_activity_id': False, # TODO : input OP activity jika memang perlu dibebankan ke OP Activity
                    'dest_account_id': infras.closing_allocation_to_cost_account_id.id,
                    'cost': header_dict_vals['total_cost'],
                }
            else:
                line_values = {
                    'cost_allocation_id': False,
                    'cost_center_id': False,
                    'cost_activity_id': False, # TODO : input OP activity jika memang perlu dibebankan ke OP Activity
                    'dest_account_id': infras.closing_allocation_to_cost_account_id.id,
                    'cost': header_dict_vals['total_cost'],
                }
            if line_values:
                header_dict_vals['line_ids'].append((0,0,line_values))
            self.env['plantation.closing.account.allocation'].create(header_dict_vals)
        return True

    def account_move_create_infrastructure(self):
        for rec in self:
            if self.infras_allocation_move_id and rec.infras_allocation_move_id.state!='draft':
                raise ValidationError(_('Journal Infrastructure Allocation Found. \nPlease set to draft those journal before Re-Compute Infras Allocation Summary'))
            self.env.cr.execute(f"select create_journal_allocation_summary({rec.id}, '{'infras'}', {self.env.user.id})")

    def action_summerize_and_create_move_infras(self):
        self.action_summerize_infras_move_line()
        self.account_move_create_infrastructure()

    def action_view_infras_allocation_summary(self):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_plantation_closing_account_allocation')
        result['domain'] = "[('closing_sequence_id','=',%s),('type','=','infras')]" % (self.id)
        return result

    def action_view_coresponding_infras_move_line(self):
        all_infrastructures = self.env['plantation.infrastructure'].search([])
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('parent_state','=','posted'),
            ('cost_allocation_id','in',all_infrastructures.mapped('cost_allocation_id').ids)], order='date asc')
        if self.infras_allocation_move_id:
            move_lines += self.infras_allocation_move_id.line_ids
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_account_moves_journal_running_account')
        if len(move_lines) > 1:
            result['domain'] = "[('id','in',%s)]" % (move_lines.ids)
        elif len(move_lines)==1:
            result['domain'] = "[('id','=',%s)]" % (move_lines.id)
        else:
            result['domain'] = "[('id','=',0)]"
        return result

    # Sequence 7 : Bibitan
    def action_close_nursery(self):
        for rec in self:
            rec.state = 'cip'

    def action_view_coresponding_nursery_move_line(self):
        all_nursery = self.env['plantation.land.nursery'].search([])
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('parent_state','=','posted'),
            ('cost_allocation_id','in',all_nursery.mapped('cost_allocation_id').ids)], order='date asc')
        if self.nursery_allocation_move_id:
            move_lines += self.nursery_allocation_move_id.line_ids
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_account_moves_journal_running_account')
        if len(move_lines) > 1:
            result['domain'] = "[('id','in',%s)]" % (move_lines.ids)
        elif len(move_lines)==1:
            result['domain'] = "[('id','=',%s)]" % (move_lines.id)
        else:
            result['domain'] = "[('id','=',0)]"
        return result

    # Sequence 8 : Construction in Progress
    project_allocation_move_id = fields.Many2one('account.move', string='Journal Project CIP Allocation')
    src_project_account_id = fields.Many2one('account.account', 'CIP Account')
    project_allocation_account_id = fields.Many2one('account.account', 'CIP Allocation Counterpart')
    
    def action_close_cip(self):
        for rec in self:
            if not rec.project_allocation_move_id:
                raise ValidationError(_("Journal Project CIP Allocation not found!. \nPlease create the journal Project CIP Allocation"))
            if rec.project_allocation_move_id.state!='posted':
                raise ValidationError(_("Please post Journal Project CIP Allocation"))
            rec.project_allocation_move_id._post()
            rec.state = 'plasma'

    def action_summerize_project_move_line(self):
        # Validation
        if self.project_allocation_move_id and self.project_allocation_move_id.state!='draft':
            raise ValidationError(_('Journal Project CIP Allocation Found. \nPlease set to draft those journal before Re-Compute Infras Allocation Summary'))
        # Delete existing Summary
        existing_summary = self.env['plantation.closing.account.allocation'].search([('closing_sequence_id','=',self.id),
            ('type','=','project_cip')])
        if existing_summary:
            existing_summary.unlink()

        all_project_cips = self.env['plantation.project'].search([('state','in',['inprogress','done'])])
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),
                ('account_id', '=', self.src_project_account_id.id),
                ('cost_allocation_id', 'in', all_project_cips.mapped('cost_center_id.type_id').ids),
                ('cost_center_id', '!=', False)])
        
        for project in all_project_cips:
            if not project.category_id.cip_account_id:
                raise ValidationError(_('Project %s tidak memiliki Akun Beban CIP. \
                    \nSilahkan diisi melalui menu Project Category') %(project.code))
            # Create Header
            project_moves = move_lines.filtered(lambda l: l.cost_center_id.id==project.cost_center_id.id)
            if not project_moves:
                continue

            header_dict_vals = {
                'closing_sequence_id': self.id,
                'type': 'project_cip',
                'project_cip_id': project.id,
                'cost_allocation_id': project.cost_center_id.type_id.id,
                'cost_center_id': project.cost_center_id.id,
                'total_cost': sum([(x.debit-x.credit) for x in project_moves]),
                'line_ids': [(0,0,{
                    'cost_allocation_id': False,
                    'cost_center_id': False,
                    'cost_activity_id': False, # TODO : input OP activity jika memang perlu dibebankan ke OP Activity
                    'dest_account_id': project.category_id.cip_account_id.id,
                    'cost': sum([(x.debit-x.credit) for x in project_moves]),
                    })],
            }
            self.env['plantation.closing.account.allocation'].create(header_dict_vals)
        return True

    def account_move_create_project(self):
        for rec in self:
            if self.project_allocation_move_id and rec.project_allocation_move_id.state!='draft':
                raise ValidationError(_('Journal Project CIP Allocation Found. \nPlease set to draft those journal before Re-Compute Infras Allocation Summary'))
            self.env.cr.execute(f"select create_journal_allocation_summary({rec.id}, '{'project_cip'}', {self.env.user.id})")

    def action_summerize_and_create_move_project(self):
        self.action_summerize_project_move_line()
        self.account_move_create_project()

    def action_view_project_allocation_summary(self):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_plantation_closing_account_allocation')
        result['domain'] = "[('closing_sequence_id','=',%s),('type','=','project_cip')]" % (self.id)
        return result

    def action_view_coresponding_project_move_line(self):
        move_lines = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('parent_state','=','posted'),
            ('cost_allocation_id.code','=','PJ')], order='date asc')
        if self.project_allocation_move_id:
            move_lines += self.project_allocation_move_id.line_ids
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_plantation_account.action_account_moves_journal_running_account')
        if len(move_lines) > 1:
            result['domain'] = "[('id','in',%s)]" % (move_lines.ids)
        elif len(move_lines)==1:
            result['domain'] = "[('id','=',%s)]" % (move_lines.id)
        else:
            result['domain'] = "[('id','=',0)]"
        return result

    # Sequence 9 : Plasma
    def action_close_plasma(self):
        for rec in self:
            rec.state = 'inti'

    # Sequence 10 : TM TBM
    def action_close_inti(self):
        for rec in self:
            rec.state = 'mill'

    # Sequence 11 : Mill Cost Valuation
    def action_close_mill(self):
        for rec in self:
            rec.state = 'close_period'

    # Sequence 12 : Closing Period
    def action_close_period(self):
        for rec in self:
            rec.state = 'done'
