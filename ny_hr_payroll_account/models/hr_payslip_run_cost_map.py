# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrPayslipRunCostMap(models.Model):
    _name = 'hr.payslip.cost.map'
    _description = 'Cost Mapping on Batch Payslip'
    _order = 'slip_id desc, id asc'
    
    payslip_line_id = fields.Many2one('hr.payslip.line', string='Payslip Line', ondelete='cascade')
    rule_id = fields.Many2one(related='payslip_line_id.salary_rule_id', store=True, string='Salary Rule')
    partner_id = fields.Many2one('res.partner', string='Partner')
    account_id = fields.Many2one('account.account', string='Account')
    debit_amount = fields.Float('Amount Debit')
    credit_amount = fields.Float('Amount Credit')

    slip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')
    payslip_run_id = fields.Many2one(related='slip_id.payslip_run_id', string='Payslip Batches', store=True, copy=False)

    plantation_location_type_id = fields.Many2one("lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")