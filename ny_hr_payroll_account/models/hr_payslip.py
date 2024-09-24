# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    cost_map_ids = fields.One2many('hr.payslip.cost.map', 'slip_id', string='Cost Mapping')

    def action_map_cost(self):
        for slip in self:
            if slip.cost_map_ids:
                slip.cost_map_ids.unlink()
            slip.line_ids._create_cost_map()