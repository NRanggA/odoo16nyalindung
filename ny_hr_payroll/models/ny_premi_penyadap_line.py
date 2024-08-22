# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class NyPremiPenyadapLine(models.Model):
    _name = 'ny.premi.penyadap.line'
    _description = 'Premi Penyadap Line'

    ref_id = fields.Many2one('ny.premi.penyadap', string='Reference')
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='restrict', required=True)
    karet_kering_qty = fields.Float()
    target_qty = fields.Float()
    lebih_target_qty = fields.Float(compute='compute_qty', string='Lebih Target')
    grade_id = fields.Many2one('ny.premi.penyadap.grade', string='Nilai', store=True)
    rate = fields.Float('Rate')
    premi_amount = fields.Float(compute='compute_amount', string='Premi', store=True)

    other_input_id = fields.Many2one('hr.payslip.other.input', string='Other Input')


    @api.depends('karet_kering_qty','target_qty')
    def compute_qty(self):
        for line in self:
            line.lebih_target_qty = line.karet_kering_qty - line.target_qty if line.karet_kering_qty > line.target_qty else 0.0

    @api.depends('lebih_target_qty','rate')
    def compute_amount(self):
        for line in self:
            line.premi_amount = line.lebih_target_qty * line.rate
    
    @api.onchange('grade_id')
    def onchange_grade(self):
        self.rate = self.grade_id.rate
    
    def unlink(self):
        for rec in self:
            if rec.ref_id.batch_other_input_id.state!='draft':
                raise ValidationError(_("Cannot delete other input which is the state of its Batch are not in draft state"))
            if rec.other_input_id.payslip_id and rec.other_input_id.payslip_id.state!='draft':
                raise ValidationError(_("Cannot delete other input batch which is already linked with Payslip"))
        return super().unlink()