# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrPayslipOtherInput(models.Model):
    _name = 'hr.payslip.other.input'
    _description = 'Payroll Other Input'

    batch_id = fields.Many2one('hr.payslip.batch.other.input', string='Batch', ondelete='cascade')
    date = fields.Date(related='batch_id.date', store=True, string='Date')
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='restrict', required=True)
    type_id = fields.Many2one(related='batch_id.type_id', store=True, string='Type', ondelete='restrict')
    type_code = fields.Char(related='type_id.code', store=True, string='Code')
    amount = fields.Float()
    payslip_id = fields.Many2one('hr.payslip', string='Payslip')

    def unlink(self):
        for rec in self:
            if rec.batch_id.state!='draft':
                raise ValidationError(_("Cannot delete other input which is the state of its Batch are not in draft state"))
            if rec.payslip_id:
                raise ValidationError(_("Cannot delete other input batch which is already linked with Payslip"))
        return super().unlink()