# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    def action_gae_distribution(self):
        self.ensure_one()
        gae_cm_lines = self.env['hr.payslip.cost.map'].sudo().search([
                                            ('payslip_run_id','=',self.id), 
                                            ('debit_amount','>',0),
                                            ('type','=','reclass'),
                                            '|',
                                                ('gae_distribution_id','!=',False),
                                                ('gae_to_location','!=',False),
                                            ])
        distributed_cm_to_add = []
        for cml in gae_cm_lines:
            if cml.gae_to_location and cml.gae_to_location_ids:
                block_tanams = self.env['lhm.plant.block'].search([('location_id','=',cml.gae_to_location_ids.ids)])
                remaining_cost = cml.debit_amount
                len_block = len(block_tanams.filtered(lambda l: l.planted>0).ids) - 1
                total_ha = sum(block_tanams.filtered(lambda l: l.planted>0).mapped('planted'))
                tm_per_varieaties = {}
                for block_planted in block_tanams.filtered(lambda l: l.planted>0):
                    if not len_block:
                        dr_amount = remaining_cost
                    else:
                        dr_amount = round(cml.debit_amount * block_planted.planted / total_ha,2)
                    if block_planted.status == 'tm':
                        if block_planted.varieties_id.id not in tm_per_varieaties:
                            tm_per_varieaties.update({block_planted.varieties_id.id: 0.0})
                        tm_per_varieaties[block_planted.varieties_id.id] += dr_amount
                        continue
                    vals_to_add = {
                        'payslip_line_id': cml.payslip_line_id.id,
                        'partner_id': cml.partner_id.id,
                        'plantation_varieties_id': block_planted.varieties_id.id,
                        'plantation_location_type_id': block_planted.location_type_id.id,
                        'plantation_location_id': block_planted.location_id.id,
                        'plantation_activity_id': block_planted.payroll_gc_dest_activity_id.id,
                        'account_id': block_planted.payroll_gc_dest_activity_id.account_id.id,
                        'gc_distribution_debit_amount': dr_amount,
                        'gc_distribution_credit_amount': 0.0,
                        'slip_id': cml.payslip_line_id.slip_id.id,
                        'payslip_run_id': self.id,
                        'gc_distribution': True,
                        'type': 'reclass',
                    }
                    distributed_cm_to_add.append(vals_to_add)
                    len_block -= 1
                    remaining_cost -= dr_amount
                
                for varieties_id, dr_amount in tm_per_varieaties.items():
                    vals_to_add = {
                        'payslip_line_id': cml.payslip_line_id.id,
                        'partner_id': cml.partner_id.id,
                        'plantation_varieties_id': varieties_id,
                        'account_id': cml.account_id.id,
                        'gc_distribution_debit_amount': dr_amount,
                        'gc_distribution_credit_amount': 0.0,
                        'slip_id': cml.payslip_line_id.slip_id.id,
                        'payslip_run_id': self.id,
                        'gc_distribution': True,
                        'type': 'reclass',
                    }
                    distributed_cm_to_add.append(vals_to_add)
            elif cml.gae_distribution_id:
                remaining_cost = cml.debit_amount
                len_dist = len(cml.gae_distribution_id.line_ids.ids) - 1
                for dist_plan in cml.gae_distribution_id.line_ids:
                    if not len_dist:
                        dr_amount = remaining_cost
                    else:
                        dr_amount = cml.debit_amount * dist_plan.distribution_percentage / 100.0
                    distributed_cm_to_add.append({
                        'payslip_line_id': cml.payslip_line_id.id,
                        'partner_id': cml.partner_id.id,
                        'plantation_varieties_id': dist_plan.varieties_id.id,
                        # 'plantation_location_type_id': field_cost_type.id,
                        # 'plantation_location_type_id': block_tanam.location_type_id.id,
                        # 'plantation_location_id': block_tanam.location_id.id,
                        # 'plantation_activity_id': block_tanam.payroll_gc_dest_activity_id.id,
                        'account_id': cml.account_id.id,
                        'gc_distribution_debit_amount': dr_amount,
                        'gc_distribution_credit_amount': 0.0,
                        'slip_id': cml.payslip_line_id.slip_id.id,
                        'payslip_run_id': self.id,
                        'gc_distribution': True,
                        'type': 'reclass',
                    })
                    len_dist -= 1
                    remaining_cost -= dr_amount
            cml.gc_distribution_credit_amount = cml.debit_amount
            cml.gc_distributed = True
            
        if distributed_cm_to_add:
            self.env['hr.payslip.cost.map'].sudo().create(distributed_cm_to_add)
    
    def action_gc_distribution_new_check(self):
        self.ensure_one()
        # Cost Mapping with type General Charge or Indirect
        gc_cm_lines = self.env['hr.payslip.cost.map'].sudo().search([
                                            ('payslip_run_id','=',self.id), 
                                            ('debit_amount','>',0),
                                            ('type','=','reclass'),
                                            '|',('plantation_location_type_id.general_charge','=',True), 
                                                ('plantation_location_type_id.indirect','=',True)])
        location_map = {} # temporery field to store mapping distribution, to prevent search on database for each line
        # {location_id: {blok_tanam: }}
        distributed_cm_to_add = []
        for cml in gc_cm_lines:
            # if 'Ilmi' not in cml.slip_id.employee_id.name :
            #     continue
            key = (cml.plantation_varieties_id.id, cml.plantation_location_id.id)
            if key not in location_map:
                block_tanams_non_tbm = []
                block_tanams_tbm = []
                afdeling_found = self.env['res.afdeling'].search([('location_id','=',cml.plantation_location_id.id)], limit=1)
                cost_center_found = self.env['account.cost.center'].search([('location_id','=',cml.plantation_location_id.id)], limit=1)
                indirect_found = self.env['plantation.indirect.cost'].search([('location_id','=',cml.plantation_location_id.id)], limit=1)
                if afdeling_found:
                    block_tanam_non_tbm = self.env['lhm.plant.block'].search([
                                                ('varieties_id','=',cml.plantation_varieties_id.id),
                                                ('afdeling_id','=',afdeling_found.id),
                                                ('planted','>',0),('status','!=','tbm')], order='status desc')
                    if block_tanam_non_tbm:
                        block_tanams_non_tbm.extend([x for x in block_tanam_non_tbm])
                    block_tanam_tbm = self.env['lhm.plant.block'].search([
                                                ('varieties_id','=',cml.plantation_varieties_id.id),
                                                ('afdeling_id','=',afdeling_found.id),
                                                ('planted','>',0),('status','=','tbm')], order='status desc')
                    if block_tanam_tbm:
                        block_tanams_tbm.extend([x for x in block_tanam_tbm])
                elif cost_center_found or indirect_found:
                    if cml.plantation_varieties_id:
                        domain = [('varieties_id','=',cml.plantation_varieties_id.id),('planted','>',0)]
                    else:
                        domain = [('varieties_id.name','=','Karet'),('planted','>',0)]
                    block_tanam_non_tbm = self.env['lhm.plant.block'].search(domain + [('status','!=','tbm')], order='status desc')
                    if block_tanam_non_tbm:
                        block_tanams_non_tbm.extend([x for x in block_tanam_non_tbm])
                    block_tanam_tbm = self.env['lhm.plant.block'].search(domain + [('status','=','tbm')], order='status desc')
                    if block_tanam_tbm:
                        block_tanams_tbm.extend([x for x in block_tanam_tbm])
                else:
                    if cml.plantation_varieties_id:
                        raise ValidationError(_(f"Tidak ditemukan Blok Tanam atas untuk ORG {cml.plantation_varieties_id.name} dari proses distribusi GC dengan kode {cost_center_found.code}"))
                    else:
                        raise ValidationError(_(f"Tidak ditemukan Blok Tanam atas dari proses distribusi GC dengan kode {cml.plantation_location_id.code}"))

                total_planted_tbm = sum([x.planted for x in block_tanams_tbm])
                total_planted_tm = sum([x.planted for x in block_tanams_non_tbm])
                block_tanams = block_tanams_non_tbm + block_tanams_tbm
                total_planted = total_planted_tbm + total_planted_tm
                projects = {}
                for block in block_tanams:
                    if block.is_project:
                        project_tanam = self.env['lhm.project'].search([('plant_block_id','=',block.id)], limit=1)
                        projects.update({block.id: project_tanam})
                location_map.update({key: {
                    'block_tanams': block_tanams,
                    'n_block': len(block_tanams),
                    'total_planted_is_available': True if total_planted else False,
                    'total_planted': total_planted,
                    'max_allocation_pct': (total_planted_tbm / total_planted) if total_planted else len(block_tanams_tbm),
                    'projects': projects,
                }})
            
            remaining_cost = cml.debit_amount * location_map[key]['max_allocation_pct']
            allocated_cost = 0.0
            n_block = location_map[key]['n_block']
            for block_tanam in location_map[key]['block_tanams']:
                n_block -= 1
                if block_tanam.is_project:
                    project_tanam = location_map[key]['projects'].get(block_tanam.id, False)
                    if not project_tanam:
                        continue
                    elif self.date_end > project_tanam.harvest_date_schedule:
                        # Brarti ini sudah lewat fase pre-harvest
                        continue
                elif block_tanam.status != 'tbm':
                    continue

                if not block_tanam.payroll_gc_dest_activity_id:
                    raise ValidationError(_(f"Block Tanam {block_tanam.code} belum dapat setting Payroll GC to Block Activity"))
                
                if location_map[key]['total_planted_is_available']:
                    pct_cost = block_tanam.planted / location_map[key]['total_planted']
                else:
                    pct_cost = 1 / location_map[key]['total_planted']
                if not n_block:
                    dr_amount = remaining_cost
                    remaining_cost -= dr_amount
                else:
                    dr_amount = round(pct_cost*cml.debit_amount, 0)
                    remaining_cost -= dr_amount
                    
                distributed_cm_to_add.append({
                    'payslip_line_id': cml.payslip_line_id.id,
                    'partner_id': cml.partner_id.id,
                    'plantation_varieties_id': cml.plantation_varieties_id.id,
                    # 'plantation_location_type_id': field_cost_type.id,
                    'plantation_location_type_id': block_tanam.location_type_id.id,
                    'plantation_location_id': block_tanam.location_id.id,
                    'plantation_activity_id': block_tanam.payroll_gc_dest_activity_id.id,
                    'account_id': block_tanam.payroll_gc_dest_activity_id.account_id.id,
                    'gc_distribution_debit_amount': dr_amount,
                    'slip_id': cml.payslip_line_id.slip_id.id,
                    'payslip_run_id': self.id,
                    'gc_distribution': True,
                    'type': 'reclass',
                })                
                cml.gc_distribution_credit_amount = cml.gc_distribution_credit_amount + dr_amount
                cml.gc_distributed = True
            
        if distributed_cm_to_add:
            self.env['hr.payslip.cost.map'].sudo().create(distributed_cm_to_add)
    
    def action_map_cost_reclass(self):
        super(HrPayslipRun, self).action_map_cost_reclass()
        for batch in self:
            batch.action_gae_distribution()