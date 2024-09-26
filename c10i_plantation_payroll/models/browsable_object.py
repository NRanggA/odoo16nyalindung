#-*- coding:utf-8 -*-
from odoo import fields
from odoo.addons.c10i_hr_payroll_pph.models.browsable_object import Payslips2

import logging
_logger = logging.getLogger(__name__)

class Payslips3(Payslips2):
    def compute_upah_harian_from_lhm(self):
        payslip = self.env['hr.payslip'].browse(self.id)
        return sum(payslip.lhm_line_ids.filtered(lambda l: not l.is_borong).mapped('contract_wage_value')) if payslip.lhm_line_ids else 0.0

    def compute_upah_borongan_from_lhm(self):
        payslip = self.env['hr.payslip'].browse(self.id)
        return sum(payslip.lhm_line_ids.filtered(lambda l: l.is_borong).mapped('contract_wage_value')) if payslip.lhm_line_ids else 0.0