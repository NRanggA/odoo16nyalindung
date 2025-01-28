# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class LhmTransactionLine(models.Model):
    _inherit = 'lhm.transaction.line'

    payslip_id = fields.Many2one('hr.payslip', string='Payslip', groups='c10i_hr_payroll.group_hr_payroll_user')

    def button_draft(self):
        for rec in self:
            if any([x.payslip_id and x.payslip_id.state=='done' for x in rec.line_ids]):
                raise ValidationError("Tidak dapat Set Draft karena Gaji sudah di proses")
            for line in rec.line_ids:
                if line.payslip_id:
                    line.payslip_id = False
        return super().button_draft()