# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _get_mapping_account(self, config):
        if not self.total:
            return []
        self.ensure_one()
        mappings = []
        gc_default_location_result = self.slip_id.employee_id.get_default_location_activity_payroll()
        if not config.is_map_from_lhm:
            dr_amount = cr_amount = 0.0
            if config.default_debit_account_id or config.is_general_charge:
                dr_amount = self.total
            else:
                cr_amount = self.total
            vals1 = {
                'payslip_line_id': self.id,
                'partner_id': config.partner_id.id,
                'plantation_varieties_id': gc_default_location_result.get('plantation_varieties_id', False) if config.is_general_charge else False,
                'plantation_location_type_id': gc_default_location_result.get('plantation_location_type_id', False) if config.is_general_charge else False,
                'plantation_location_id': gc_default_location_result.get('plantation_location_id', False) if config.is_general_charge else False,
                'plantation_activity_id': gc_default_location_result.get('plantation_activity_id', False) if config.is_general_charge else False,
                'account_id': gc_default_location_result.get('plantation_account_id', False) if config.is_general_charge else (config.default_debit_account_id.id or config.default_credit_account_id.id),
                'debit_amount': dr_amount,
                'credit_amount': cr_amount,
                'slip_id': self.slip_id.id,
                'payslip_run_id': self.slip_id.payslip_run_id.id,
            }
            if config.is_general_charge and config.is_bpjs_tk:
                vals1.update({
                    'plantation_activity_id': gc_default_location_result.get('plantation_activity_bpjs_tk_id', False),
                    'account_id': gc_default_location_result.get('plantation_account_bpjs_tk_id', False),
                })
            elif config.is_general_charge and config.is_bpjs_kes:
                vals1.update({
                    'plantation_activity_id': gc_default_location_result.get('plantation_activity_bpjs_kes_id', False),
                    'account_id': gc_default_location_result.get('plantation_account_bpjs_kes_id', False),
                })
            if config.is_general_charge and not vals1['account_id']:
                raise ValidationError(f"Karyawan {self.slip_id.employee_id.name} belum memiliki Setting GC (Aktifitas dan Akun). Silahkan di seting terlebih dahulu di Kemandoran {self.slip_id.employee_id.kemandoran_id.name} atau Karyawan")
            mappings.append(vals1)
        else:
            lhm_lines = []
            if config.lhm_type=='upah_borong':
                lhm_lines = self.slip_id.lhm_line_ids.filtered(lambda l: l.is_borong)
            elif config.lhm_type=='gaji':
                lhm_lines = self.slip_id.lhm_line_ids.filtered(lambda l: not l.is_borong)
            
            for lhm_line in lhm_lines:
                dr_amount = cr_amount = 0.0
                dr_amount = lhm_line.contract_wage_value
                mappings.append({
                    'payslip_line_id': self.id,
                    'partner_id': config.partner_id.id,
                    'plantation_varieties_id': lhm_line.varieties_id.id,
                    'plantation_location_type_id': lhm_line.location_type_id.id,
                    'plantation_location_id': lhm_line.location_id.id,
                    'plantation_activity_id': lhm_line.activity_id.id,
                    'account_id': lhm_line.activity_id.account_id.id,
                    'debit_amount': dr_amount,
                    'credit_amount': cr_amount,
                    'slip_id': self.slip_id.id,
                    'payslip_run_id': self.slip_id.payslip_run_id.id,
                    'lhm_line_id': lhm_line.id,
                })
        return mappings
    
    def _create_cost_map(self):
        vals_list = []
        for line in self:
            for config in line.salary_rule_id.config_account_ids:
                vals_list.extend(line._get_mapping_account(config))
        if vals_list:
            self.env['hr.payslip.cost.map'].create(vals_list)