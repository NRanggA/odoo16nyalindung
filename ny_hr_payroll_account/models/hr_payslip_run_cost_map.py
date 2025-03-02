# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrPayslipRunCostMap(models.Model):
    _name = 'hr.payslip.cost.map'
    _description = 'Cost Mapping on Batch Payslip'
    _order = 'slip_id desc, id asc'
    
    payslip_line_id = fields.Many2one('hr.payslip.line', string='Payslip Line', ondelete='cascade', groups="c10i_hr_payroll.group_hr_payroll_user")
    rule_id = fields.Many2one(related='payslip_line_id.salary_rule_id', store=True, string='Salary Rule')
    partner_id = fields.Many2one('res.partner', string='Partner')
    account_id = fields.Many2one('account.account', string='Account')
    debit_amount = fields.Float('Amount Debit')
    credit_amount = fields.Float('Amount Credit')

    slip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=False, ondelete='cascade', groups="c10i_hr_payroll.group_hr_payroll_user")
    # payslip_run_id = fields.Many2one(related='slip_id.payslip_run_id', string='Payslip Batches', store=True, copy=False)
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches')

    plantation_varieties_id = fields.Many2one("plant.varieties", string="ORG", ondelete="restrict")
    plantation_location_type_id = fields.Many2one("lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")

    lhm_type = fields.Selection([('gaji', 'Gaji Harian'),('upah_borong', 'Upah Borongan')], string='LHM Type')
    gc_distributed = fields.Boolean(default=False)
    gc_distribution = fields.Boolean(default=False)
    gc_distribution_debit_amount = fields.Float('GC Distribution Amount Debit')
    gc_distribution_credit_amount = fields.Float('GC Distribution Amount Credit')
    type = fields.Selection([('bill', 'for Vendor Bill'),('reclass', 'For Reclass Journal')], string='Type')
