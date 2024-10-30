# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class NyPremiPenyadapMandor(models.Model):
    _name = 'ny.premi.penyadap.mandor'
    _description = 'Premi Penyadap Mandor'

    ref_id = fields.Many2one('ny.premi.penyadap', string='Reference')
    kemandoran_id = fields.Many2one('hr.foreman', string='Kemandoran')
    position = fields.Char('Jabatan')
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='restrict', required=False)
    block_tanam_id = fields.Many2one('lhm.plant.block', string='Blok Tanam')

    # base qty
    total_karet_kering_qty = fields.Float("Total Produksi")
    target_qty = fields.Float("Target Produksi")
    karet_kering_qty = fields.Float(compute='compute_qty', string='Produksi Karet Kering')
    lebih_target_qty = fields.Float(compute='compute_qty', string='Lebih Target')
    
    # base rate
    base_rate = fields.Float(compute='compute_amount', store=True, string='Rate Basis')
    surplus_rate = fields.Float(compute='compute_amount', store=True, string='Rate Lebih')
    premi_produksi_amount = fields.Float(compute='compute_amount', string='Premi Basis', store=True)
    premi_lebih_target_amount = fields.Float(compute='compute_amount', string='Premi Lebih Basis', store=True)
    premi_amount = fields.Float(compute='compute_amount', string='Total Premi', store=True)

    other_input_id = fields.Many2one('hr.payslip.other.input', string='Other Input')

    @api.depends('base_hk','base_libur','act_hk','act_libur')
    def compute_days(self):
        for line in self:
            line.base_total_days = line.base_hk + line.base_libur
            line.act_total_days = line.act_hk + line.act_libur

    @api.depends('total_karet_kering_qty','target_qty')
    def compute_qty(self):
        for line in self:
            line.karet_kering_qty = line.total_karet_kering_qty if line.total_karet_kering_qty < line.target_qty else line.target_qty
            line.lebih_target_qty = line.total_karet_kering_qty - line.target_qty if line.total_karet_kering_qty > line.target_qty else 0.0

    @api.depends('lebih_target_qty',
                 'position',
                 'ref_id.base_premi_rate_assisten',
                 'ref_id.base_premi_rate_mandor',
                 'ref_id.base_premi_rate_kepala_mandor',
                 'ref_id.base_premi_rate_tap_kontrol',
                 'ref_id.surplus_premi_rate_assisten',
                 'ref_id.surplus_premi_rate_mandor',
                 'ref_id.surplus_premi_rate_kepala_mandor',
                 'ref_id.surplus_premi_rate_tap_kontrol',
                 )
    def compute_amount(self):
        for line in self:
            base_rate = surplus_rate = 0.0
            if line.position=='assisten':
                base_rate = line.ref_id.base_premi_rate_assisten
                surplus_rate = line.ref_id.surplus_premi_rate_assisten
            elif line.position=='mandor':
                base_rate = line.ref_id.base_premi_rate_mandor
                surplus_rate = line.ref_id.surplus_premi_rate_mandor
            elif line.position=='kepala_mandor':
                base_rate = line.ref_id.base_premi_rate_kepala_mandor
                surplus_rate = line.ref_id.surplus_premi_rate_kepala_mandor
            elif line.position=='tap_kontrol':
                base_rate = line.ref_id.base_premi_rate_tap_kontrol
                surplus_rate = line.ref_id.surplus_premi_rate_tap_kontrol
            line.base_rate = base_rate
            line.surplus_rate = surplus_rate
            line.premi_produksi_amount = line.karet_kering_qty * line.base_rate
            line.premi_lebih_target_amount = line.lebih_target_qty * line.surplus_rate
            line.premi_amount = line.premi_produksi_amount + line.premi_lebih_target_amount
    
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

    def action_view_foreman(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.action_edit_production_target_foreman")
        action['domain'] = [(f'{self.position}_id','=',self.employee_id.id)]
        return action

    def action_view_lhm(self):
        kemandorans = self.env['hr.foreman'].search([(f'{self.position}_id','=',self.employee_id.id)])
        domain = [('lhm_id.state','=','done'), \
                ('lhm_transaction_line_id.date','>=',self.ref_id.date_from), \
                ('lhm_transaction_line_id.date','<=',self.ref_id.date_to)]
        varieties = kemandorans.mapped('blok_tanam_id.varieties_id')
        if len(varieties)>1:
            if len(varieties.harvest_activity_id)>1:
                domain.append(('lhm_transaction_line_id.activity_id','in',varieties.harvest_activity_id.ids))
            else:
                domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
        else:
            domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
        blok_tanams = kemandorans.blok_tanam_id
        locations = blok_tanams.location_id
        if len(locations)==1:
            domain.append(('lhm_transaction_line_id.location_id','=',locations.id))
        else:
            domain.append(('lhm_transaction_line_id.location_id','in',locations.ids))
        domain.extend(['|',('product_id.name','=','Latex'),('product_id_2.name','=','Lump'),('lhm_transaction_line_id.is_borong','=',False)])
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.lhm_trans_nap_line_action")
        action['domain'] = domain
        return action