# -*- coding: utf-8 -*-
from odoo import models, fields, Command, api, _
from odoo.exceptions import UserError, ValidationError

class HrPayslipBatchOtherInput(models.Model):
    _inherit = 'hr.payslip.batch.other.input'

    def action_set_draft(self):
        self.write({'state': 'draft'})