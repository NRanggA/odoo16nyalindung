# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime, time

class NyPremiPenyadap(models.Model):
    _name = 'ny.premi.penyadap'
    _description = 'Premi Penyadap'
    _order = 'date_to desc'

    @api.model
    def _default_other_input_type(self):
        return self.env.ref('ny_hr_payroll.oth_input_type_premi_penyadap').id or False

    other_input_type_id = fields.Many2one('hr.payslip.other.input.type', string='Other Input Type', default=_default_other_input_type, required=True)
    line_ids = fields.One2many('ny.premi.penyadap.line','ref_id')
    mandor_line_ids = fields.One2many('ny.premi.penyadap.mandor','ref_id')
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    batch_other_input_id = fields.Many2one('hr.payslip.batch.other.input', string='Batch Other Input')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirm')
    ], default='draft', string='Status')

    base_premi_rate_assisten = fields.Float("Basis Produksi Asisten")
    base_premi_rate_mandor = fields.Float("Basis Produksi Mandor")
    base_premi_rate_kepala_mandor = fields.Float("Basis Produksi Kepala mandor")
    base_premi_rate_tap_kontrol = fields.Float("Basis Produksi Tap Kontrol")
    surplus_premi_rate_assisten = fields.Float("Lebih Produksi Asisten")
    surplus_premi_rate_mandor = fields.Float("Lebih Produksi Mandor")
    surplus_premi_rate_kepala_mandor = fields.Float("Lebih Produksi Kepala Mandor")
    surplus_premi_rate_tap_kontrol = fields.Float("Lebih Produksi Tap Kontrol")

    # Field untuk import
    is_import       = fields.Boolean('Import Data', default=False)
    file            = fields.Binary('File', attachment=True)
    error_message   = fields.Text('Error Message')

    def import_data(self):
        def cell_to_string(cell_value):
            if cell_value and (isinstance(cell_value, (float, np.floating)) or isinstance(cell_value, (int, np.integer))):
                return str(int(cell_value)) if not np.isnan(cell_value) else ''
            else:
                return cell_value.strip()
        
        if self.is_import:
            if not self.file:
                raise UserError(_("Masukkan File Terlebih Dahulu"))
        
        data = base64.b64decode(self.file)
        excel_file = io.BytesIO(data)
        df = pd.read_excel(excel_file, header=0)
        
        to_update   = []
        error_message_list = []

        for index, row in df.iterrows():
            premi_produksi_line = self.env['ny.premi.penyadap.line'].search([('employee_id.no_induk', '=', cell_to_string(row.get('NIK', ''))), ('ref_id', '=', self.id)], limit=1)
            if not premi_produksi_line:
                error_message_list.append(f"Baris ke- {index + 2} karyawan dengan nip {row.get('NIK', '')}, tidak ditemukan pada line saat ini!")

            # Validasi nilai yang akan di import 
            grade = self.env['ny.premi.penyadap.grade'].search([('name', '=', row.get('NILAI', ''))], limit=1)
            if not grade:
                error_message_list.append(f"Baris ke- {index + 2} karyawan dengan nip {row.get('NIK', '')}, Nilai tidak ditemukan !")

            to_update.append((1, premi_produksi_line.id, {
                'grade_id' : grade.id,
            }))

        if error_message_list:
            error_message = '\n'.join(error_message_list)
            self.error_message = error_message
            raise ValidationError(_("Import data gagal dengan error berikut:\n%s") % error_message)

        self.line_ids = to_update
        return True



    def compute_base_production(self):
        self.line_ids.unlink()

        domain = [('lhm_id.state','=','done'), \
                  ('lhm_transaction_line_id.date','>=',self.date_from), \
                  ('lhm_transaction_line_id.date','<=',self.date_to), \
                  '|',('product_id.name','=','Lateks'),('product_id_2.name','=','Lump')]
        result = self.env['lhm.transaction.nap.line'].search(domain)
        to_create = []
        for employee in result.employee_id:
            karet_kering = sum(result.filtered(lambda n: n.employee_id.id==employee.id).mapped('hasil_convert_latex'))
            karet_kering += sum(result.filtered(lambda n: n.employee_id.id==employee.id).mapped('hasil_convert_lump'))

            # target = (HK total sebulan - ABSENSI yang tipenya L) * Target per orang
            day_from = datetime.combine(fields.Date.from_string(self.date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(self.date_to), time.max)
            base_hk = employee.with_context(leave_premi_sadap=True)._get_work_days_data(
                day_from,
                day_to,
                calendar=employee.contract_id.resource_calendar_id,
                compute_leaves=True,
            )
            base_libur = (self.date_to - self.date_from).days+1 - base_hk['days'] + 4
            att_domain = [('employee_id','=',employee.id),('date','>=',self.date_from),('date','<=',self.date_to)]
            # act_hk = self.env['hr.attendance.sheet'].search_count(att_domain + [('type_id.code','=','KJ')])
            act_libur = self.env['hr.attendance.sheet'].search_count(att_domain + [('type_id.code','=','L')])

            vals = {
                'employee_id': employee.id,
                'karet_kering_qty': karet_kering,
                'kemandoran_id': employee.kemandoran_id.id,
                # 'block_tanam_id': employee.kemandoran_id.blok_tanam_id.id,
                'block_tanam_id': employee.blok_tanam_id.id,
                # 'base_hk': base_hk['days'] - 4,
                'base_libur': base_libur,
                'base_total_days': (self.date_to - self.date_from).days+1,
                # 'act_hk': act_hk,
                'act_libur': act_libur,
                'act_total_days': (self.date_to - self.date_from).days+1,
                # 'target_qty': (31 - 5) * employee.kemandoran_id.block_tanam_id.production_daily_target,
            }
            to_create.append((0,0,vals))
        if to_create:
            self.line_ids = to_create
        return True

    def compute_mandor_production(self):
        self.mandor_line_ids.unlink()
        to_create = []
        kemandorans = self.env['hr.foreman'].search([('blok_tanam_id.varieties_id.name','=','Karet')])
        for kepala_mandor in kemandorans.kepala_mandor_id:
            domain = [('lhm_id.state','=','done'), \
                    ('lhm_transaction_line_id.date','>=',self.date_from), \
                    ('lhm_transaction_line_id.date','<=',self.date_to)]
            varieties = kemandorans.filtered(lambda x: x.kepala_mandor_id.id==kepala_mandor.id).mapped('blok_tanam_id.varieties_id')
            if len(varieties)>1:
                if len(varieties.harvest_activity_id)>1:
                    domain.append(('lhm_transaction_line_id.activity_id','in',varieties.harvest_activity_id.ids))
                else:
                    domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
            else:
                domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
            blok_tanams = kemandorans.filtered(lambda x: x.kepala_mandor_id.id==kepala_mandor.id).blok_tanam_id
            # locations = blok_tanams.location_id
            # if len(locations)==1:
            #     domain.append(('lhm_transaction_line_id.location_id','=',locations.id))
            # else:
            #     domain.append(('lhm_transaction_line_id.location_id','in',locations.ids))
            kemandoranx = kemandorans.filtered(lambda x: x.kepala_mandor_id.id==kepala_mandor.id)
            if len(kemandoranx)==1:
                domain.append(('lhm_id.kemandoran_id','=',kemandoranx.id))
            else:
                domain.append(('lhm_id.kemandoran_id','in',kemandoranx.ids))
            domain.extend(['|',('product_id.name','=','Lateks'),('product_id_2.name','=','Lump'),('lhm_transaction_line_id.is_borong','=',False)])
            lhm_found = self.env['lhm.transaction.nap.line'].search(domain)
            
            karet_kering = sum(lhm_found.mapped('hasil_convert_latex'))
            karet_kering += sum(lhm_found.mapped('hasil_convert_lump'))
            to_create.append((0,0,{
                'employee_id': kepala_mandor.id,
                'position': 'kepala_mandor',
                'kemandoran_id': False,
                'block_tanam_id': False,
                'total_karet_kering_qty': karet_kering,
                # 'target_qty': sum(blok_tanams.mapped('production_daily_target_mandor')),
                'target_qty': sum(kemandorans.filtered(lambda x: x.kepala_mandor_id.id==kepala_mandor.id).mapped('production_daily_target_mandor')),
            }))
        for tap_kontrol in kemandorans.tap_kontrol_id:
            domain = [('lhm_id.state','=','done'), \
                    ('lhm_transaction_line_id.date','>=',self.date_from), \
                    ('lhm_transaction_line_id.date','<=',self.date_to)]
            varieties = kemandorans.filtered(lambda x: x.tap_kontrol_id.id==tap_kontrol.id).mapped('blok_tanam_id.varieties_id')
            if len(varieties)>1:
                if len(varieties.harvest_activity_id)>1:
                    domain.append(('lhm_transaction_line_id.activity_id','in',varieties.harvest_activity_id.ids))
                else:
                    domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
            else:
                domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
            blok_tanams = kemandorans.filtered(lambda x: x.tap_kontrol_id.id==tap_kontrol.id).blok_tanam_id
            # locations = blok_tanams.location_id
            # if len(locations)==1:
            #     domain.append(('lhm_transaction_line_id.location_id','=',locations.id))
            # else:
            #     domain.append(('lhm_transaction_line_id.location_id','in',locations.ids))
            kemandoranx = kemandorans.filtered(lambda x: x.tap_kontrol_id.id==tap_kontrol.id)
            if len(kemandoranx)==1:
                domain.append(('lhm_id.kemandoran_id','=',kemandoranx.id))
            else:
                domain.append(('lhm_id.kemandoran_id','in',kemandoranx.ids))
            domain.extend(['|',('product_id.name','=','Lateks'),('product_id_2.name','=','Lump'),('lhm_transaction_line_id.is_borong','=',False)])
            lhm_found = self.env['lhm.transaction.nap.line'].search(domain)
            
            karet_kering = sum(lhm_found.mapped('hasil_convert_latex'))
            karet_kering += sum(lhm_found.mapped('hasil_convert_lump'))
            to_create.append((0,0,{
                'employee_id': tap_kontrol.id,
                'position': 'tap_kontrol',
                'kemandoran_id': False,
                'block_tanam_id': False,
                'total_karet_kering_qty': karet_kering,
                # 'target_qty': sum(blok_tanams.mapped('production_daily_target_mandor')),
                'target_qty': sum(kemandorans.filtered(lambda x: x.tap_kontrol_id.id==tap_kontrol.id).mapped('production_daily_target_mandor')),

            }))
        for mandor in kemandorans.mandor_id:
            domain = [('lhm_id.state','=','done'), \
                    ('lhm_transaction_line_id.date','>=',self.date_from), \
                    ('lhm_transaction_line_id.date','<=',self.date_to)]
            varieties = kemandorans.filtered(lambda x: x.mandor_id.id==mandor.id).mapped('blok_tanam_id.varieties_id')
            if len(varieties)>1:
                if len(varieties.harvest_activity_id)>1:
                    domain.append(('lhm_transaction_line_id.activity_id','in',varieties.harvest_activity_id.ids))
                else:
                    domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
            else:
                domain.append(('lhm_transaction_line_id.activity_id','=',varieties.harvest_activity_id.id))
            blok_tanams = kemandorans.filtered(lambda x: x.mandor_id.id==mandor.id).blok_tanam_id
            # locations = blok_tanams.location_id
            # if len(locations)==1:
            #     domain.append(('lhm_transaction_line_id.location_id','=',locations.id))
            # else:
            #     domain.append(('lhm_transaction_line_id.location_id','in',locations.ids))
            kemandoranx = kemandorans.filtered(lambda x: x.mandor_id.id==mandor.id)
            if len(kemandoranx)==1:
                domain.append(('lhm_id.kemandoran_id','=',kemandoranx.id))
            else:
                domain.append(('lhm_id.kemandoran_id','in',kemandoranx.ids))
            domain.extend(['|',('product_id.name','=','Lateks'),('product_id_2.name','=','Lump'),('lhm_transaction_line_id.is_borong','=',False)])
            lhm_found = self.env['lhm.transaction.nap.line'].search(domain)
            
            karet_kering = sum(lhm_found.mapped('hasil_convert_latex'))
            karet_kering += sum(lhm_found.mapped('hasil_convert_lump'))
            to_create.append((0,0,{
                'employee_id': mandor.id,
                'position': 'mandor',
                'kemandoran_id': False,
                'block_tanam_id': False,
                'total_karet_kering_qty': karet_kering,
                # 'target_qty': sum(blok_tanams.mapped('production_daily_target_mandor')),
                'target_qty': sum(kemandorans.filtered(lambda x: x.mandor_id.id==mandor.id).mapped('production_daily_target_mandor')),
            }))
        if to_create:
            self.mandor_line_ids = to_create
        return True

    def action_compute(self):
        self.compute_base_production()
        self.compute_mandor_production()
        return True

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
                if not line.other_input_id and line.premi_amount:
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
            
            for mline in rec.mandor_line_ids:
                if not mline.other_input_id and mline.premi_amount:
                    line_values = {
                        'batch_id': new_batch_oth_input.id,
                        'employee_id': mline.employee_id.id,
                        'amount': mline.premi_amount
                    }
                    new_oth_input_line = self.env['hr.payslip.other.input'].create(line_values)
                    line.write({
                        'other_input_id': new_oth_input_line.id
                    })
                else:
                    line.other_input_id.amount = mline.premi_amount

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
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.action_edit_production_target")
        action['domain'] = [('varieties_id.name','=','Karet')]
        return action

    def action_view_foreman(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.action_edit_production_target_foreman")
        # action['domain'] = [('blok_tanam_id','!=',False)]
        return action