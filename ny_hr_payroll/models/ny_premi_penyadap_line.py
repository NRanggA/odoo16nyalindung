# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class NyPremiPenyadapLine(models.Model):
    _name = 'ny.premi.penyadap.line'
    _description = 'Premi Penyadap Line'

    ref_id = fields.Many2one('ny.premi.penyadap', string='Reference')
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='restrict', required=True)
    kemandoran_id = fields.Many2one('hr.foreman', string='Kemandoran')
    block_tanam_id = fields.Many2one('lhm.plant.block', string='Blok Tanam')

    # hari
    base_hk = fields.Float(compute='compute_days', store=True)
    base_libur = fields.Float()
    base_total_days = fields.Float()
    act_hk = fields.Float(compute='compute_days', store=True)
    act_libur = fields.Float()
    act_total_days = fields.Float()

    # base qty
    karet_kering_qty = fields.Float()
    # target_qty = fields.Float()
    target_qty = fields.Float(compute='compute_target', store=True)
    lebih_target_qty = fields.Float(compute='compute_qty', string='Lebih Target')
    
    # base rate
    grade_id = fields.Many2one('ny.premi.penyadap.grade', string='Nilai', store=True)
    rate = fields.Float('Rate')
    premi_amount = fields.Float(compute='compute_amount', string='Premi', store=True)

    other_input_id = fields.Many2one('hr.payslip.other.input', string='Other Input')

    # @api.depends('base_hk','base_libur','act_hk','act_libur')
    # def compute_days(self):
    #     for line in self:
    #         line.base_total_days = line.base_hk + line.base_libur
    #         line.act_total_days = line.act_hk + line.act_libur
    @api.depends('base_libur', 'act_libur', 'base_total_days', 'act_total_days')
    def compute_days(self):
        for line in self:
            line.base_hk = line.base_total_days - line.base_libur
            line.act_hk = line.act_total_days - line.act_libur

    @api.depends('block_tanam_id', 'act_libur', 'base_libur', 'base_total_days')
    def compute_target(self):
        for line in self:
            target = 0.0
            if line.block_tanam_id:
                target = line.block_tanam_id.production_daily_target
            # if line.act_libur:
            if line.act_libur > line.base_libur:
                line.target_qty = (line.base_total_days - line.base_libur) * target
            else:
                line.target_qty = (line.base_total_days - line.act_libur) * target
            # else:
            #     line.target_qty = (line.base_total_days - line.base_libur) * target

    
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
            if rec.ref_id.batch_other_input_id and rec.ref_id.batch_other_input_id.state!='draft':
                raise ValidationError(_("Cannot delete other input which is the state of its Batch are not in draft state"))
            if rec.other_input_id.payslip_id and rec.other_input_id.payslip_id.state!='draft':
                raise ValidationError(_("Cannot delete other input batch which is already linked with Payslip"))
        return super().unlink()

    def action_view_lhm(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.lhm_trans_nap_line_action")
        action['domain'] = [('lhm_id.state','=','done'), \
                  ('lhm_transaction_line_id.date','>=',self.ref_id.date_from), \
                  ('lhm_transaction_line_id.date','<=',self.ref_id.date_to), \
                  ('employee_id','=',self.employee_id.id), \
                  '|',('product_id.name','=','Lateks'),('product_id_2.name','=','Lump')]
        return action