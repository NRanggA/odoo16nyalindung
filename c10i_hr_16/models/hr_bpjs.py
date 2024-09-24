# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class EmployeeBPJS(models.Model):
    _name = "hr.bpjs"
    _description = "BPJS"
    _rec_name = 'type'

    type = fields.Selection([('bpjs_kesehatan', 'BPJS Kesehatan'), 
        ('bpjs_ketenagakerjaan', 'BPJS Ketenagakerjaan'),
        ('bpjs_tk_jkk', 'BPJS Jaminan Keselamatan Kerja'),
        ('bpjs_tk_jkm', 'BPJS Jaminan Kematian'),
        ('bpjs_tk_jht', 'BPJS Jaminan Hari Tua'),
        ('bpjs_tk_pensiun', 'BPJS Jaminan Pensiun')], string='Type', required=True)
    allowance_pct = fields.Float('% Tunjangan')
    deduction_pct = fields.Float('% Potongan')
    total_tuition = fields.Float(compute='_compute_total', string='Total Iuran %')
    plafond_salary = fields.Float('Plafond Salary', help="Maximum Salary that will be deducted for contribution of bpjs amount")
    active = fields.Boolean(default=True)

    def _compute_total(self):
        for bpjs in self:
            bpjs.total_tuition = bpjs.allowance_pct + bpjs.deduction_pct