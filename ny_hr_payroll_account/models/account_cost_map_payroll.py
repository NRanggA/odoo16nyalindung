# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command, _
from odoo.exceptions import ValidationError, UserError

class AccountCostMapPayroll(models.Model):
    _name = 'account.cost.map.payroll'
    _description = 'Account Cost Mapping'

    payslip_run_ids = fields.Many2many('hr.payslip.run', 'account_cost_map_payslip_run_rel', string='Payslip Batch')
    date = fields.Date("Accounting Date", required=True)
    move_ids = fields.Many2many('account.move', 'account_cost_map_accrued_move_rel', string='Accrued Journal Entries')
    state = fields.Selection([('draft','New'),('mapped','Mapped'),('done','Posted')], default='draft', string='Status')

    def unlink(self):
        for rec in self:
            if rec.state!='draft' or rec.move_ids:
                raise UserError("Tidak dapat menghapus yang sudah pernah di proses")
        return super().unlink()

    def action_map_cost(self):
        for batch in self.payslip_run_ids:
            batch.sudo().action_map_cost_reclass()
        self.state = 'mapped'
    
    def action_view_cost_map(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll_account.hr_payslip_cost_map_action")
        if self.payslip_run_ids:
            if len(self.payslip_run_ids.ids)>1:
                action['domain'] = [('payslip_run_id','in',self.payslip_run_ids.ids),('gc_distribution','=',False),('type','=','reclass')]
            else:
                action['domain'] = [('payslip_run_id','=',self.payslip_run_ids.id),('gc_distribution','=',False),('type','=','reclass')]
        else:
            action['domain'] = [('payslip_run_id','=',0)]
        return action

    def action_view_gc_distribution(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll_account.hr_payslip_cost_map_action")
        if self.payslip_run_ids:
            if len(self.payslip_run_ids.ids)>1:
                action['domain'] = [('payslip_run_id','in',self.payslip_run_ids.ids),'|',('gc_distributed','=',True),('gc_distribution','=',True),('type','=','reclass')]
            else:
                action['domain'] = [('payslip_run_id','=',self.payslip_run_ids.id),'|',('gc_distributed','=',True),('gc_distribution','=',True),('type','=','reclass')]
        else:
            action['domain'] = [('payslip_run_id','=',0)]
        return action

    def create_account_move(self):
        lhm_journal = self.env.ref('c10i_lhm_v16.plantation_lhm_journal')
        
        if not self.payslip_run_ids.cost_map_ids:
            raise ValidationError(_("Please click Cost Mapping before creating the journal"))
        if len(self.payslip_run_ids)>1:
            query_partner = f"SELECT partner_id FROM hr_payslip_cost_map WHERE payslip_run_id=any(array{str(self.payslip_run_ids.ids)}) and type='reclass' GROUP BY partner_id"
        else:
            query_partner = f"SELECT partner_id FROM hr_payslip_cost_map WHERE payslip_run_id={self.payslip_run_ids.id} and type='reclass' GROUP BY partner_id"
        self.env.cr.execute(query_partner)
        
        partner_map = dict(map(lambda p: (p, []), [result[0] for result in self.env.cr.fetchall()]))
        rule_map = dict(map(lambda r: (r.id, r), self.payslip_run_ids.cost_map_ids.rule_id))
        
        for batch in self.payslip_run_ids:
            for partner in self.env['res.partner'].browse(partner_map.keys()):
                query = """SELECT 
                        rule_id,
                        plantation_varieties_id,
                        plantation_location_type_id,
                        plantation_location_id,
                        plantation_activity_id,
                        account_id,
                        sum(debit_amount) as debit,
                        sum(credit_amount) as credit,
                        partner_id
                    FROM hr_payslip_cost_map
                    WHERE payslip_run_id=%s and partner_id=%s and gc_distribution='false' and type='reclass'
                    GROUP BY partner_id, rule_id, account_id, plantation_varieties_id, 
                        plantation_location_type_id, plantation_location_id, 
                        plantation_activity_id 
                """
                self.env.cr.execute(query%(batch.id, partner.id))
                
                for vals in self.env.cr.dictfetchall():
                    vals.update({
                        'name': rule_map[vals['rule_id']].name,
                        'quantity': 1.0,
                        'tax_ids': False,
                        'plantation_src_journal_id': lhm_journal.id,
                    })
                    del vals['rule_id']
                    partner_map[partner.id].append((0,0,vals))
                    # balance += vals['debit'] - vals['credit']
                

        cost_move_to_create = []
        account = self.env.company.payroll_bill_account_id
        for partner_id, move_lines in partner_map.items():
            amount = sum([ml[2]['credit'] for ml in move_lines]) - sum([ml[2]['debit'] for ml in move_lines])
            reclass_move_vals = {
                'name': f'Reclass {account.name}',
                'account_id': account.id,
                'debit': amount if amount > 0 else 0,
                'credit': abs(amount) if amount < 0 else 0,
                'quantity': 1.0,
                'tax_ids': False,
            }
            balance = 0.0
            for a,b,ml in move_lines:
                balance += ml['debit'] - ml['credit']
            
            balance += reclass_move_vals['debit'] - reclass_move_vals['credit']

            cost_move_to_create.append({
                # 'date': self.payslip_run_ids[0].date_end,
                'date': self.date,
                'partner_id': partner_id,
                'journal_id': lhm_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines + [(0,0,reclass_move_vals)],
            })
        
        cost_moves = self.env['account.move'].create(cost_move_to_create)
        self.write({
            'move_ids': list(map(lambda x2: Command.link(x2.id), cost_moves))
        })
        return True
    
    def create_account_move_general_charge(self):
        lhm_journal = self.env.ref('c10i_lhm_v16.plantation_lhm_journal')

        if not self.payslip_run_ids.cost_map_ids:
            raise ValidationError(_("Please click Cost Mapping before creating the journal"))
        rule_map = dict(map(lambda r: (r.id, r), self.payslip_run_ids.cost_map_ids.rule_id))
        move_lines = []
        for batch in self.payslip_run_ids:
            query = """(SELECT 
                    plantation_varieties_id,
                    plantation_location_type_id,
                    plantation_location_id,
                    plantation_activity_id,
                    account_id,
                    sum(debit_amount-credit_amount) as balance
                FROM hr_payslip_cost_map
                WHERE payslip_run_id=%s and gc_distribution='true' and type='reclass'
                GROUP BY account_id, plantation_varieties_id, plantation_location_type_id,
                    plantation_location_id, plantation_activity_id)
                UNION ALL
                (SELECT
                    NULL as plantation_varieties_id, 
                    plantation_location_type_id,
                    plantation_location_id,
                    plantation_activity_id,
                    account_id,
                    sum(credit_amount-debit_amount) as balance
                FROM hr_payslip_cost_map
                WHERE payslip_run_id=%s and gc_distributed='true'
                GROUP BY account_id, plantation_varieties_id, plantation_location_type_id,
                    plantation_location_id, plantation_activity_id)
            """
            self.env.cr.execute(query%(batch.id,self.id))
            
            for vals in self.env.cr.dictfetchall():
                dr_amt = cr_amt = 0.0
                if vals['balance']>0:
                    dr_amt = vals['balance']
                else:
                    cr_amt = vals['balance']

                vals.update({
                    'name': "GC Distribution",
                    'plantation_src_journal_id': lhm_journal.id,
                    'debit': dr_amt,
                    'credit': cr_amt,
                })
                move_lines.append([0,0,vals])
            
        reclass_gc_vals = {
            'date': self.date,
            'journal_id': self.env['account.journal'].search([('type','=','general')], limit=1).id,
            'move_type': 'entry',
            'line_ids': move_lines,
        }
        gc_moves = self.env['account.move'].create(reclass_gc_vals)
            
        self.write({
            'move_ids': list(map(lambda x2: Command.link(x2.id), gc_moves))
        })
        return True

    def action_post(self):
        self.move_ids._post()
        self.state = 'done'

    def action_reset_move(self):
        pass

    def action_view_moves(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        if len(self.move_ids) > 1:
            action['domain'] = [('id', 'in', self.move_ids.ids)]
        elif self.move_ids:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.move_ids.id
        else:
            action['domain'] = [('id','=',0)]
        return action