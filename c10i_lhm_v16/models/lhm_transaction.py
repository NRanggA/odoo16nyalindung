# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import logging
import time
# import datetime
import calendar
from odoo.tools.translate import _
# from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons import decimal_precision as dp
from odoo import models, fields, tools, exceptions, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import base64
import xlrd
from datetime import datetime, timedelta, time
import pandas as pd
import numpy as np
import io

from decimal import Decimal, getcontext

_logger = logging.getLogger(__name__)


###################################################### Transaction LHM ######################################################
class lhm_transaction(models.Model):
    _name           = 'lhm.transaction'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _order          = "date desc, kemandoran_code asc"
    _description    = 'Transaksi Laporan Harian Mandor'

    @api.model
    def _get_state(self):
        doc_id  = self.env['res.doc.type'].search([('code', '=', 'lhm')], limit=1)
        if doc_id and doc_id.approval:
            state = [('draft', 'New'), ('in_progress', 'Progress'), ('confirmed', 'Confirmed'), ('done', 'Approved'), ('close', 'Close')]
        else:
            state = [('draft', 'New'), ('done', 'Progress'),('close', 'Close')]
        return state

    @api.depends('date','state')
    def _compute_account_period_id(self):
        for plantation_transaction in self:
            if plantation_transaction.date:
                period_id = self.env['account.period'].search([('date_start', '<=', plantation_transaction.date), ('date_stop', '>=', plantation_transaction.date), ('special','=',False)])
                if period_id:
                    plantation_transaction.account_period_id = period_id

    @api.depends('kemandoran_id','kemandoran_id.afdeling_id', 'kemandoran_id.division_id')
    def _compute_location(self):
        for loc in self:
            if loc.kemandoran_id.afdeling_id:
                loc.location = loc.kemandoran_id.afdeling_id.name
            elif loc.kemandoran_id.division_id:
                loc.location = loc.kemandoran_id.division_id.name
            else:
                loc.location = "NotDefined"

    @api.depends('user_id')
    def _compute_operating_unit_id(self):
        for plantation_transaction in self:
            if plantation_transaction.user_id:
                plantation_transaction.operating_unit_id = plantation_transaction.user_id.default_operating_unit_id

    def _default_doc_id(self):
        doc_id = self.env['res.doc.type'].search([('code', '=', 'lhm')])[-1]
        return doc_id and doc_id.id or False

    name                    = fields.Char("Nama", default="/")
    kemandoran_id           = fields.Many2one("hr.foreman", string="Kemandoran", ondelete="restrict", tracking=True)
    doc_type_id             = fields.Many2one("res.doc.type", string="Document Type", ondelete="restrict", tracking=True, default=_default_doc_id)
    approval                = fields.Boolean(string="Approval", related="doc_type_id.approval", readonly=True)
    date                    = fields.Date("Tanggal", tracking=True)
    kemandoran_code         = fields.Char("Kode Kemandoran", related="kemandoran_id.code", readonly=True)
    mandor_id               = fields.Many2one("hr.employee", string="Mandor", ondelete="restrict", related="kemandoran_id.foreman_id", readonly=True, store=True)
    asisten_mandor_id       = fields.Many2one("hr.employee", string="Mandor Besar", ondelete="restrict", related="kemandoran_id.foreman_id_1", readonly=True, store=True)
    kerani_id               = fields.Many2one("hr.employee", string="Kerani", ondelete="restrict", related="kemandoran_id.admin_id", readonly=True, store=True)
    location                = fields.Char("Afdeling/ Divisi", compute="_compute_location", readonly=True, store=True)
    nik_mandor              = fields.Char("NIK Mandor", related="kemandoran_id.nik_mandor", readonly=True)
    nik_mandor_1            = fields.Char("NIK Mandor Besar", related="kemandoran_id.nik_mandor_1", readonly=True)
    nik_kerani              = fields.Char("NIK Kerani", related="kemandoran_id.nik_kerani", readonly=True)
    lhm_line_ids            = fields.One2many('lhm.transaction.line', 'lhm_id', string="Detail LHM")
    lhm_nap_line_ids        = fields.One2many('lhm.transaction.nap.line', 'lhm_id', string="Detail LHM NAP")
    # lhm_contractor_line_ids = fields.One2many('lhm.contractor.line', 'lhm_id', string="Detail Buku Kontraktor")
    is_nap                  = fields.Boolean(string='Is NAP', compute='_compute_is_nap', store=True)
    is_borong               = fields.Boolean(string='Is Borong', compute='_compute_is_borong', store=True)
    is_hasil_2              = fields.Boolean(string='Is Hasil 2', compute='_compute_is_hasil_2', store=True)
    skb                     = fields.Boolean('Is SKB', compute="_compute_is_skb", store=True)
    process_line_ids        = fields.One2many('lhm.transaction.process.line', 'lhm_id', string="Detail Progress LHM")
    material_line_ids       = fields.One2many('lhm.transaction.material.line', 'lhm_id', string="Detail Material LHM")
    emp_out_ids             = fields.One2many('hr.employee.foreman.transfer', 'lhm_id', string="Detail Employee Transfer Out LHM", domain=[('type', '=', 'out')], readonly=1)
    emp_in_ids              = fields.One2many('hr.employee.foreman.transfer', 'lhm_id', string="Detail Employee Transfer In LHM", domain=[('type', '=', 'in')], readonly=1)
    user_id                 = fields.Many2one('res.users', string='Penanggung Jawab', index=True, tracking=True, default=lambda self: self.env.user)
    operating_unit_id       = fields.Many2one('operating.unit', string='Operating Unit', compute='_compute_operating_unit_id', readonly=True, store=True)
    account_period_id       = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", compute='_compute_account_period_id', readonly=True, store=True)
    date_start              = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop               = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    company_id              = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    note                    = fields.Text("Catatan")
    state                   = fields.Selection(selection=_get_state, string='Status',
                                    copy=False, default='draft', index=False, readonly=False, tracking=True,
                                    help="* New: Dokumen LHM baru.\n"
                                         "* Cancelled: LHM dibatalkan.\n"
                                         "* Progress: Proses Pengisian Progress.\n"
                                         "* Confirmed: LHM sudah diperiksa oleh Mandor.\n"
                                         "* Approved: LHM sudah disetujui oleh Asisten/Kepala Kebun. \n"
                                         "* Closed: LHM sudah diclosing. \n")
    invoice_id          = fields.Many2one('account.move', 'Payroll Invoice')
    pending_nab_link    = fields.Boolean('LHM belum sama dengan NAB', compute='_check_pending_nab_link', store=True)
    pending_nap_link    = fields.Boolean('LHM belum sama dengan NAP', compute='_check_pending_nap_link', store=True)
    sph_move_ids        = fields.One2many('sph.move', 'lhm_id', string='Sph Move')
    # validation_message   = fields.Text('Validation Message')

    nap_line_zero = fields.Boolean(
        string="Validasi Get Data Karet",
        compute="_compute_nap_line_zero",
        store=True
    )

    @api.depends('lhm_nap_line_ids.lhm_nap_line_id')
    def _compute_nap_line_zero(self):
        for record in self:
            record.nap_line_zero = any(
                not nap_line.lhm_nap_line_id for nap_line in record.lhm_nap_line_ids
            )

    @api.depends('lhm_line_ids.activity_id.is_panen')
    def _compute_is_nap(self):
        for record in self:
            record.is_nap = any(line.activity_id.is_nap for line in record.lhm_line_ids)
    
    @api.depends('lhm_line_ids.is_borong')
    def _compute_is_borong(self):
        for record in self:
            record.is_borong = any(line.is_borong for line in record.lhm_line_ids)

    @api.depends('lhm_line_ids.activity_id.is_panen')
    def _compute_is_hasil_2(self):
        for record in self:
            record.is_hasil_2 = any(line.activity_id.is_hasil_2 for line in record.lhm_line_ids)

    @api.depends('lhm_line_ids.activity_id.skb')
    def _compute_is_skb(self):
        for record in self:
            record.skb = any(line.activity_id.skb for line in record.lhm_line_ids)

    # Menggunakan contract_id Contract
    @api.onchange('date', 'kemandoran_id')
    def _onchange_kemandoran(self):
        other_ids = False
        if self.date and self.kemandoran_id:
            other_ids = self.env['lhm.transaction'].search([('id', '!=', self._origin.id), ('date', '=', self.date), ('kemandoran_id', '=', self.kemandoran_id.id)])
            if other_ids:
                self.date = False
                self.kemandoran_id = False
                return {
                    'value': {'lhm_line_ids': list(map(lambda x: (2, x), [x.id for x in self.lhm_line_ids]))},
                    'warning': {'title': _('Kesalahan Input Data'),
                                'message': _("Dokumen sudah ada: %s.") % other_ids[-1].name},
                }
        # Hapus semua data di `lhm_line_ids` sebelum menambahkan data baru
        self.lhm_line_ids = [(5, 0, 0)]
        
        if self.date and self.kemandoran_id and not other_ids:
            transfer_out_ids    = self.env['hr.employee.foreman.transfer'].search([('date', '=', self.date), ('type', '=', 'out'), ('kemandoran_to_id', '=', self.kemandoran_id.id), ('lhm_line_id', '=', False)])
            transfer_in_ids     = self.env['hr.employee.foreman.transfer'].search([('date', '=', self.date), ('type', '=', 'in'), ('kemandoran_from_id', '=', self.kemandoran_id.id), ('lhm_line_id', '=', False)])
            other_out_attn      = self.env['hr.attendance.type'].search([('type', '=', 'out')], limit=1)
            other_in_attn       = self.env['hr.attendance.type'].search([('type', '=', 'in')], limit=1)

            emp_out_ids = [x.employee_id.id for x in transfer_out_ids]
            list_employee = []
            seq = 1



            # Mencari Absensi karyawan berdasarkan tanggal yang sama di masukkan di form lhm
            start_date  = datetime.combine(self.date, datetime.min.time())
            end_date    = start_date + timedelta(days=1)

            # Pencarian absensi karyawan pada tanggal yang sama
            absensi = self.env['hr.attendance.sheet'].search([
                ('employee_id', 'in', self.kemandoran_id.employee_ids.ids),
                ('date', '=', self.date),
                ('check_in', '!=', False),
                ('check_out', '!=', False)
            ])
            absensi_employee_ids = absensi.mapped('employee_id.id')
            
            # absensi_kj = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)

            for employee in self.kemandoran_id.employee_ids:
                if employee.id in absensi_employee_ids:

                    # employee_absensi = absensi.filtered(lambda a: a.employee_id.id == employee.id)
                    # attendance = employee_absensi.filtered(lambda a: a.type_id == absensi_kj)

                    values = {
                        'sequence'              : seq,
                        'date'                  : self.date or False,
                        'work_day'              : 0.0,
                        'non_work_day'          : 0.0,
                        'total_hke'             : 0.0,
                        'total_hkne'            : 0.0,
                        'contract_value_date'   : 0.0,
                        'work_result'           : 0.0,
                        'premi'                 : 0.0,
                        'overtime_value'        : 0.0,
                        'penalty'               : 0.0,
                        'name'                  : employee and employee.no_induk or False,
                        'employee_id'           : employee and employee.id or False,
                        'attendance_id'         : False, 
                        # 'contract_id'           : contract and contract.id or False,
                        # 'contract_wage_value'   : contract.wage if contract.wage_type_id.name == 'Month' else contract.wage_day,
                        'contract_id'           : 0.0,
                        'contract_wage_value'   : 0.0,
                    }
                    if employee.id in emp_out_ids:
                        values.update({
                            'attendance_id': other_out_attn and other_out_attn.id or False,
                            'transfer_id': self.env['hr.employee.foreman.transfer'].search([
                                ('date', '=', self.date),
                                ('type', '=', 'out'),
                                ('kemandoran_to_id', '=', self.kemandoran_id.id),
                                ('lhm_line_id', '=', False),
                                ('employee_id', '=', employee.id)
                            ], limit=1).id or False
                        })
                    list_employee.append((0, 0, values))
                    seq += 1

            if transfer_in_ids:
                for transfer in transfer_in_ids:
                    values = {
                        'sequence'              : seq,
                        'date'                  : self.date or False,
                        'work_day'              : 0.0,
                        'non_work_day'          : 0.0,
                        'total_hke'             : 0.0,
                        'total_hkne'            : 0.0,
                        'contract_value_date'   : 0.0,
                        'work_result'           : 0.0,
                        'premi'                 : 0.0,
                        'overtime_value'        : 0.0,
                        'penalty'               : 0.0,
                        'name'                  : transfer and transfer.employee_id and transfer.employee_id.no_induk or False,
                        'employee_id'           : transfer and transfer.employee_id and transfer.employee_id.id or False,
                        # 'contract_id'           : contract and contract.id or False,
                        # 'contract_wage_value'   : contract.wage if contract.wage_type_id.name == 'Month' else contract.wage_day,
                        'contract_id'           : 0.0,
                        'contract_wage_value'   : 0.0,
                        'attendance_id'         : other_in_attn and other_in_attn.id or False,
                        'transfer_id'           : transfer and transfer.id or False
                    }
                    list_employee.append((0, 0, values))
                    seq += 1
            self.lhm_line_ids = list_employee

    # Menggunakan Contract_id
    def check_all(self, date_start, date_stop, employe_ids):
        plantation_line_obj = self.env['lhm.transaction.line'].sudo()
        for employee_id in employe_ids:
            total_hke           = 0
            # total_hke_2         = 0
            total_hke_day       = 0
            
            total_hkne          = 0
            total_hkne_day      = 0
            
            trans_valid             = []
            # trans_valid_borongan    = []
            lhm_list                = []
            all_transaction_employee    = plantation_line_obj.search([('lhm_id.date', '>=', date_start), ('lhm_id.date', '<=', date_stop), ('employee_id', '=', employee_id)], order='date asc')
            
            for emp_transaction in all_transaction_employee:
                # if not emp_transaction.is_borong:
                if emp_transaction.attendance_id and emp_transaction.employee_id.contract_id.wage_type_id.name == 'Month' and (emp_transaction.lhm_id.state == 'done' or emp_transaction.lhm_id.state == 'in_progress'):
                    trans_valid.append(emp_transaction.id)
                    if emp_transaction.lhm_id.id not in lhm_list:
                        lhm_list.append(emp_transaction.lhm_id.id)
                if emp_transaction.work_day > 0 and emp_transaction.attendance_id and emp_transaction.attendance_id.type_hk == 'hke' and (emp_transaction.lhm_id.state == 'done' or emp_transaction.lhm_id.state == 'in_progress'):
                    total_hke += emp_transaction.work_day
                elif emp_transaction.non_work_day > 0 and emp_transaction.attendance_id and emp_transaction.attendance_id.type_hk == 'hkne' and emp_transaction.employee_id.contract_id.wage_type_id.name == 'Month' and (emp_transaction.lhm_id.state == 'done' or emp_transaction.lhm_id.state == 'in_progress'):
                    total_hkne += emp_transaction.non_work_day
                # else:
                #     trans_valid_borongan.append(emp_transaction.id)
                #     total_hke_2 += emp_transaction.work_day

            # Looping untuk lhm transaksi yang bukan borongan 
            for emp_transaction_write in plantation_line_obj.search([('id', 'in', trans_valid)], order='date asc'):
                if emp_transaction_write.work_day > 0 and emp_transaction_write.attendance_id and emp_transaction_write.attendance_id.type_hk == 'hke' and (emp_transaction_write.lhm_id.state == 'done' or emp_transaction_write.lhm_id.state == 'in_progress'):
                    total_hke_day += emp_transaction_write.work_day
                elif emp_transaction_write.non_work_day > 0 and emp_transaction_write.attendance_id and emp_transaction_write.attendance_id.type_hk == 'hkne' and emp_transaction_write.employee_id.contract_id.wage_type_id.name == 'Month' and (emp_transaction_write.lhm_id.state == 'done' or emp_transaction_write.lhm_id.state == 'in_progress'):
                    total_hkne_day += emp_transaction_write.non_work_day
                if emp_transaction_write.attendance_id and (emp_transaction_write.non_work_day > 0 or emp_transaction_write.work_day > 0) and (emp_transaction_write.lhm_id.state == 'done' or emp_transaction_write.lhm_id.state == 'in_progress'):

                    contract_wage_value         = emp_transaction_write.contract_id.wage / (total_hke + total_hkne)
                    contract_value_date         = emp_transaction_write.contract_id.wage / (total_hke_day + total_hkne_day)
                    contract_value_hkne         = ((emp_transaction_write.contract_id.wage / (total_hke + total_hkne)) * total_hkne)

                    values  = {
                        # 'total_hke'             : total_hke_2 + total_hke,
                        'total_hke'             : total_hke,
                        'total_hkne'            : total_hkne,
                        'contract_wage_value'   : contract_wage_value,
                        'contract_value_date'   : contract_value_date,
                        'contract_value_hkne'   : contract_value_hkne,
                    }
                    emp_transaction_write.write(values)
                else:
                    
                    values = {
                        'total_hke'             : 0.0,
                        'total_hkne'            : 0.0,
                        'contract_wage_value'   : emp_transaction_write.contract_id.wage if emp_transaction_write.contract_id.wage_type_id.name == 'Month' else emp_transaction_write.contract_id.wage_day / emp_transaction_write.contract_id.work_day,
                        'contract_value_date'   : 0.0,
                    }
                    emp_transaction_write.write(values)
            
            # Looping untuk lhm transaksi yang borongan
            # for emp_transaction_borongan in plantation_line_obj.search([('id', 'in', trans_valid_borongan)], order='date asc'):
            #     if emp_transaction_borongan.work_day > 0 and emp_transaction_borongan.attendance_id and emp_transaction_borongan.attendance_id.type_hk == 'hke' and (emp_transaction_borongan.lhm_id.state == 'done' or emp_transaction_borongan.lhm_id.state == 'in_progress'):
            #         total_hke_day += emp_transaction_borongan.work_day
            #     elif emp_transaction_borongan.non_work_day > 0 and emp_transaction_borongan.attendance_id and emp_transaction_borongan.attendance_id.type_hk == 'hkne' and emp_transaction_borongan.employee_id.contract_id.wage_type_id.name == 'Month' and (emp_transaction_borongan.lhm_id.state == 'done' or emp_transaction_borongan.lhm_id.state == 'in_progress'):
            #         total_hkne_day += emp_transaction_borongan.non_work_day
            #     if emp_transaction_borongan.attendance_id and (emp_transaction_borongan.non_work_day > 0 or emp_transaction_borongan.work_day > 0) and (emp_transaction_borongan.lhm_id.state == 'done' or emp_transaction_borongan.lhm_id.state == 'in_progress'):
            #         values  = {
            #             'total_hke'             : total_hke_2 + total_hke,
            #         }
            #         emp_transaction_borongan.write(values)
            #     else:
            #         values = {
            #             'total_hke'             : 0.0,
            #         }
            #         emp_transaction_borongan.write(values)

            for lhm_reprogress in plantation_line_obj.search([('lhm_id', 'in', lhm_list)], order='date asc'):
                if (lhm_reprogress.lhm_id.state == 'done' or lhm_reprogress.lhm_id.state == 'in_progress'):
                    if lhm_reprogress.attendance_id and lhm_reprogress.employee_id and lhm_reprogress.employee_id.type_id and lhm_reprogress.employee_id.contract_id.wage_type_id.name == 'Month' and \
                        (lhm_reprogress.non_work_day > 0 or lhm_reprogress.work_day > 0):
                        self.env.cr.execute("""
                            SELECT 
                                ltl.activity_id,
                                ltl.location_id,
                                SUM(ltl.work_day) as hk,
                                SUM(ltl.work_day * ltl.contract_wage_value) + SUM(ltl.premi + ltl.overtime_value - ltl.penalty) as realisasi,
                                case when is_panen is TRUE then SUM(ltl.work_result) else 0 end as nilai,
                                SUM(ltl.premi + ltl.overtime_value - ltl.penalty) as premi,
                                SUM(ltl.non_work_day) as hkne,
                                SUM(ltl.contract_value_date) + SUM(ltl.work_day * ltl.contract_wage_value) + SUM(ltl.premi + ltl.overtime_value - ltl.penalty) - SUM(CASE WHEN ltl.contract_value_date > 0 THEN ltl.contract_wage_value ELSE 0 END) as realisasi_date
                            FROM 
                                lhm_transaction_line ltl
                            LEFT JOIN 
                                lhm_activity la on ltl.activity_id = la.id
                            WHERE 
                                ltl.activity_id is not NULL and lhm_id = %s 
                            GROUP BY 
                                ltl.activity_id, ltl.location_id, la.is_panen;
                            """, (lhm_reprogress.lhm_id.id,))
                        for progres in self.env.cr.fetchall():
                            progress_line   = self.env['lhm.transaction.process.line'].search([('activity_id', '=', progres[0]), ('location_id', '=', progres[1]), ('lhm_id', '=', lhm_reprogress.lhm_id.id)])
                            if progress_line:
                                new_lines = {
                                    'realization'       : progres[3],
                                    'realization_date'  : progres[7],
                                }
                                progress_line.write(new_lines)
        return True

    # Menggunakan Contract_id
    def run_progress(self):

        # Cek jika wizard sudah ditampilkan sebelumnya di context
        if not self.env.context.get('wizard_shown'):
            # Pengecekan employee sesuai kemandoran
            check_employee = self.check_employee_in_kemandoran()
            if check_employee:
                # Tambahkan context 'wizard_shown' untuk mencegah loop
                check_employee['context']['wizard_shown'] = True
                return check_employee
        
        # Panggil fungsi untuk mengecek hasil 1 dan 2
        self._check_employee_not_hasil_1_2()
        # fungsi untuk menambahkan employee panen ke dalam Nap
        self.lhm_line_ids.get_employee_panen_nap()
        # Panggil fungsi untuk mengambil gaji untuk setiap employee
        self.lhm_line_ids.get_wage_value_employee()
        # Fungsi mengambil gaji karyawan borongan rawat
        self.lhm_line_ids.get_wage_borong_rawat()
        # Fungsi mengambil gaji karyawan borongan panen
        self.lhm_line_ids.get_wage_borong_panen()
        # jelankan fungsi progress
        self._progress()
        # Panggil fungsi untuk mengambil material yang digunakan
        self.get_material()

    # Fungsi untuk mengecek employee sesuai kemandoran
    def check_employee_in_kemandoran(self):
        # Mengambil daftar employee yang sesuai dengan kemandoran
        allowed_employees = self.kemandoran_id.employee_ids 

        # Daftar employee_id pada lhm_line_ids yang tidak sesuai dengan kemandoran
        invalid_employees = self.lhm_line_ids.filtered(lambda line: line.employee_id not in allowed_employees)

        if invalid_employees:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'lhm.transaction.warning.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_message': "Beberapa karyawan di dalam LHM line tidak sesuai dengan Kemandoran yang dipilih.",
                    'default_invalid_employee_ids': [(6, 0, invalid_employees.mapped('employee_id').ids)]
                }
            }

    def _check_employee_not_hasil_1_2(self):
        # Cari semua baris yang tidak memiliki hasil_1 dan hasil_2
        lines_without_results = self.lhm_line_ids.filtered(lambda line: not line.hasil_1 and not line.hasil_2)

        if lines_without_results:
            # Buat daftar pesan error
            validation_message_list = [
                f"Karyawan '{line.employee_id.name}' tidak memiliki hasil 1 dan hasil 2. Silahkan hapus data terlebih dahulu dan perbaiki absensi nya jika employee tersebut tidak kerja."
                for line in lines_without_results
            ]

            # Gabungkan pesan error ke dalam satu string
            validation_message = '\n'.join(validation_message_list)

            # Raise ValidationError dengan pesan yang terstruktur
            raise ValidationError(_("Data gagal diproses dengan error berikut:\n%s") % validation_message)

        return True

    def _progress(self):
        lhm_progress_list = []
        lhm_removed_list = []
        sequence_number = 1
        progress_line_obj = self.env['lhm.transaction.process.line']

        if self.process_line_ids:
            for data in self.process_line_ids:
                lhm_progress_list.append(data.id)

        self.env.cr.execute("""
            SELECT 
                ltl.activity_id,
                ltl.location_id,
                ltl.product_id,
                ltl.product_id_2,
                SUM(ltl.work_day) AS hk,
                SUM(ltl.work_day * ltl.contract_wage_value) + SUM(ltl.premi + ltl.overtime_value - ltl.penalty) AS realisasi,
                SUM(ltl.hasil_1) AS nilai,
                CASE WHEN la.is_panen IS TRUE THEN SUM(ltl.hasil_2) ELSE 0 END AS nilai2,
                SUM(ltl.premi + ltl.overtime_value - ltl.penalty) AS premi,
                SUM(ltl.non_work_day) AS hkne,
                SUM(ltl.contract_value_date) + SUM(ltl.work_day * ltl.contract_wage_value) + SUM(ltl.premi + ltl.overtime_value - ltl.penalty) - SUM(CASE WHEN ltl.contract_value_date > 0 THEN ltl.contract_wage_value ELSE 0 END) AS realisasi_date,
                ltl.satuan_1,
                CASE WHEN la.is_panen IS TRUE THEN ltl.satuan_2 ELSE NULL END AS satuan_2
            FROM 
                lhm_transaction_line ltl
            LEFT JOIN 
                lhm_activity la ON ltl.activity_id = la.id
            WHERE 
                ltl.activity_id IS NOT NULL AND ltl.lhm_id = %s 
            GROUP BY 
                ltl.activity_id, ltl.location_id, ltl.product_id, ltl.product_id_2, la.is_panen, ltl.satuan_1, ltl.satuan_2;
        """, (self.id,))

        for progres in self.env.cr.fetchall():
            activity_data = self.env['lhm.activity'].search([('id', '=', progres[0])])

            if lhm_progress_list:
                progress_line = progress_line_obj.search([('activity_id', '=', progres[0]), ('location_id', '=', progres[1]), ('lhm_id', '=', self.id)])
                if progress_line and len(progress_line) > 1:
                    raise ValidationError(_("Terjadi kesalahan (T.T), Error Code %s. \n"
                                            "Hubungi administrator untuk informasi lebih lanjut!"))
                if progress_line and len(progress_line) == 1:
                    if progress_line.nilai != progres[6] and progress_line.activity_id:
                        progress_line.write({'nilai': progres[6], 'updated': True})
                    if progress_line.nilai2 != progres[7] and progress_line.activity_id.is_panen:
                        progress_line.write({'nilai2': progres[7], 'updated': True})
                    if progress_line.work_day != progres[4]:
                        progress_line.write({'work_day': progres[4], 'updated': True})
                    if progress_line.non_work_day != progres[9]:
                        progress_line.write({'non_work_day': progres[9]})
                    if progress_line.realization != progres[5]:
                        progress_line.write({'realization': progres[5], 'updated': True})
                    if progress_line.realization_date != progres[10]:
                        progress_line.write({'realization_date': progres[10]})
                    if progress_line.premi != progres[8]:
                        progress_line.write({'premi': progres[8], 'updated': True})
                    if progress_line.product_id.id != progres[2]:
                        progress_line.write({'product_id': progres[2]})
                    if progress_line.product_id_2.id != progres[3]:
                        progress_line.write({'product_id_2': progres[3]})
                    if progres[7] > 0:  # Jika ada hasil_2
                        if progress_line.uom_id.id != activity_data.uom_id.id:
                            progress_line.write({'uom_id': activity_data.uom_id.id})
                        if progress_line.uom2_id.id != activity_data.uom2_id.id:
                            progress_line.write({'uom2_id': activity_data.uom2_id.id})
                    else:  # Jika tidak ada hasil_2
                        if progress_line.uom_id.id != progres[11]:
                            # progress_line.write({'uom_id': progres[11]})
                            progress_line.write({'uom_id': activity_data.uom_id.id})
                        if progress_line.uom2_id.id != progres[12]:
                            progress_line.write({'uom2_id': progres[12]})
                    lhm_removed_list.append(progress_line.id)
                else:
                    new_lines = {
                        'sequence': sequence_number,
                        'date': self.date,
                        'activity_id': progres[0],
                        'location_id': progres[1],
                        'product_id': progres[2],
                        'product_id_2': progres[3],
                        'nilai': progres[6],
                        'uom_id': progres[11] if progres[11] else (activity_data.uom_id.id if activity_data else False),
                        'nilai2': progres[7],
                        'uom2_id': progres[12] if progres[12] else (activity_data.uom2_id.id if activity_data else False),
                        'work_day': progres[4],
                        'non_work_day': progres[9],
                        'realization': progres[5],
                        'realization_date': progres[10],
                        'premi': progres[8],
                        'lhm_id': self.id,
                    }
                    if new_lines:
                        self.env['lhm.transaction.process.line'].create(new_lines)
                        sequence_number += 1
            else:
                new_lines = {
                    'sequence': sequence_number,
                    'date': self.date,
                    'activity_id': progres[0],
                    'location_id': progres[1],
                    'product_id': progres[2],
                    'product_id_2': progres[3],
                    'nilai': progres[6],
                    'uom_id': progres[11] if progres[11] else (activity_data.uom_id.id if activity_data else False),
                    'nilai2': progres[7],
                    'uom2_id': progres[12] if progres[12] else (activity_data.uom2_id.id if activity_data else False),
                    'work_day': progres[4],
                    'non_work_day': progres[9],
                    'realization': progres[5],
                    'realization_date': progres[10],
                    'premi': progres[8],
                    'lhm_id': self.id,
                }
                if new_lines:
                    self.env['lhm.transaction.process.line'].create(new_lines)
                    sequence_number += 1

        if len(lhm_removed_list) != len(lhm_progress_list):
            to_remove_list = []
            if len(lhm_progress_list) > len(lhm_removed_list):
                to_remove_list = list(set(lhm_progress_list) ^ set(lhm_removed_list))
            for removed_progress in progress_line_obj.search([('id', 'in', to_remove_list)]):
                removed_progress.write({
                    'realization': 0.0,
                    'realization_date': 0.0,
                    'work_day': 0.0,
                    'premi': 0.0,
                    'deleted': True,
                })
        if False in [isinstance(x.attendance_id.id, bool) for x in self.lhm_line_ids]:
            date_str = self.date.strftime('%Y-%m-%d')
            self.name = self.kemandoran_id.code + "/" + datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            if self.doc_type_id.approval:
                self.state = 'in_progress'
            else:
                self.state = 'done'
        else:
            raise ValidationError(_("Minimal salah satu absensi di daftar karyawan harus terisi!"))
        for lhm_line in self.lhm_line_ids:
            if lhm_line.transfer_id:
                lhm_line.transfer_id.write({'name': self.name})

        employee_ids = []
        for line in self.lhm_line_ids:
            if line.attendance_id and line.employee_id and \
                    line.employee_id.contract_id and line.employee_id.contract_id.wage_type_id.name == "Month" and line.employee_id.id not in employee_ids \
                    and line.valid and (line.work_day > 0 or line.non_work_day > 0):
                employee_ids.append(line.employee_id.id)
        if employee_ids:
            self.check_all(self.account_period_id.date_start, self.account_period_id.date_stop, employee_ids)

    # Mengunakan contract_id
    def button_draft(self):
        for rec in self:
            # Validasi jika state NAP done tidak bisa di hapus
            for line in rec.lhm_nap_line_ids:
                if line.lhm_nap_line_id.lhm_nap_id.state == 'done':
                    raise ValidationError(_("Anda tidak dapat membatalkan dokumen ini karena status NAP sudah Done, silahkan cancel terlebih dahulu dokumen NAP yang bersangkutan!"))

            # Menghapus semua data pada NAP
            if rec.lhm_nap_line_ids:
                for line in rec.lhm_nap_line_ids:
                    line.unlink()
        
            if rec.state in ['close']:
                raise ValidationError(_("Anda tidak dapat membatalkan dokumen dalam status Close!"))
            else:
                rec.state      = 'draft'
                employee_ids    = []
                for material in rec.material_line_ids:
                    material.unlink()
                for line in rec.lhm_line_ids:
                    if line.attendance_id and line.employee_id and \
                            line.employee_id.contract_id and line.employee_id.contract_id.wage_type_id.name == "Month" and line.employee_id.id not in employee_ids \
                            and line.valid and (line.work_day > 0 or line.non_work_day > 0):
                        employee_ids.append(line.employee_id.id)
                if employee_ids != []:
                    rec.check_all(rec.account_period_id.date_start, rec.account_period_id.date_stop, employee_ids)

                for line in rec.lhm_line_ids:
                    if line.attendance_id and line.employee_id and \
                        line.employee_id.contract_id and line.employee_id.contract_id.wage_type_id.name == "Month" and line.employee_id and \
                        line.valid and (line.work_day > 0 or line.non_work_day > 0):
                        values = {
                            'total_hke'             : 0.0,
                            'total_hkne'            : 0.0,
                            'contract_wage_value'   : 0.0,
                            'contract_value_date'   : 0.0,
                            'contract_id'           : 0,
                        }
                        line.write(values)
                    else:
                        values = {
                            'total_hke'             : 0.0,
                            'total_hkne'            : 0.0,
                            'contract_wage_value'   : 0.0,
                            'contract_value_date'   : 0.0,
                            'contract_id'           : 0,
                        }
                        line.write(values)
                return True
            return True

    # Menggunakan Contract ID
    def recalculate_plantation(self):
        all_plantation_ids  = self.env['lhm.transaction'].search([('account_period_id', '=', self.account_period_id.id)])
        for plantation in all_plantation_ids:
            for line in plantation.lhm_line_ids:
                if line.attendance_id and line.employee_id and line.contract_id:
                    if line.attendance_id:
                        line.valid      = True
                    if line.overtime_hour and line.overtime_hour > 0:
                        holiday         = False
                        overtime_data   = self.env['hr.overtime'].search([('hours', '=', line.overtime_hour)], limit=1)
                        holiday_data    = self.env['hr.holidays.public.line'].search([('date', '=', line.date)])
                        if holiday_data:
                            holiday     = True
                        if overtime_data and line.employee_id.type_id and line.employee_id.type_id.overtime_calc:
                            if holiday and overtime_data and line.contract_id.wage != 0.00:
                                line.overtime_value = (line.contract_id.wage / 173) * overtime_data.holiday
                            elif not holiday and overtime_data and line.contract_id.wage != 0.00:
                                line.overtime_value = (line.contract_id.wage / 173) * overtime_data.normal_day
                            else:
                                line.overtime_value = 0
                        if overtime_data and line.employee_id.type_id and not line.employee_id.type_id.overtime_calc:
                            if holiday and overtime_data and line.contract_id.wage != 0.00:
                                line.overtime_value = (line.contract_id.wage / 25) * float(float(3) / float(20)) * overtime_data.holiday
                            elif not holiday and overtime_data and line.contract_id.wage != 0.00:
                                line.overtime_value = (line.contract_id.wage / 25) * float(float(3) / float(20)) * overtime_data.normal_day
                            else:
                                line.overtime_value = 0

    @api.depends('process_line_ids.nab_line_ids', 'process_line_ids.nab_afkir_line_ids')
    def _check_pending_nab_link(self):
        for lhm in self:
            check = True
            for line in lhm.process_line_ids:
                if line.activity_id.is_panen:
                    nab_nilai = sum([x.qty_nab for x in line.nab_line_ids if x.lhm_nab_id.state!='draft']) \
                            + sum([x.qty for x in line.nab_afkir_line_ids if x.lhm_nab_afkir_id.state!='draft'])
                    if nab_nilai>=line.nilai:
                        check = False
            lhm.pending_nab_link = check

    @api.depends('process_line_ids.nap_line_ids', 'process_line_ids.nap_afkir_line_ids')
    def _check_pending_nap_link(self):
        for lhm in self:
            check = True
            for line in lhm.process_line_ids:
                if line.activity_id.is_panen:
                    nap_nilai = sum([x.qty_nap for x in line.nap_line_ids if x.lhm_nap_id.state!='draft']) \
                            + sum([x.qty for x in line.nap_afkir_line_ids if x.lhm_nap_afkir_id.state!='draft'])
                    if nap_nilai>=line.nilai:
                        check = False
            lhm.pending_nap_link = check

    def get_material(self):
        move_obj            = self.env['stock.move']
        material_line_obj   = self.env['lhm.transaction.material.line']
        if self.material_line_ids:
            for material in self.material_line_ids:
                material.unlink()
        for progress in self.process_line_ids:
            if progress.activity_id and progress.location_id and progress.location_id.type_id.skb_declare == True:
                date_start  = datetime.combine(self.date.replace(day=1), time(0, 0, 0))
                lhm_date    = datetime.combine(self.date, time(23, 59, 59))
                domain = [
                    ('date', '>=', date_start), 
                    ('date', '<=', lhm_date), 
                    # ('skb', '=', True),
                    ('picking_type_id.code', '=', 'issue'), 
                    ('state', '=', 'done'), 
                    ('plantation_location_id', '=', progress.location_id.id), 
                    ('plantation_activity_id', '=', progress.activity_id.id), 
                    ('origin_returned_move_id', '=', False),
                    ('pending_material_allocation', '>', 0.0),
                    ]
                skb_ids     = move_obj.search(domain)

                for skb in skb_ids:
                    values_skb  = {
                        'name'              : skb.picking_id.bpb_number or '',
                        'date'              : self.date,
                        'product_id'        : skb.product_id.id,
                        'location_id'       : skb.plantation_location_id.id,
                        'activity_id'       : skb.plantation_activity_id.id,
                        'real_stock_qty'    : skb.product_uom_qty,
                        'stock_qty'         : skb.plantation_material_allocation,
                        'product_uom_id'    : skb.product_uom.id,
                        'move_id'           : skb.id,
                        'picking_id'        : skb.picking_id and skb.picking_id.id or False,
                        'lhm_id'            : self.id,
                        'progress_id'       : progress.id,
                    }
                    material_line_obj.create(values_skb)

    def reprogress_plantation(self):
        all_plantation_ids = self.env['lhm.transaction'].search([('state', 'in', ['in_progress','done']), ('account_period_id', '=', self.account_period_id.id)])
        for plantation in all_plantation_ids:
            plantation.run_progress()

    def button_confirm(self):
        for nap_line in self.lhm_nap_line_ids:
            # if (not nap_line.hasil_1_nap or nap_line.hasil_1_nap == 0 or nap_line.hasil_2_nap or nap_line.hasil_2_nap == 0) and nap_line.lhm_transaction_line_id.is_hasil_2:
            if nap_line.lhm_transaction_line_id.activity_id.is_hasil_2:
                if (not nap_line.hasil_1_nap or nap_line.hasil_1_nap == 0) and \
                    (not nap_line.hasil_2_nap or nap_line.hasil_2_nap == 0):
                    raise ValidationError(_(
                        'Nilai NAP belum terisi, silahkan melakukan proses Nota Angkut Panen!'
                    ))

        self.state = 'confirmed'

    def button_approve(self):
        # Kumpulkan nama karyawan yang tipe absensinya tidak sesuai
        mismatch_names = []

        for line in self.lhm_line_ids:
            # Cari sheet absensi yang sesuai untuk setiap karyawan
            attendance_sheet = self.env['hr.attendance.sheet'].search([
                ('employee_id', '=', line.employee_id.id),
                ('date', '=', self.date)
            ], limit=1)
            # Jika tidak ada catatan absensi yang ditemukan, lanjutkan ke karyawan berikutnya
            if not attendance_sheet:
                continue

            # Cek apakah kode tipe absensi tidak sesuai
            if line.attendance_id.code != attendance_sheet.type_id.code:
                mismatch_names.append(line.employee_id.name)

        # Jika ada ketidakcocokan, tampilkan pesan kesalahan dengan semua nama karyawan
        if mismatch_names:
            mismatch_names_str = ", ".join(mismatch_names)
            raise UserError(_("Tipe absensi pada form LHM tidak sama dengan yang di Attendance untuk karyawan: [%s]") % mismatch_names_str)
        else:
            self.state = 'done'

    def button_reject(self):
        self.state = 'in_progress'

    def unlink(self):
        for transaction in self:
            if transaction.state != 'draft':
                raise UserError(_('Status dokumen LHM nomor %s dengan kemandoran %s adalah %s.\n'
                                  'Laporan Harian Mandor hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (transaction.name, transaction.kemandoran_id.name, transaction.state.title()))
            if transaction.lhm_line_ids:
                unlink_transfer = self.env['hr.employee.foreman.transfer'].search([('date', '=', transaction.date), '|', ('lhm_id', '=', transaction.id), ('other_lhm_id', '=', transaction.id)])
                if not unlink_transfer:
                    return super(lhm_transaction, self).unlink()
                    pass
                for transfer in unlink_transfer:
                    if (transfer.lhm_id and transfer.lhm_id.id) == transaction.id:
                        transfer.unlink()
                    elif (transfer.other_lhm_id and transfer.other_lhm_id.id) == transaction.id:
                        if transfer.lhm_line_id and transfer.lhm_id:
                            if transfer.lhm_id:
                                if transfer.lhm_id.state not in ['draft', 'in_progress']:
                                    raise UserError(_('Status dokumen LHM nomor %s dengan kemandoran %s adalah %s.\n'
                                                      'Hubungi kemandoran terkait untuk menghapus Daftar Karyawan') %
                                                    (transfer.lhm_id.name, transfer.lhm_id.kemandoran_id.name, transfer.lhm_id.state.title()))
                                else:
                                    new_values = {
                                        'attendance_id'         : False,
                                        'satuan_id'             : False,
                                        'activity_id'           : False,
                                        'location_id'           : False,
                                        'location_type_id'      : False,
                                        'valid'                 : False,
                                        'work_day'              : 0.0,
                                        'non_work_day'          : 0.0,
                                        'total_hke'             : 0.0,
                                        'total_hkne'            : 0.0,
                                        'min_wage_value_date'   : 0.0,
                                        'work_result'           : 0.0,
                                        'premi'                 : 0.0,
                                        'overtime_hour'         : 0.0,
                                        'overtime_value'        : 0.0,
                                        'penalty'               : 0.0,
                                    }
                                    transfer.lhm_line_id.write(new_values)
                                    transfer.unlink()
                            else:
                                transfer.unlink()
                        else:
                            transfer.unlink()
                    else:
                        pass
        transaction = super(lhm_transaction, self).unlink()
        return transaction

    @api.model
    def create(self, values):
        kemandoran = self.env['hr.foreman'].search([('id', '=', values.get('kemandoran_id'))])
        date = values.get('date')
        if kemandoran:
            values['name'] = f"{kemandoran.code or ''}/{date}"
        else:
            values['name'] = f"{kemandoran.code or ''}/"

        return super(lhm_transaction, self).create(values)

    def write(self, values):
        for record in self:
            kemandoran_id = values.get('kemandoran_id')
            date          = values.get('date')

            if kemandoran_id or date:
                if kemandoran_id:
                    kemandoran = self.env['hr.foreman'].browse(kemandoran_id)
                else:
                    kemandoran = record.kemandoran_id
            else:
                kemandoran = record.kemandoran_id

            date = date or record.date
            values['name'] = f"{kemandoran.code or ''}/{date}"
        
        return super(lhm_transaction, self).write(values)

class lhm_transaction_line(models.Model):
    _name           = 'lhm.transaction.line'
    _description    = 'Detail Transaksi Laporan Harian Mandor'
    _order          = 'sequence'

    # @api.onchange("location_type_id", "location_id")
    # def _get_doc_activity_ids(self):
    #     for line in self:
    #         activity_list   = []
    #         doc_id          = self.env['res.doc.type'].search([('code','=','lhm')], limit=1)
    #         level_1         = self.env['lhm.activity'].search([('level','=',1)], limit=1)
    #         avail_act       = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])

    #         if doc_id:
    #             for act in avail_act:
    #                 if doc_id.id in act.doc_ids.ids:
    #                     activity_list.append(act.id)

    #         if level_1:
    #             activity_list.append(level_1.id)

    #         if (line.location_type_id and line.location_type_id.project) and line.location_id:
    #             project_ids = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
    #             project_act = []
    #             avail       = []
    #             if level_1:
    #                 avail.append(level_1.id)
    #             for project in project_ids:
    #                 project_act += [x.activity_id.id for x in project.line_ids]

    #             if project_act != []:
    #                 for act_project in project_act:
    #                     if act_project in activity_list:
    #                         avail.append(act_project)
    #             if avail:
    #                 line.doc_activity_ids = [(6, 0, avail)]
    #             else:
    #                 line.doc_activity_ids = [(6, 0, activity_list)]
    #         else:
    #             line.doc_activity_ids = [(6, 0, activity_list)]

    #         if not line.doc_activity_ids:
    #             line.doc_activity_ids = [(6, 0, [])]

    name                = fields.Char("NIK", related="employee_id.no_induk", readonly=True)
    date                = fields.Date("Date")
    sequence            = fields.Integer()
    work_day            = fields.Float("HK")
    non_work_day        = fields.Float("HKN")
    work_result         = fields.Float("Hasil")
    unit_price          = fields.Float("Tarif")
    premi               = fields.Float("Premi")
    overtime_hour       = fields.Integer("Jam Lembur")
    overtime_value      = fields.Float("Rupiah Lembur")
    penalty             = fields.Float("Penalty")
    kontanan            = fields.Boolean("Kontanan")
    valid               = fields.Boolean("Valid")
    total_hke           = fields.Float(string="Total HKE")
    total_hkne          = fields.Float(string="Total HKNE")
    # UMR 
    min_wage_value      = fields.Float(string="Upah Minimum")
    min_wage_value_date = fields.Float(string="Upah Tanggal")
    min_wage_value_hkne = fields.Float(string="Upah HKNE")
    # Contract
    contract_id         = fields.Many2one('hr.contract', string='Contract', ondelete="restrict")
    contract_wage_value = fields.Float(string="Upah")
    contract_value_date = fields.Float(string="Upah Tanggal Contract")
    contract_value_hkne = fields.Float(string="Upah HKNE Contract")
    # relasi
    employee_id         = fields.Many2one("hr.employee", string="Nama", ondelete="restrict")
    attendance_id       = fields.Many2one("hr.attendance.type", string="Absensi", ondelete="restrict")
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    no_line             = fields.Boolean(string="Mandatory", related="location_type_id.no_line")
    varieties_id        = fields.Many2one('plant.varieties', string="ORG", ondelete='restrict')
    varieties_validator = fields.Boolean(compute='_set_plantation_validator', store=True, string="Varieties Validator")
    @api.depends('location_type_id')
    def _set_plantation_validator(self):
        for line in self:
            validator = False
            if line.location_type_id:
                # Plantation, GC, IDC, PJ, NS => True (artinya wajib diisi)
                validator = line.location_type_id.code in ('FC','GC','IDC', 'PJ', 'NS')
            line.varieties_validator = validator
    filtered_locations  = fields.Many2many('lhm.location', 'lhm_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    satuan_id           = fields.Many2one("uom.uom", string="Satuan", ondelete="restrict")
    transfer_id         = fields.Many2one("hr.employee.foreman.transfer", string="Transfer")
    filtered_activities = fields.Many2many('lhm.activity', 'lhm_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    doc_activity_ids    = fields.Many2many('lhm.activity', store=True)
    progressive         = fields.Boolean("Progressive", related="employee_id.type_id.monthly_employee", readonly=True)
    panen               = fields.Boolean("Panen", related="activity_id.is_panen", readonly=True)
    overtime            = fields.Boolean("Overtime", related="employee_id.type_id.overtime_calc", readonly=True)
    attendance_type     = fields.Selection([('in', 'Masuk'), ('out', 'Keluar'), ('na', 'N/A'), ('kj', 'KJ')], string='Type', related="attendance_id.type", readonly=True)
    min_wage_id         = fields.Many2one("hr.minimum.wage", string="Upah Minimum", ondelete="restrict")
    lhm_nab_ids         = fields.One2many('lhm.transaction.line.nab.line', 'lhm_line_id', 'LHM Detail')
    lhm_nap_ids         = fields.One2many('lhm.transaction.line.nap.line', 'lhm_line_id', 'LHM Detail')
    lhm_id              = fields.Many2one("lhm.transaction", string="LHM", ondelete="cascade")
    state               = fields.Selection(related='lhm_id.state', string='Status', store=True)
    transaction_nap_line_ids = fields.One2many('lhm.transaction.nap.line', 'lhm_transaction_line_id', string="Transaction NAP Lines")
    # POC Nyalindung
    # Penyadap
    hasil_latex     = fields.Float('Hasil Latex (L)')
    drc_latex       = fields.Float('drc Latex (%)')
    hasil_lump      = fields.Float('Hasil Lump (kg)')
    drc_lump        = fields.Float('drc Lump (%)')
    target_panen    = fields.Float('Target Panen')

    product_id      = fields.Many2one('product.product', string="Product 1", ondelete="restrict")
    product_id_2    = fields.Many2one('product.product', string="Product 2", ondelete="restrict")
    hasil_1         = fields.Float(string="Hasil 1")
    satuan_1        = fields.Many2one('uom.uom', string='Satuan 1', ondelete="restrict")
    hasil_2         = fields.Float(string="Hasil 2")
    satuan_2        = fields.Many2one('uom.uom', string='Satuan 2', ondelete="restrict")
    is_hasil_2      = fields.Boolean("Is Hasil 2", default=False)
    is_borong       = fields.Boolean("Is Borong", default=False)
    is_panen        = fields.Boolean(related='activity_id.is_panen', readonly=True, store=True)
    
    state        = fields.Selection(related='lhm_id.state', readonly=True, store=True)

    # Report pada detail LHM
    hasil_1_nap = fields.Float(
        string="Hasil 1 NAP", 
        related='transaction_nap_line_ids.hasil_1_nap', 
        readonly=True
    )
    hasil_2_nap = fields.Float(
        string="Hasil 2 NAP", 
        related='transaction_nap_line_ids.hasil_2_nap', 
        readonly=True
    )
    hasil_convert_latex = fields.Float(
        string="Hasil Convert Latex", 
        related='transaction_nap_line_ids.hasil_convert_latex', 
        readonly=True
    )
    hasil_convert_lump = fields.Float(
        string="Hasil Convert Lump", 
        related='transaction_nap_line_ids.hasil_convert_lump', 
        readonly=True
    )


    @api.depends('varieties_id','location_type_id', 'lhm_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.lhm_id.state!='draft':
                line.filtered_locations = []
            else:
                if line.location_type_id.code in ('WS','VH','MA','GC','MC','LB'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'lhm_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.lhm_id.state!='draft':
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','lhm')], limit=1)
                if line.location_type_id and line.location_type_id.project and line.location_id:
                    projects = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
                    project_activity_ids = []
                    for project in projects:
                        # if doc_form:
                        #     project_activity_ids += [x.activity_id.id for x in project.line_ids if doc_form.id in x.doc_ids.ids]
                        # else:
                            project_activity_ids += [x.activity_id.id for x in project.line_ids]

                    if project_activity_ids:
                        line.filtered_activities = [(6, 0, project_activity_ids)]
                    else:
                        line.filtered_activities = []
                else:
                    if line.location_type_id.code in ('WS','VH','MA','NS','LB'):
                        activities = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])
                    else: # GC, IDC, PLANTATION
                        if line.varieties_id:
                            if line.location_type_id.general_charge:
                                activities = line.varieties_id.general_charges_activity_ids
                            elif line.location_type_id.indirect:
                                activities = line.varieties_id.indirect_cost_activity_ids
                            # Menambahkan tipe lokasi Mills 
                            elif line.location_type_id.mills:
                                activities = line.varieties_id.mill_costs_ids
                            else:
                                activities = line.varieties_id.harvest_activity_ids
                                activities |= line.varieties_id.upkeep_activity_ids
                        else:
                            # activities = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])
                            activities = []
                    if False: #doc_form:
                        act_ids = []
                        for act in activities:
                            if doc_form.id in act.doc_ids.ids:
                                act_ids.append(act.id)
                        line.filtered_activities = [(6, 0, act_ids)]
                    else:
                        line.filtered_activities = [(6, 0, activities.ids)] if activities else []

    # Fungsi untuk menghitung konversi latex dan lump
    # def compute_conversion(self, lhm_nap_line, is_hasil_2):
    def compute_conversion(self, lhm_nap_line):
        """
        Fungsi untuk menghitung konversi hasil latex dan lump.
        """
        convert_hasil_latex = 0
        convert_hasil_lump = 0

        # Menghitung konversi untuk hasil latex
        drc_latex           = lhm_nap_line.drc_latex_nap
        convert_hasil_latex = lhm_nap_line.hasil_1_nap * drc_latex / 100

        # Menghitung konversi untuk hasil lump
        drc_lump            = lhm_nap_line.drc_lump_nap
        convert_hasil_lump  = lhm_nap_line.hasil_2_nap * drc_lump / 100

        # if is_hasil_2:
        #     # Menghitung konversi untuk hasil latex
        #     drc_latex           = lhm_nap_line.drc_latex_nap
        #     convert_hasil_latex = lhm_nap_line.hasil_1_nap * drc_latex / 100

        #     # Menghitung konversi untuk hasil lump
        #     drc_lump            = lhm_nap_line.drc_lump_nap
        #     convert_hasil_lump  = lhm_nap_line.hasil_2_nap * drc_lump / 100
        # else:
        #     # Menghitung konversi untuk hasil latex
        #     drc_latex           = lhm_nap_line.drc_latex_nap
        #     convert_hasil_latex = lhm_nap_line.hasil_1_nap * drc_latex / 100
            
        lhm_nap_line.write({
            'hasil_convert_latex'   : convert_hasil_latex,
            'hasil_convert_lump'    : convert_hasil_lump
        })
        
        return convert_hasil_latex, convert_hasil_lump

    def get_wage_borong_panen(self):
        for record in self:
            if not record.activity_id.is_nap:
                continue

            # Panggil fungsi untuk mengecek apakah employee ini bulanan atau bukan
            record._check_employee_bulanan()
            lhm_nap_line = self.env['lhm.transaction.nap.line'].search([('lhm_transaction_line_id', '=', record.id)])
            
            # Hitung konversi menggunakan fungsi compute_conversion
            # convert_hasil_latex, convert_hasil_lump = record.compute_conversion(lhm_nap_line, record.is_hasil_2)
            convert_hasil_latex, convert_hasil_lump = record.compute_conversion(lhm_nap_line)

            if record.is_hasil_2:
                
                # Dapatkan harga borongan berdasarkan DRC
                price_1     = record.activity_id.get_price_borongan(drc=lhm_nap_line.drc_latex_nap, product=record.product_id)
                price_2     = record.activity_id.get_price_borongan(drc=lhm_nap_line.drc_lump_nap, product=record.product_id_2)
                
                # Menghitung hasil akhir
                hasil_latex = convert_hasil_latex * price_1
                hasil_lump  = convert_hasil_lump * price_2
                hasil       = hasil_latex + hasil_lump
            else:
                # Menghitung gaji menggunakan data dari get_price_borongan tanpa DRC
                price_1     = record.activity_id.get_price_borongan()
                hasil       = lhm_nap_line.hasil_1_nap * price_1

            # Hanya update nilai kontrak jika is_borong bernilai True
            if record.is_borong:
                record.write({'contract_wage_value': hasil})

    # fungsi untuk mendapatkan gaji employee yang borongan non panen (rawat)
    def get_wage_borong_rawat(self):
        for record in self:
            if record.is_borong:
                if not record.activity_id.is_nap:
                    # panggil fungsi untuk mengecek employee ini bulanan atau bukan
                    record._check_employee_bulanan()
                    
                    wage_hasil = record.hasil_1 * record.activity_id.get_price_borongan()
                    values = {
                        'contract_wage_value': wage_hasil
                    }
                    record.write(values)

    # Fungsi untuk mendapatkan gaji
    def get_wage_value_employee(self):
        for record in self:
            if not record.is_borong:
                contract             = False
                lhm_transaction_date = record.lhm_id.date if record.lhm_id else False
                
                if record.employee_id and record.employee_id.basic_salary_type == 'employee':
                    contract = self.env['hr.contract'].sudo().search([
                        ('employee_id', '=', record.employee_id.id),
                        ('date_start', '<=', lhm_transaction_date),
                        '|',('date_end', '=', False),('date_end', '>=', lhm_transaction_date),
                        ('state', '=', 'open'),
                        ('is_lhm', '=', True ),
                    ], limit=1)
                elif record.employee_id and record.employee_id.basic_salary_type == 'employee_type':
                    contract = self.env['hr.contract'].sudo().search([
                        ('employee_type_id', '=', record.employee_id.type_id.id),
                        ('date_start', '<=', lhm_transaction_date),
                        '|',('date_end', '=', False),('date_end', '>=', lhm_transaction_date),
                        # ('date_end', '>=', lhm_transaction_date),
                        ('state', '=', 'open'),
                        ('is_lhm', '=', True ),
                    ], limit=1)
                if not contract:
                    raise ValidationError(_(f"Contract pada Karyawan : { record.employee_id.name } dengan Tipe Karyawan : {record.employee_id.type_id.name}, tidak ditemukan !"))

                values = {
                    'contract_id'           : contract and contract.id or False,
                    'contract_wage_value'   : contract.wage if contract.wage_type_id.name == 'Month' else contract.wage_day,
                }
                record.write(values)

    # Fungsi untuk menambahkan employee ke dalam NAP jika panen
    def get_employee_panen_nap(self):
        for record in self:
            # Cek apakah aktivitas adalah panen
            if record.activity_id.is_nap:
                # Periksa apakah record untuk employee dan lhm_id serta lhm_transaction_line_id sudah ada
                existing_nap_line = self.env['lhm.transaction.nap.line'].search([
                    ('lhm_id', '=', record.lhm_id.id),
                    ('lhm_transaction_line_id', '=', record.id),
                    ('employee_id', '=', record.employee_id.id),
                ], limit=1)

                # Jika record belum ada, buat record baru
                if not existing_nap_line:
                    value = {
                        'lhm_id'                 : record.lhm_id.id,
                        'lhm_transaction_line_id': record.id,
                        'employee_id'            : record.employee_id.id,
                        'sequence'               : record.sequence,
                    }
                    # Buat record baru di lhm.transaction.nap.line
                    self.env['lhm.transaction.nap.line'].create(value)

    # Fungsi untuk mengecek jika borongan employee bulanan atau bukan
    def _check_employee_bulanan(self):
        employee_bulanan_names = [] 
        for record in self:
            if record.is_borong:
                if record.employee_id.contract_id.wage_type_id.name == 'Month':
                    employee_bulanan_names.append(record.employee_id.name)
        
        if employee_bulanan_names:
            employee_names_str = ', '.join(employee_bulanan_names)
            raise ValidationError(_(f'Untuk karyawan bulanan tidak bisa dihitung menggunakan borongan untuk employee:[ {employee_names_str} ]'))

    @api.onchange('is_hasil_2')
    def _onchange_is_hasil_2(self):
        if self.is_hasil_2:
            if self.lhm_id.name == '/':
                return {
                    'warning': {
                        'title': _('Peringatan'),
                        'message': _("Silahkan save terlebih dahulu sebelum memasukkan Nilai 1 dan Nilai 2 !")
                        },
                }

    # fungsi untuk membuka wizard
    def buka_wizard(self):
        context = {
            'default_transaction_line_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wizard Hasil LHM',
            'res_model': 'wizard.hasil.lhm',
            'view_mode': 'form',
            'view_id': self.env.ref('c10i_lhm_v16.view_wizard_hasil_lhm_form').id,
            'target': 'new',
            'context': context,
        }

    def tambah_hasil_2(self):
        if self.is_hasil_2:
            wizard_action = self.buka_wizard()
            return wizard_action

    # (TODO) akan di hapus, namun harus di cek terlebih dahulu impact nya akan kemana 
    @api.onchange('hasil_latex','drc_latex', 'hasil_lump', 'drc_lump')
    def onchange_hasil_karet(self):
        self.work_result = (self.hasil_latex * self.drc_latex / 100.0) + (self.hasil_lump * self.drc_lump / 100.0)

    @api.onchange('attendance_id')
    def _onchange_attendance_id(self):
        non_work_day    = 0
        if self.attendance_id and self.attendance_id.type_hk == 'hkne' and \
                (self.employee_id.type_id.monthly_employee or self.employee_id.type_id.sku_employee \
                or self.employee_id.type_id.contract_employee):
            non_work_day    = 1
        if self.attendance_id:
            self.location_type_id   = False
            self.location_id        = False
            self.activity_id        = False
            # self.satuan_id          = False
            self.work_day           = 0.0
            self.work_result        = 0.0
            self.premi              = 0.0
            self.overtime_hour      = 0.0
            self.overtime_value     = 0.0
            self.penalty            = 0.0
            self.valid              = True
            self.non_work_day       = non_work_day
        else:
            self.location_type_id   = False
            self.location_id        = False
            self.activity_id        = False
            # self.satuan_id          = False
            self.work_day           = 0.0
            self.work_result        = 0.0
            self.premi              = 0.0
            self.overtime_hour      = 0.0
            self.overtime_value     = 0.0
            self.penalty            = 0.0
            self.valid              = False
            self.non_work_day       = 0.0

    @api.onchange('location_type_id')
    def _onchange_location_type_id(self):
        if self.location_type_id:
            self.location_id    = False
            self.activity_id    = False
            # self.satuan_id      = False
            self.varieties_id = self.location_type_id.varieties_id.id

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.activity_id    = False
            # self.satuan_id      = False

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            self.satuan_1      = self.activity_id.uom_id and self.activity_id.uom_id.id or False
            self.satuan_2      = self.activity_id.uom2_id and self.activity_id.uom2_id.id or False
            if self.activity_id.is_panen:
                lokasi = self.env['lhm.plant.block'].search([('location_id','=',self.location_id.id)], limit=1)
                # self.target_panen = lokasi.target_panen_perhari if lokasi else 0.0

    # (TODO) Pengecekan Lebih lannjut terkait transfer employee
    def _check_transfer_employee(self):
        for transfer in self:
            transfer_data   = transfer.transfer_id
            if transfer_data:
                if not transfer_data.lhm_id and not transfer_data.lhm_line_id:
                    transfer_data.write({
                        'name'          : self.lhm_id.name or '',
                        'lhm_id'        : self.lhm_id and self.lhm_id.id or False,
                        'lhm_line_id'   : self.id or False,
                    })
                    if transfer_data.other_lhm_line_id:
                        other_line_data = self.browse(transfer_data.other_lhm_line_id.id).transfer_id
                        if not other_line_data.other_lhm_id and not other_line_data.other_lhm_line_id:
                            other_line_data.write({
                                'other_lhm_id'      : self.lhm_id and self.lhm_id.id or False,
                                'other_lhm_line_id' : self.id or False,
                            })
        return True

    def _check_work_day(self):
        for line in self:
            if line.attendance_id and line.attendance_id.special and line.attendance_id.type == 'kj':
                if not line.is_borong and line.work_day <= 0:
                    raise UserError(_('HK Wajib Diisi jika Is Borong tidak aktif !'))

    @api.model
    def create(self, values):
        line    = super(lhm_transaction_line, self).create(values)
        line._check_transfer_employee()
        line._check_work_day()
        return line

    def write(self, values):
        line    = super(lhm_transaction_line, self).write(values)
        self._check_work_day()
        return line

    # (TODO) Pengencekan lebih dalam menganai hapus daftar karyawan di LHM
    def unlink(self):
        for transaction_line in self:
            if transaction_line.transfer_id:
                unlink_transfer    = self.env['hr.employee.foreman.transfer'].search([('date', '=', self.date),'|',('lhm_line_id', '=', transaction_line.id),('other_lhm_line_id', '=', transaction_line.id)])
                for transfer in unlink_transfer:
                    if (transfer.lhm_line_id and transfer.lhm_line_id.id) == transaction_line.id:
                        transfer.unlink()
                    elif (transfer.other_lhm_line_id and transfer.other_lhm_line_id.id) == transaction_line.id:
                        if transfer.lhm_line_id and transfer.lhm_id:
                            if transfer.lhm_id:
                               if transfer.lhm_id.state not in ['draft','in_progress']:
                                   raise UserError(_('Status dokumen LHM nomor %s dengan kemandoran %s adalah %s.\n'
                                                     'Hubungi kemandoran terkait untuk menghapus Daftar Karyawan') %
                                                    (transfer.lhm_id.name, transfer.lhm_id.kemandoran_id.name, transfer.lhm_id.state.title()))
                               else:
                                   new_values = {
                                       'attendance_id'      : False,
                                       'satuan_id'          : False,
                                       'activity_id'        : False,
                                       'location_id'        : False,
                                       'location_type_id'   : False,
                                       'work_day'           : 0.0,
                                       'non_work_day'       : 0.0,
                                       'work_result'        : 0.0,
                                       'premi'              : 0.0,
                                       'overtime_hour'      : 0.0,
                                       'overtime_value'     : 0.0,
                                       'penalty'            : 0.0,
                                   }
                                   transfer.lhm_line_id.write(new_values)
                                   transfer.unlink()
                            else:
                                transfer.unlink()
                        else:
                            transfer.unlink()
                    else:
                        pass
        line = super(lhm_transaction_line, self).unlink()
        return line

    @api.onchange('overtime_hour')
    def _onchange_overtime_hour(self):
        if self.overtime_hour:
            holiday         = False
            overtime_data   = self.env['hr.overtime'].search([('hours','=',self.overtime_hour)], limit=1)
            holiday_data    = self.env['hr.holidays.public.line'].search([('date', '=', self.date)])
            if holiday_data:
                holiday = True
            if overtime_data and self.employee_id.type_id and self.employee_id.type_id.overtime_calc:
                if holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    self.overtime_value = (self.min_wage_id.umr_month / 173) * overtime_data.holiday
                elif not holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    self.overtime_value = (self.min_wage_id.umr_month / 173) * overtime_data.normal_day
                else:
                    self.overtime_value = 0
            if overtime_data and self.employee_id.type_id and not self.employee_id.type_id.overtime_calc:
                if holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    self.overtime_value = (self.min_wage_id.umr_month / 25) * float(float(3)/float(20)) * overtime_data.holiday
                elif not holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    self.overtime_value = (self.min_wage_id.umr_month / 25) * float(float(3)/float(20)) * overtime_data.normal_day
                else:
                    self.overtime_value = 0
        elif self.overtime_hour <= 0 :
            self.overtime_value = 0

    @api.onchange('work_day')
    def _onchange_work_day(self):
        if self.work_day:
            if self.attendance_id and self.attendance_id.type == 'na':
                self.work_day = 0
                return {
                    'warning': {'title': _('Kesalahan Input Data'),
                                'message': _("HK tidak boleh diisi jika Absensi: %s.") % self.attendance_id.code},
                }
            total_work_day  = 0
            if isinstance(self.id, int):
                domain = [
                    ('employee_id', '=', self.employee_id.id),
                    ('date', '=', self.date),
                    ('id', '!=', self.id)]
            else:
                domain = [
                    ('employee_id', '=', self.employee_id.id),
                    ('date', '=', self.date),
                    ('id', '!=', self._origin.id)]
            data_lhm_line   = self.search(domain)
            max_hk          = 1

            if not data_lhm_line:
                total_work_day  = 0
            else:
                for lhm_line in data_lhm_line:
                    total_work_day = total_work_day + lhm_line.work_day
            if (total_work_day + self.work_day) > max_hk:
                if (max_hk - total_work_day) < 0 and not data_lhm_line:
                    self.work_day = 1
                elif (max_hk - total_work_day) < 0 and data_lhm_line:
                    self.work_day = 0
                else:
                    self.work_day = max_hk - total_work_day
                return {
                        'warning': {'title': _('Kesalahan Input Data'), 'message': _("HK tidak boleh lebih dari: %s.") % max_hk },
                    }
    
    @api.constrains('employee_id', 'attendance_id')
    def _check_attendance_id(self):
        for record in self:
            record._check_attendance_one()

    def _check_attendance_one(self):
        if self.attendance_id and self.employee_id and self.attendance_id.type in ['out','in']:
            if isinstance(self.id, int):
                domain = [
                    ('employee_id', '=', self.employee_id.id),
                    ('attendance_id', '=', self.attendance_id.id),
                    ('date', '=', self.date),
                    ('id', '!=', self.id)]
            else:
                domain = [
                    ('employee_id', '=', self.employee_id.id),
                    ('attendance_id', '=', self.attendance_id.id),
                    ('date', '=', self.date),
                    ('id', '!=', self._origin.id)]
            lhm_line    = self.search(domain)
            if lhm_line:
                raise UserError(_('Anda tidak dapat membuat daftar karyawan dengan nama %s dan absensi %s karena terjadi duplikasi data!') % (self.employee_id.name, self.attendance_id.code))
        return True

class lhm_transaction_nap_line(models.Model):
    _name               = 'lhm.transaction.nap.line'
    _description        = 'LHM Transaksi NAP Line'


    lhm_id                  = fields.Many2one("lhm.transaction", string="LHM", ondelete="cascade")
    lhm_transaction_line_id = fields.Many2one('lhm.transaction.line', string="LHM Line", ondelete="cascade")
    lhm_nap_line_id         = fields.Many2one('lhm.nap.line', string="NAP Line", ondelete="cascade")
    sequence                = fields.Integer()
    employee_id             = fields.Many2one('hr.employee', string='Employee')
    name                    = fields.Char("NIK", related="employee_id.no_induk", readonly=True)
    product_id              = fields.Many2one('product.product', string="Product 1", ondelete="restrict")
    product_id_2            = fields.Many2one('product.product', string="Product 2", ondelete="restrict")
    hasil_1_nap             = fields.Float(string="Hasil NAP 1")
    satuan_1_nap            = fields.Many2one('uom.uom', string='Satuan NAP 1', ondelete="restrict")
    hasil_2_nap             = fields.Float(string="Hasil NAP 2")
    satuan_2_nap            = fields.Many2one('uom.uom', string='Satuan NAP 2', ondelete="restrict")
    drc_latex_nap           = fields.Float('drc Latex NAP (%)')
    drc_lump_nap            = fields.Float('drc Lump NAP (%)')
    
    hasil_convert_latex     = fields.Float(string="Hasil Convert Latex",  digits=(16, 2))
    hasil_convert_lump      = fields.Float(string="Hasil Convert Lump",  digits=(16, 2))

    # @api.onchange('block_id', 'tgl_panen')
    # def _onchange_block_tgl_panen(self):
    #     if self.block_id and self.tgl_panen:
    #         # Cari karyawan yang sesuai dari data NAP
    #         nap_lines = self.env['lhm.transaction.nap.line'].search([
    #             ('lhm_transaction_line_id.location_id', '=', self.block_id.location_id.id),
    #             ('lhm_transaction_line_id.lhm_id.date', '=', self.tgl_panen),
    #             ('lhm_transaction_line_id.activity_id.is_panen', '=', True),
    #         ])
    #         employee_ids = nap_lines.mapped('employee_id')
    #         return {'domain': {'employee_id': [('id', 'in', employee_ids.ids)]}}

class lhm_transaction_process_line(models.Model):
    _name           = 'lhm.transaction.process.line'
    _description    = 'LHM Transaction Process Line'

    sequence            = fields.Integer()
    name                = fields.Char(related='activity_id.name', store=True, readonly=True)
    date                = fields.Date("Tanggal", )
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    nilai               = fields.Float('Nilai 1')
    uom_id              = fields.Many2one("uom.uom", string="Satuan 1", ondelete="restrict")
    nilai2              = fields.Float('Nilai 2')
    uom2_id             = fields.Many2one("uom.uom", string="Satuan 2", ondelete="restrict")
    work_day            = fields.Float('HK')
    non_work_day        = fields.Float('HKN')
    premi               = fields.Float('Premi')
    realization         = fields.Float('Realisasi')
    realization_date    = fields.Float(string="Realisasi Tanggal")
    deleted             = fields.Boolean('D')
    updated             = fields.Boolean('U')
    lhm_id              = fields.Many2one("lhm.transaction", string="LHM", ondelete="cascade")
    nab_line_ids        = fields.Many2many('lhm.nab.line', 'lhm_process_nab_line_rel', 'progress_id', 'nab_line_id', 'Nab Ref')
    nab_afkir_line_ids  = fields.Many2many('lhm.nab.afkir.line', 'lhm_process_nab_afkir_line_rel', 'progress_id', 'nab_afkir_line_id', 'Nab Afkir Ref')
    nab_nilai           = fields.Float('Nilai NAB', compute='_compute_qty_nab', store=True)
    nap_line_ids        = fields.Many2many('lhm.nap.line', 'lhm_process_nap_line_rel', 'progress_id', 'nap_line_id', 'Nap Ref')
    nap_afkir_line_ids  = fields.Many2many('lhm.nap.afkir.line', 'lhm_process_nap_afkir_line_rel', 'progress_id', 'nap_afkir_line_id', 'Nap Afkir Ref')
    nap_nilai           = fields.Float('Nilai NAP', compute='_compute_qty_nap', store=True)

    product_id  = fields.Many2one('product.product', string="Product 1", ondelete="restrict")
    product_id_2 = fields.Many2one('product.product', string="Product 2", ondelete="restrict")

    @api.depends('nab_line_ids', 'nab_afkir_line_ids')
    def _compute_qty_nab(self):
        for line in self:
            if line.activity_id.is_panen:
                line.nab_nilai = sum([x.qty_nab for x in line.nab_line_ids if x.lhm_nab_id.state!='draft']) \
                        + sum([x.qty for x in line.nab_afkir_line_ids if x.lhm_nab_afkir_id.state!='draft'])

    @api.depends('nap_line_ids', 'nap_afkir_line_ids')
    def _compute_qty_nap(self):
        for line in self:
            if line.activity_id.is_panen:
                line.nap_nilai = sum([x.qty_nap for x in line.nap_line_ids if x.lhm_nap_id.state!='draft']) \
                        + sum([x.qty for x in line.nap_afkir_line_ids if x.lhm_nap_afkir_id.state!='draft'])

################################################## End Of Transaction LHM ###################################################