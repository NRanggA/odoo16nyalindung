# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    accrued_move_ids = fields.Many2many('account.move', 'hr_payslip_run_accrued_move_rel', 'payslip_run_id', 'move_id', string='Accrued Journal Entries')
    bill_move_ids = fields.Many2many('account.move', 'hr_payslip_run_bill_move_rel', 'payslip_run_id', 'move_id', string='Vendor Bills')

    def action_map_cost(self):
        self.slip_ids.action_map_cost()
    
    def action_view_cost_map(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll_account.hr_payslip_cost_map_action")
        action['domain'] = [('payslip_run_id','=',self.id)]
        return action
    
    def create_account_move(self):
        lhm_journal = self.env.ref('c10i_lhm_v16.plantation_lhm_journal')
        for batch in self:
            query_partner = f"SELECT partner_id FROM hr_payslip_cost_map WHERE payslip_run_id={batch.id} GROUP BY partner_id"
            self.env.cr.execute(query_partner)
            partner_ids = [result[0] for result in self.env.cr.fetchall()]
            accrual_to_create = []
            bill_to_create = []
            print("::::::::::::::::::::", partner_ids)
            for partner in self.env['res.partner'].browse(partner_ids):
                        # sum(map.debit_amount) as debit,
                        # sum(map.credit_amount) as credit,
                query = """SELECT 
                        plantation_location_type_id,
                        plantation_location_id,
                        plantation_activity_id,
                        account_id,
                        sum(debit_amount-credit_amount) as price_unit,
                        partner_id
                    FROM hr_payslip_cost_map
                    WHERE payslip_run_id=%s and partner_id=%s
                    GROUP BY partner_id, account_id, plantation_location_type_id,
                        plantation_location_id, plantation_activity_id 
                """
                self.env.cr.execute(query%(self.id, partner.id))
                accrual_move_lines = []
                # bill_move_lines = []
                # balance = 0.0
                ## Cost Accrual
                for vals in self.env.cr.dictfetchall():
                    vals.update({
                        'name': 'Gaji Karyawan',
                        'quantity': 1.0,
                        'tax_ids': False,
                        'plantation_src_journal_id': lhm_journal.id,
                    })
                    print(".................", vals)
                    accrual_move_lines.append((0,0,vals))
                    # balance += vals['debit'] - vals['credit']
                ## Counterpart Accrual
                # accrual_move_lines.append((0,0,{
                #     'partner_id': partner.id,
                #     'account_id': False,
                #     'name': f"Accrual Salary {batch.name} Period {batch.date_end.strftime('%m/%y')}",
                #     'debit': abs(balance) if balance < 0 else 0.0,
                #     'credit': balance if balance > 0 else 0.0,
                # }))
                ## reconcile Accrual on Bill
                # bill_move_lines.append((0,0,{
                #     'partner_id': partner.id,
                #     'account_id': False,
                #     'name': f"Payment Salary {batch.name} Period {batch.date_end.strftime('%m/%y')}",
                #     'price_unit': balance if balance > 0 else 0.0,
                #     'quantity': 1.0,
                # }))

                # accrual_to_create.append({
                #     'date': batch.date_end,
                #     'journal_id': self.env['account.journal'].search([('code','=','MISC')], limit=1).id,
                #     'move_type': 'entry',
                #     'line_ids': accrual_move_lines,
                # })
                print("::::::::::::::::::::", partner_ids)
                bill_to_create.append({
                    'date': batch.date_end,
                    'partner_id': partner.id,
                    'journal_id': self.env['account.journal'].search([('type','=','purchase')], limit=1).id,
                    'move_type': 'in_invoice',
                    'invoice_line_ids': accrual_move_lines,
                })

            # accrued_moves = self.env['account.move'].create(accrual_to_create)
            bill_moves = self.env['account.move'].create(bill_to_create)
            print("::::::::::::::::::::bill_moves", bill_moves)
            
            batch.write({
                # 'accrued_move_ids': list(map(lambda x1: Command.add(x1.id), accrued_moves)),
                'bill_move_ids': list(map(lambda x2: Command.link(x2.id), bill_moves))
            })
    
    def action_view_accrued_moves(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        if len(self.accrued_move_ids) > 1:
            action['domain'] = [('id', 'in', self.accrued_move_ids.ids)]
        elif self.accrued_move_ids:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.accrued_move_ids.id
        else:
            action['domain'] = [('id','=',0)]
        action['context'] = {'default_move_type': 'entry', 'view_no_maturity': True}
        return action

    def action_view_bill_moves(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        if len(self.bill_move_ids) > 1:
            action['domain'] = [('id', 'in', self.bill_move_ids.ids)]
        elif self.bill_move_ids:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.bill_move_ids.id
        else:
            action['domain'] = [('id','=',0)]
        return action