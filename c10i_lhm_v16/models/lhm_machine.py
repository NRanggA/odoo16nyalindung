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

BULAN_INDONESIA = [('1', 'Januari'),
                   ('2', 'Februari'),
                   ('3', 'Maret'),
                   ('4', 'April'),
                   ('5', 'Mei'),
                   ('6', 'Juni'),
                   ('7', 'Juli'),
                   ('8', 'Agustus'),
                   ('9', 'September'),
                   ('10', 'Oktober'),
                   ('11', 'November'),
                   ('12', 'Desember')]
# TAHUN           = [(num, str(num)) for num in range((datetime.datetime.now().year) - 30, (datetime.datetime.now().year) + 1)]

TAHUN = [(num, str(num)) for num in range(datetime.now().year - 30, datetime.now().year + 1)]



################################################## Transaction Buku Mesin ###################################################
class lhm_machine(models.Model):
    _name           = 'lhm.machine'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = 'Buku Mesin'

    def _default_account_period_id(self):
        date = datetime.today().strftime('%Y-%m-%d')
        period_id   = self.env['account.period'].search([('date_start', '<=', date),
                                                        ('date_stop', '>=', date),
                                                        ('special', '=', False)])
        period = False
        if period_id and len(period_id) > 1:
            period  = period_id[-1]
        elif period_id and len(period_id) == 1:
            period  = period_id
        return period and period.id or False

    @api.depends('user_id')
    def _compute_operating_unit_id(self):
        for plantation_transaction in self:
            if plantation_transaction.user_id:
                plantation_transaction.operating_unit_id = plantation_transaction.user_id.default_operating_unit_id

    def _default_doc_id(self):
        doc_id = self.env['res.doc.type'].search([('code', '=', 'bm')])[-1]
        return doc_id and doc_id.id or False

    def _default_state(self):
        doc_id = self.env['res.doc.type'].search([('code', '=', 'bm')])[-1]
        if doc_id and doc_id.approval:
            state = 'draft'
        else:
            state = 'confirmed'
        return state

    name                = fields.Char('Nama', required=False)
    machine_id          = fields.Many2one("lhm.utility", string="Mesin", ondelete="restrict", domain="[('type','=', 'ma')]")
    doc_type_id         = fields.Many2one("res.doc.type", string="Document Type", ondelete="restrict", tracking=True, default=_default_doc_id)
    approval            = fields.Boolean(string="Approval", related="doc_type_id.approval", readonly=True)
    machine_code        = fields.Char('Kode', readonly=True, related="machine_id.code")
    
    account_period_id   = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", tracking=True, default=_default_account_period_id)
    date_start          = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop           = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    
    uom_performance     = fields.Selection([('km', 'KM'), ('hm', 'HM')], string='Satuan', readonly=True, related="machine_id.uom_performance", store=True)
    line_ids            = fields.One2many('lhm.machine.line', inverse_name='lhm_machine_id', string="Detail Buku Mesin", )
    note                = fields.Text("Catatan")
    user_id             = fields.Many2one('res.users', string='Penanggung Jawab', index=True, tracking=True, default=lambda self: self.env.user)
    operating_unit_id   = fields.Many2one('operating.unit', string='Operating Unit', compute='_compute_operating_unit_id', readonly=True, store=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    state               = fields.Selection([
                            ('draft', 'New'), ('cancel', 'Cancelled'),
                            ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                            copy=False, default=_default_state, index=True, readonly=True, tracking=True,
                            help="* New: Dokumen Baru.\n"
                                 "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                 "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                 "* Done: Dokumen Sudah Selesai Diproses. \n")

    @api.onchange('machine_id','account_period_id')
    def onchange_validate(self):
        if self.machine_id and self.account_period_id:
            other_ids = self.env['lhm.machine'].search([('id', '!=', self._origin.id), ('account_period_id', '=', self.account_period_id.id), ('machine_id', '=', self.machine_id.id)])
            if other_ids:
                self.account_period_id  = False
                self.machine_id         = False
                return {
                    'warning': {'title': _('Kesalahan Input Data'),
                                'message': _("Dokumen sudah ada: %s.") % other_ids.name, },
                }


    def unlink(self):
        for machine in self:
            if machine.state not in ['draft'] and self.doc_type_id.approval == True:
                raise UserError(_('Status dokumen Buku Mesin dengan nomor %s adalah %s.\n'
                                  'Buku Kendaraan hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (
                                    machine.name, machine.state.title()))
        machine = super(lhm_machine, self).unlink()
        return machine

    def button_confirm(self):
        self.state = 'confirmed'

    def button_draft(self):
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, values):
        machine = self.env['lhm.utility'].search([('id', '=', values.get('machine_id'))])
        period_id = self.env['account.period'].search([('id', '=', values.get('account_period_id'))])

        if period_id:
            month = period_id.date_start.strftime('%m')
            year = period_id.date_start.strftime('%Y')
            values['name'] = f"{machine.code or ''}/{year}-{month}"
        else:
            values['name'] = f"{machine.code or ''}/"

        return super(lhm_machine, self).create(values)


    def write(self, values):
        for record in self:
            machine_id = values.get('machine_id', record.machine_id.id)
            account_period_id = values.get('account_period_id', record.account_period_id.id)

            machine = self.env['lhm.utility'].browse(machine_id)
            period_id = self.env['account.period'].browse(account_period_id)
            if period_id:
                month = period_id.date_start.strftime('%m')
                year = period_id.date_start.strftime('%Y')
                values['name'] = f"{machine.code or ''}/{year}-{month}"

        return super(lhm_machine, self).write(values)

class lhm_machine_line(models.Model):
    _name           = 'lhm.machine.line'
    _description    = 'LHM Machine Line'
    _order          = 'date, location_type_id, location_id, activity_id asc'

    @api.depends("location_type_id","location_id")
    def _get_doc_activity_ids(self):
        for line in self:
            activity_list = []
            doc_id      = self.env['res.doc.type'].search([('code', '=', 'bm')], limit=1)
            level_1     = self.env['lhm.activity'].search([('level', '=', 1)], limit=1)
            avail_act   = self.env['lhm.activity'].search([('type_id', '=', line.location_type_id.id)])
            if doc_id:
                for act in avail_act:
                    if doc_id.id in act.doc_ids.ids:
                        activity_list.append(act.id)
            if level_1:
                activity_list.append(level_1.id)
            if (line.location_type_id and line.location_type_id.project) and line.location_id:
                project_ids = self.env['lhm.project'].search([('location_id', '=', line.location_id.id)])
                project_act = []
                avail = []
                if level_1:
                    avail.append(level_1.id)
                for project in project_ids:
                    project_act += [x.activity_id.id for x in project.line_ids]
                if project_act != []:
                    for act_project in project_act:
                        if act_project in activity_list:
                            avail.append(act_project)
                if avail:
                    line.doc_activity_ids = [(6, 0, avail)]
                else:
                    line.doc_activity_ids = [(6, 0, activity_list)]
            else:
                line.doc_activity_ids = [(6, 0, activity_list)]

            # Ensure doc_activity_ids is never empty or undefined
            if not line.doc_activity_ids:
                line.doc_activity_ids = [(6, 0, [])]

    name                = fields.Char("Nama", readonly=True, related="lhm_machine_id.name", store=True)
    date                = fields.Date("Tanggal", copy=False)
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    varieties_id        = fields.Many2one('plant.varieties', string="ORG", ondelete='restrict')
    varieties_validator = fields.Boolean(compute='_set_plantation_validator', store=True, string="Varieties Validator")
    @api.depends('location_type_id')
    def _set_plantation_validator(self):
        for line in self:
            validator = False
            if line.location_type_id:
                # Plantation FC, GC, IDC, PJ => True (artinya wajib diisi)
                validator = line.location_type_id.code in ('FC','GC','IDC','PJ')
            line.varieties_validator = validator
    filtered_locations  = fields.Many2many('lhm.location', 'lhm_ma_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    filtered_activities = fields.Many2many('lhm.activity', 'lhm_ma_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    doc_activity_ids    = fields.Many2many('lhm.activity', store=True, compute=_get_doc_activity_ids)
    use_value           = fields.Float("Meter Pemakaian")
    use_hours           = fields.Float("Jam Kerja")
    lhm_machine_id      = fields.Many2one("lhm.machine", string="Buku Mesin", ondelete="cascade")

    @api.depends('varieties_id','location_type_id', 'lhm_machine_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.lhm_machine_id.state!='draft':
                line.filtered_locations = []
            else:
                if line.location_type_id.code in ('NS','LB','GC','MC'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION FC, PJ, IDC
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'lhm_machine_id.state')
    def _filter_activities(self):
        query_parents = """SELECT parent_id FROM lhm_activity"""
        self.env.cr.execute(query_parents)
        parent_activity_ids = [x[0] for x in self.env.cr.fetchall()]
        for line in self:
            if line.lhm_machine_id.state!='draft':
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','bm')], limit=1)
                if line.location_type_id and line.location_type_id.project and line.location_id:
                    projects = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
                    project_activity_ids = []
                    for project in projects:
                        # if doc_form:
                        #     project_activity_ids += [x.activity_id.id for x in project.line_ids if doc_form.id in x.doc_ids.ids]
                        # else:
                            project_activity_ids += [x.activity_id.id for x in project.line_ids if x.activity_id.id not in parent_activity_ids]

                    if project_activity_ids:
                        line.filtered_activities = [(6, 0, project_activity_ids)]
                    else:
                        line.filtered_activities = []
                else:
                    if line.location_type_id.code in ('WS','VH','MA','LB','NS'):
                        domain = [('type_id','=',line.location_type_id.id)]
                        if parent_activity_ids:
                            domain.append(('id','not in',parent_activity_ids))
                        activities = self.env['lhm.activity'].search(domain)
                    else: # GC, IDC, PLANTATION FC
                        if line.varieties_id:
                            if line.location_type_id.general_charge:
                                activities = line.varieties_id.general_charges_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
                            elif line.location_type_id.indirect:
                                activities = line.varieties_id.indirect_cost_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
                            elif line.location_type_id.mills:
                                activities = line.varieties_id.mill_costs_ids.filtered(lambda x: x.id not in parent_activity_ids)
                            else:
                                activities = line.varieties_id.harvest_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
                                activities |= line.varieties_id.upkeep_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
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
    
    @api.onchange('location_type_id')
    def _onchange_location_type_id(self):
        if self.location_type_id:
            self.location_id    = False
            self.activity_id    = False
            self.varieties_id = self.location_type_id.varieties_id.id

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.activity_id    = False

    @api.constrains('date')
    def _check_date_unique(self):
        for rec in self:
            rec._check_date_line()

    def _check_date_line(self):
        if not (self.date >= self.lhm_machine_id.account_period_id.date_start and self.date <= self.lhm_machine_id.account_period_id.date_stop):
            month = [item for item in BULAN_INDONESIA if item[0] == str(fields.Date.from_string(self.lhm_machine_id.account_period_id.date_start).month)][0][1]
            raise UserError(_('Tanggal %s pada Buku Mesin tidak dalam periode %s %s.\n'
                              'Ubah tanggal atau hapus baris di Daftar Buku Mesin') % (
                            self.date, month, str(fields.Date.from_string(self.lhm_machine_id.account_period_id.date_start).year)))
        # domain = [('date', '=', self.date)]
        # if self.search_count(domain) > 1:
        #     raise UserError(_('Tidak boleh ada tanggal yang sama.\n'
        #                       'Tanggal: %s') % self.date)
        return True
    def copy_line(self):
        self.copy()
        return True
############################################## End Of Transaction Buku Mesin ################################################