# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    cost_map_ids = fields.One2many('hr.payslip.cost.map', 'payslip_run_id', string='Cost Mapping')

    accrued_move_ids = fields.Many2many('account.move', 'hr_payslip_run_accrued_move_rel', 'payslip_run_id', 'move_id', string='Accrued Journal Entries')
    bill_move_ids = fields.Many2many('account.move', 'hr_payslip_run_bill_move_rel', 'payslip_run_id', 'move_id', string='Vendor Bills')

    account_cost_map_payroll_ids = fields.Many2many('account.cost.map.payroll', 'account_cost_map_payslip_run_rel', 'hr_payslip_run_id', 'account_cost_map_payroll_id', string='Payslip Batch')

    def action_gc_distribution(self):
        self.ensure_one()
        query_get_gc = f"""SELECT 
                cm.partner_id, 
                cm.plantation_varieties_id, 
                cm.plantation_location_type_id, 
                cm.plantation_location_id,
                cm.plantation_activity_id, 
                array_agg(cm.id) as cm_ids, sum(cm.debit_amount) as cost  
            FROM hr_payslip_cost_map cm, lhm_location_type llt \
            WHERE cm.plantation_location_type_id=llt.id
                and llt.general_charge='true'
                and cm.payslip_run_id={self.id} 
                and cm.debit_amount>0 
                and cm.type='reclass'
            GROUP BY cm.partner_id,
                cm.plantation_varieties_id,
                cm.plantation_location_type_id,
                cm.plantation_location_id,
                cm.plantation_activity_id"""
        self.env.cr.execute(query_get_gc)
        gc_lines = self.env.cr.fetchall()
        cost_map_to_add = []
        field_cost_type = self.env['lhm.location.type'].search([('plantation','=',True)], limit=1)
        project_cost_type = self.env['lhm.location.type'].search([('project','=',True)], limit=1)
        for partner_id, varieties_id, type_id, location_id, activity_id, cm_ids, debit_amt in gc_lines:
            afdeling_found = self.env['res.afdeling'].search([('location_id','=',location_id)], limit=1)
            cost_center_found = self.env['account.cost.center'].search([('location_id','=',location_id)], limit=1)
            if afdeling_found:
                block_tanams = self.env['lhm.plant.block'].search([('varieties_id','=',varieties_id),('afdeling_id','=',afdeling_found.id),('planted','>',0)], order='status desc')
            elif cost_center_found:
                block_tanams = self.env['lhm.plant.block'].search([('varieties_id','=',varieties_id),('planted','>',0)], order='status desc')
            else:
                if varieties_id:
                    orgx = self.env['plant.varieties'].browse(varieties_id)
                    raise ValidationError(_(f"Tidak ditemukan Blok Tanam atas untuk ORG {orgx.name} dari proses distribusi GC dengan kode {cost_center_found.code}"))
                else:
                    raise ValidationError(_(f"Tidak ditemukan Blok Tanam atas dari proses distribusi GC dengan kode {cost_center_found.code}"))

            total_planted = sum(block_tanams.mapped('planted'))
            total_planted = total_planted if total_planted else 1
            n_block = len(block_tanams.ids)
            remaining_cost = debit_amt
            allocated_cost = 0.0
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>remaining_cost", remaining_cost)
            for block_tanam in block_tanams:
                if block_tanam.status != 'tbm':
                    continue

                if not block_tanam.payroll_gc_dest_activity_id:
                    raise ValidationError(_(f"Block Tanam {block_tanam.code} belum dapat setting Payroll GC to Block Activity"))
                pct_cost = block_tanam.planted / total_planted
                if n_block==1:
                    dr_amount = remaining_cost
                else:
                    dr_amount = round(pct_cost*debit_amt, 0)
                    
                cost_map_to_add.append({
                        'payslip_line_id': False,
                        'partner_id': partner_id,
                        'plantation_varieties_id': varieties_id,
                        # 'plantation_location_type_id': field_cost_type.id,
                        'plantation_location_type_id': block_tanam.location_type_id.id,
                        'plantation_location_id': block_tanam.location_id.id,
                        'plantation_activity_id': block_tanam.payroll_gc_dest_activity_id.id,
                        'account_id': block_tanam.payroll_gc_dest_activity_id.account_id.id,
                        'gc_distribution_debit_amount': dr_amount,
                        'slip_id': False,
                        'payslip_run_id': self.id,
                        'gc_distribution': True,
                        'type': 'reclass',
                    })
                n_block -= 1
                remaining_cost -= dr_amount
                allocated_cost += dr_amount
            
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>remaining_cost 2", remaining_cost)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>allocated_cost", allocated_cost)            
            if allocated_cost:
                check_indx3 = 1
                for cm in self.env['hr.payslip.cost.map'].browse(cm_ids):
                    if check_indx3==len(cm_ids):
                        gc_distributed_amt = allocated_cost
                    else:
                        gc_distributed_amt = round(allocated_cost*(cm.debit_amount/debit_amt), 0)

                    query_update_gc = f"""UPDATE hr_payslip_cost_map SET gc_distributed='true', 
                            gc_distribution_credit_amount={gc_distributed_amt} 
                            WHERE id={cm.id}"""
                    # plantation_varieties_id={varieties_id}
                    # and plantation_location_type_id={type_id}
                    # and plantation_location_id={location_id}
                    # and payslip_run_id={self.id}
                    # and debit_amount>0 
                    self.env.cr.execute(query_update_gc)
                    check_indx3 += 1
                    allocated_cost -= gc_distributed_amt
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>allocated_cost 2", allocated_cost)            

        if cost_map_to_add:
            self.env['hr.payslip.cost.map'].sudo().create(cost_map_to_add)

            
    def action_map_cost_reclass(self):
        self.cost_map_ids.sudo().filtered(lambda x: x.type=='reclass').unlink()
        self.slip_ids.action_map_cost_reclass()
        for batch in self:
            batch.action_gc_distribution()
    
    def action_map_cost_bill(self):
        self.cost_map_ids.sudo().filtered(lambda x: x.type=='bill').unlink()
        self.slip_ids.action_map_cost_bill()
    
    def done_payslip_run(self):
        self.action_map_cost_bill()
        return super().done_payslip_run()
    
    def action_view_cost_map(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll_account.hr_payslip_cost_map_action")
        action['domain'] = [('payslip_run_id','=',self.id),('type','=','bill')]
        return action
    
    def create_account_move(self):
        lhm_journal = self.env.ref('c10i_lhm_v16.plantation_lhm_journal')
        for batch in self:
            if not batch.cost_map_ids:
                raise ValidationError(_("Please click Cost Mapping before creating the journal"))
            query_partner = f"SELECT partner_id FROM hr_payslip_cost_map WHERE payslip_run_id={batch.id} and type='bill' GROUP BY partner_id"
            self.env.cr.execute(query_partner)
            partner_ids = [result[0] for result in self.env.cr.fetchall()]
            bill_to_create = []
            # print("::::::::::::::::::::", partner_ids)
            for partner in self.env['res.partner'].browse(partner_ids):
                query = """SELECT 
                        account_id,
                        sum(debit_amount-credit_amount) as price_unit,
                        partner_id
                    FROM hr_payslip_cost_map
                    WHERE payslip_run_id=%s and partner_id=%s and gc_distribution='false' and type='bill'
                    GROUP BY partner_id, account_id
                """
                self.env.cr.execute(query%(self.id, partner.id))
                move_lines = []
                
                for vals in self.env.cr.dictfetchall():
                    vals.update({
                        'name': 'Pengajuan Gaji',
                        'quantity': 1.0,
                        'tax_ids': False,
                        # 'plantation_src_journal_id': lhm_journal.id,
                    })
                    # print(".................", vals)
                    move_lines.append((0,0,vals))
                    # balance += vals['debit'] - vals['credit']
                
                # print("::::::::::::::::::::", partner_ids)
                bill_to_create.append({
                    'date': batch.date_end,
                    'partner_id': partner.id,
                    'journal_id': self.env['account.journal'].search([('type','=','purchase')], limit=1).id,
                    'move_type': 'in_invoice',
                    'invoice_line_ids': move_lines,
                })

            bill_moves = self.env['account.move'].sudo().create(bill_to_create)
            # print("::::::::::::::::::::bill_moves", bill_moves)
            
            batch.write({
                # 'accrued_move_ids': list(map(lambda x1: Command.add(x1.id), accrued_moves)),
                'bill_move_ids': list(map(lambda x2: Command.link(x2.id), bill_moves))
            })
    
    # Sudah tidak dipake
    def create_account_move_general_charge_old(self):
        lhm_journal = self.env.ref('c10i_lhm_v16.plantation_lhm_journal')
        for batch in self:
            if not batch.cost_map_ids:
                raise ValidationError(_("Please click Cost Mapping before creating the journal"))
            accrual_to_create = []
            # print("::::::::::::::::::::", partner_ids)
            query = """(SELECT 
                    plantation_location_type_id,
                    plantation_location_id,
                    plantation_activity_id,
                    account_id,
                    sum(debit_amount-credit_amount) as balance
                FROM hr_payslip_cost_map
                WHERE payslip_run_id=%s and gc_distribution='true'
                GROUP BY account_id, plantation_location_type_id,
                    plantation_location_id, plantation_activity_id)
                UNION ALL
                (SELECT 
                    plantation_location_type_id,
                    plantation_location_id,
                    plantation_activity_id,
                    account_id,
                    sum(credit_amount-debit_amount) as balance
                FROM hr_payslip_cost_map
                WHERE payslip_run_id=%s and gc_distributed='true'
                GROUP BY account_id, plantation_location_type_id,
                    plantation_location_id, plantation_activity_id)
            """
            self.env.cr.execute(query%(self.id,self.id))
            accrual_move_lines = []
            
            for vals in self.env.cr.dictfetchall():
                dr_amt = cr_amt = 0.0
                if vals['balance']>0:
                    dr_amt = vals['balance']
                else:
                    cr_amt = vals['balance']

                vals.update({
                    'name': 'Gaji Karyawan',
                    'plantation_src_journal_id': lhm_journal.id,
                    'debit': dr_amt,
                    'credit': cr_amt,
                })
                print(".................", vals)
                accrual_move_lines.append((0,0,vals))
                # balance += vals['debit'] - vals['credit']
            
            # print("::::::::::::::::::::", partner_ids)
            accrual_to_create.append({
                'date': batch.date_end,
                'journal_id': self.env['account.journal'].search([('type','=','general')], limit=1).id,
                'move_type': 'entry',
                'line_ids': accrual_move_lines,
            })

            gc_moves = self.env['account.move'].sudo().create(accrual_to_create)
            # print("::::::::::::::::::::bill_moves", bill_moves)
            
            batch.write({
                # 'accrued_move_ids': list(map(lambda x1: Command.add(x1.id), accrued_moves)),
                'bill_move_ids': list(map(lambda x2: Command.link(x2.id), gc_moves))
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