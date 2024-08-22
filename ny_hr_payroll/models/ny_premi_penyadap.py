# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class NyPremiPenyadap(models.Model):
    _name = 'ny.premi.penyadap'
    _description = 'Premi Penyadap'
    _order = 'date_to desc'

    @api.model
    def _default_other_input_type(self):
        return self.env.ref('ny_hr_payroll.oth_input_type_premi_penyadap').id or False

    other_input_type_id = fields.Many2one('hr.payslip.other.input.type', string='Other Input Type', default=_default_other_input_type, required=True)
    line_ids = fields.One2many('ny.premi.penyadap.line','ref_id')
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    batch_other_input_id = fields.Many2one('hr.payslip.batch.other.input', string='Batch Other Input')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirm')
    ], default='draft', string='Status')

    def action_compute(self):
        # TODO: create ke hr.payslip.other.income
        pass
    
    def action_confirm(self):
        for rec in self:
            if not rec.batch_other_input_id:
                values = {
                    'name': f"{rec.other_input_type_id.name} Periode {rec.date_from.strftime('%d/%m/%Y')} s.d {rec.date_to.strftime('%d/%m/%Y')}",
                    'date': rec.date_to,
                    'type_id': rec.other_input_type_id.id,
                }
                new_batch_oth_input = self.env['hr.payslip.batch.other.input'].create(values)
            else:
                new_batch_oth_input = rec.batch_other_input_id
            
            for line in rec.line_ids:
                if not line.other_input_id:
                    line_values = {
                        'batch_id': new_batch_oth_input.id,
                        'employee_id': line.employee_id.id,
                        'amount': line.premi_amount
                    }
                    new_oth_input_line = self.env['hr.payslip.other.input'].create(line_values)
                    line.write({
                        'other_input_id': new_oth_input_line.id
                    })
                else:
                    line.other_input_id.amount = line.premi_amount

            rec.write({
                'batch_other_input_id': new_batch_oth_input.id,
                'state': 'confirm',
            })
            new_batch_oth_input.action_confirm()

    def unlink(self):
        for rec in self:
            if rec.batch_other_input_id.state!='draft':
                raise ValidationError(_("Cannot delete other input which is the state of its Batch are not in draft state"))
            if rec.payslip_id:
                raise ValidationError(_("Cannot delete other input batch which is already linked with Payslip"))
        return super().unlink()