# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _custom_gc_activity_mapping(self, config, values):
        values = super(HrPayslipLine, self)._custom_gc_activity_mapping(config, values)
        # if config.allocate_to_project:
        if config.is_general_charge and self.slip_id.employee_id.gae_to_location_ids:
            # if not self.slip_id.employee_id.gae_distribution_id and not self.slip_id.employee_id.gae_to_location_ids:
            #     raise ValidationError(_("Employee %s does not have GAE Distribution assigned.") % self.slip_id.employee_id.name)
            values.update({
                'plantation_varieties_id': False,
                'plantation_location_type_id': False,
                # harusnya sih 
                # 'account_id': config.default_debit_account_id.id or config.default_credit_account_id.id,
                # 'account_id': values.get['account_id'] or config.default_debit_account_id.id,
                'gae_to_location_ids': [(6, 0, self.slip_id.employee_id.gae_to_location_ids.ids)],
                'gae_to_location': True,
            })
        elif config.is_gea_rule:
            if not self.slip_id.employee_id.gae_distribution_id and not self.slip_id.employee_id.gae_to_location_ids:
                raise ValidationError(_("Employee %s does not have GAE Distribution assigned.") % self.slip_id.employee_id.name)
            values.update({
                'plantation_varieties_id': False,
                'plantation_location_type_id': False,
                'account_id': config.default_debit_account_id.id or config.default_credit_account_id.id,
                'gae_distribution_id': self.slip_id.employee_id.gae_distribution_id.id,
            })
        return values