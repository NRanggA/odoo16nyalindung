# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrContract(models.Model):
    _inherit = 'hr.contract'

    base_amount_bpjs_kes = fields.Float('Dasar Pengali BPJS Kesehatan')
    base_amount_bpjs_tk = fields.Float('Dasar Pengali BPJS Jamsostek')

    allw_transportation = fields.Float("Tunj. Transport")
    allw_communication = fields.Float("Tunj. Komunikasi")

    # contract_id = fields.Many2one('hr.contract', string="Contract")
    employee_ids = fields.One2many('hr.employee', 'contract_id', string="Employees")
    employee_count = fields.Integer(string="Employee Count", compute='_compute_employee_count')
    
    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for contract in self:
            contract.employee_count = len(contract.employee_ids)

    def action_open_employees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employees',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee',
            'domain': [('id', 'in', self.employee_ids.ids)],
            'context': self.env.context,
        }