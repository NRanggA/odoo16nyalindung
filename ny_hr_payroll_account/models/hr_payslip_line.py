# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _get_mapping_account(self, config):
        self.ensure_one()
        mappings = []
        if not config.is_map_from_lhm:
            dr_amount = cr_amount = 0.0
            if config.default_debit_account_id:
                dr_amount = self.total
            else:
                cr_amount = self.total
            mappings.append({
                'payslip_line_id': self.id,
                'partner_id': config.partner_id.id,
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'account_id': config.default_debit_account_id.id or config.default_credit_account_id.id,
                'debit_amount': dr_amount,
                'credit_amount': cr_amount,
                'slip_id': self.slip_id.id,
            })
        else:
            for lhm_line in self.slip_id.lhm_line_ids:
                dr_amount = cr_amount = 0.0
                dr_amount = lhm_line.contract_wage_value
                mappings.append({
                    'payslip_line_id': self.id,
                    'partner_id': config.partner_id.id,
                    'plantation_location_type_id': lhm_line.location_type_id.id,
                    'plantation_location_id': lhm_line.location_id.id,
                    'plantation_activity_id': lhm_line.activity_id.id,
                    'account_id': lhm_line.activity_id.account_id.id,
                    'debit_amount': dr_amount,
                    'credit_amount': cr_amount,
                    'slip_id': self.slip_id.id,
                })
        return mappings
    
    def _create_cost_map(self):
        vals_list = []
        for line in self:
            for config in line.salary_rule_id.config_account_ids:
                vals_list.extend(line._get_mapping_account(config))
        if vals_list:
            self.env['hr.payslip.cost.map'].create(vals_list)