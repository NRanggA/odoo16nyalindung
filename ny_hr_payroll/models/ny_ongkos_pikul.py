# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, time

class NyOngkosPikulLine(models.Model):
    _name = 'ny.ongkos.pikul.line'
    _description = 'Detail Ongkos Pikul'

    ref_id = fields.Many2one('ny.ongkos.pikul', string='Reference', ondelete='restrict')
    employee_id = fields.Many2one('hr.employee', requried=True, string='Employee', ondelete='restrict')
    plant_block_id = fields.Many2one('lhm.plant.block', 'Blok Tanam')
    qty = fields.Float('Karet Kering')
    rate = fields.Float('Harga')
    amount = fields.Float(compute='_compute_amount', store=True, string='Total')
    other_input_id = fields.Many2one('hr.payslip.other.input', string='Other Input')

    @api.depends('qty','rate')
    def _compute_amount(self):
        for line in self:
            line.amount = line.qty * line.rate

    def action_view_lhm(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.lhm_trans_nap_line_action")
        action['domain'] = [('lhm_id.state','=','done'), \
                  ('lhm_transaction_line_id.date','>=',self.ref_id.date_from), \
                  ('lhm_transaction_line_id.date','<=',self.ref_id.date_to), \
                  ('employee_id','=',self.employee_id.id), \
                  ('lhm_transaction_line_id.location_id','=',self.plant_block_id.location_id.id), \
                  '|',('product_id.name','=','Lateks'),('product_id_2.name','=','Lump')]
        return action

class NyOngkosPikul(models.Model):
    _name = 'ny.ongkos.pikul'
    _description = 'Ongkos Pikul'
    _order = 'date_to desc'

    @api.model
    def _default_other_input_type(self):
        return self.env.ref('ny_hr_payroll.oth_input_type_ongkos_pikul').id or False
    
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    rate = fields.Float('Harga Ongkos Pikul / kg')
    line_ids = fields.One2many('ny.ongkos.pikul.line','ref_id')
    other_input_type_id = fields.Many2one('hr.payslip.other.input.type', string='Other Input Type', default=_default_other_input_type, required=True)
    batch_other_input_id = fields.Many2one('hr.payslip.batch.other.input', string='Batch Other Input')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirm')
    ], default='draft', string='Status')

    @api.onchange('rate')
    def onchange_rate(self):
        self.line_ids.rate = self.rate
    
    def action_compute(self):
        for rec in self:
            rec.line_ids.unlink()
            plant_blocks = self.env['lhm.plant.block'].search([('with_ongkos_pikul','=',True)])
            to_create = []
            for block in plant_blocks:
                lhm_naps = self.env['lhm.transaction.nap.line'].search([('lhm_id.state','=','done'), \
                  ('lhm_transaction_line_id.date','>=',rec.date_from), \
                  ('lhm_transaction_line_id.date','<=',rec.date_to), \
                  ('lhm_transaction_line_id.location_id','=',block.location_id.id), \
                  '|',('product_id.name','=','Lateks'),('product_id_2.name','=','Lump')])
                for employee in lhm_naps.lhm_transaction_line_id.employee_id:
                    emp_naps = lhm_naps.filtered(lambda n: n.lhm_transaction_line_id.employee_id.id==employee.id)
                    vals = {
                        'employee_id': employee.id,
                        'plant_block_id': block.id,
                        'rate': rec.rate,
                        'qty': sum(emp_naps.mapped('hasil_convert_latex')) + sum(emp_naps.mapped('hasil_convert_lump')),
                    }
                    to_create.append((0,0,vals))
            if to_create:
                self.line_ids = to_create
    
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
                if not line.other_input_id and line.amount:
                    line_values = {
                        'batch_id': new_batch_oth_input.id,
                        'employee_id': line.employee_id.id,
                        'amount': line.amount
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

    def action_view_block(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.action_edit_block_with_ongkos_pikul")
        action['domain'] = [('varieties_id.name','=','Karet')]
        return action