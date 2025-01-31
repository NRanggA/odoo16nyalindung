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


############################################### Transaction Buku Kontraktor #################################################
class lhm_contractor(models.Model):
    _name           = 'lhm.contractor'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = 'Buku Kontraktor'

    # def _default_account_period_id(self):
    #     # date = time.strftime('%Y-%m-%d')
    #     date = datetime.now().strftime('%Y-%m-%d')
    #     period_id = self.env['account.period'].search([('date_start', '<=', date),
    #                                                    ('date_stop', '>=', date),
    #                                                    ('special', '=', False)])
    #     period = False
    #     if period_id and len(period_id) > 1:
    #         period = period_id[-1]
    #     elif period_id and len(period_id) == 1:
    #         period = period_id
    #     return period and period.id or False

    @api.depends('user_id')
    def _compute_operating_unit_id(self):
        for plantation_transaction in self:
            if plantation_transaction.user_id:
                plantation_transaction.operating_unit_id = plantation_transaction.user_id.default_operating_unit_id

    def _default_doc_id(self):
        if self._context.get('default_type',self.type) == 'vendor':
            doc_id = self.env['res.doc.type'].search([('code', '=', 'bkt')], limit=1)
        else:
            doc_id = self.env['res.doc.type'].search([('code', '=', 'bkta')], limit=1)
        return doc_id and doc_id.id or False

    def _default_state(self):
        if self._context.get('default_type',self.type) == 'vendor':
            doc_id = self.env['res.doc.type'].search([('code', '=', 'bkt')], limit=1)
        else:
            doc_id = self.env['res.doc.type'].search([('code', '=', 'bkta')], limit=1)
        if doc_id and doc_id.approval:
            state = 'draft'
        else:
            state = 'confirmed'
        return state

    name                          = fields.Char('Nama', required=False)
    date                          = fields.Date("Tanggal")
    type                          = fields.Selection([('vehicle','Alat'),('vendor','Vendor')], string='Type', index=False, readonly=True)
    supplier_id                   = fields.Many2one("res.partner", string="Kontraktor", ondelete="restrict")
    supplier_code                 = fields.Char('Kode', readonly=True, related="supplier_id.ref")
    doc_type_id                   = fields.Many2one("res.doc.type", string="Document Type", ondelete="restrict", tracking=True, default=_default_doc_id)
    approval                      = fields.Boolean(string="Approval", related="doc_type_id.approval", readonly=True)
    
    # account_period_id             = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", tracking=True, default=_default_account_period_id)
    # date_stop                     = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    
    date_start                    = fields.Date("Tanggal Pembayaran Mulai")
    date_end                      = fields.Date("Tanggal Pembayaran Selesai")
    
    operating_unit_id             = fields.Many2one('operating.unit', string='Operating Unit', compute='_compute_operating_unit_id', readonly=True, store=True)  #
    contractor_vehicle            = fields.Boolean(string="Vehicle")
    total_type                    = fields.Selection([('used', 'HM/KM Terpakai'), ('result', 'Hasil Kerja')], string='Kalkulasi')
    company_id                    = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    line_ids                      = fields.One2many('lhm.contractor.line', 'contractor_id', string="Detail Kontraktor")
    line_nap_ids                  = fields.One2many('lhm.contractor.nap.line', 'contractor_id', string="Total Biaya Panen Kontraktor Harian")
    line_vehicle_ids              = fields.One2many('lhm.contractor.vehicle.line', 'contractor_id', string="Detail Kontraktor Alat", )
    payment_type                  = fields.Selection([('payment0', 'Pembayaran 1 Bulan Penuh'),('payment1','Pembayaran Ke-1'),('payment2','Pembayaran Ke-2')], string='Pembayaran', index=False, readonly=False)
    user_id                       = fields.Many2one('res.users', string='Penanggung Jawab', index=True, tracking=True, default=lambda self: self.env.user)
    note                          = fields.Text('Catatan')
    state                         = fields.Selection([
                                    ('draft', 'New'), ('cancel', 'Cancelled'), ('process', 'Process'),
                                    ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                                    copy=False, default=_default_state, index=True, readonly=True,
                                    help="* New: Dokumen Baru.\n"
                                        "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                        "* Process: Dokumen Sedang di Process.\n"
                                        "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                        "* Done: Dokumen Sudah Selesai Diproses. \n")
    invoice_id                    = fields.Many2one('account.move', 'Invoice')
    move_id                       = fields.Many2one('account.move', 'Journal Entry')
    amount_total                  = fields.Float(compute='_compute_total', string='Total')
    material_line_ids             = fields.One2many('lhm.contractor.material.line', 'contractor_id', string="Detail Material")
    afdeling_id                   = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    
    contractor_default_journal_id = fields.Many2one(
                                comodel_name='account.journal',
                                related='company_id.contractor_default_journal_id', readonly=False,
                                string="Journal")
    account_payable_contractor_id = fields.Many2one(
                                comodel_name='account.account',
                                related='company_id.account_payable_contractor_id', readonly=False,
                                string="Account Payable Perantara Buku Kontraktor")
    is_hasil_2                   = fields.Boolean(string='Is Hasil 2', compute='_compute_is_hasil_2', store=True)

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        for line in self.line_ids:
            if not line.date:
                line.date = self.date

    @api.depends('line_ids.activity_id.is_panen')
    def _compute_is_hasil_2(self):
        for record in self:
            record.is_hasil_2 = any(line.activity_id.is_hasil_2 for line in record.line_ids)

    @api.depends('line_ids.unit_price', 'line_ids.nilai', 'line_vehicle_ids.unit_price', 'line_vehicle_ids.nilai')
    def _compute_total(self):
        for rec in self:
            amount_total = 0.0
            for line in rec.line_ids:
                amount_total += line.total
            for line in rec.line_vehicle_ids:
                amount_total += line.total
            rec.amount_total = amount_total
                
    @api.constrains('date_start', 'date_end', 'contractor_vehicle', 'type')
    def _check_date_unique(self):
        for rec in self:
            # records = self.search([('supplier_id','=',rec.supplier_id.id),('id','!=',rec.id),('date_start','=',rec.date_start),('date_end','=',rec.date_end),('contractor_vehicle','=',rec.contractor_vehicle), ('type','=',rec.type)])
            if rec.contractor_vehicle:
                records = self.env['lhm.contractor.line'].search([('contractor_id.supplier_id','=',rec.supplier_id.id),
                    ('contractor_id','!=',rec.id),
                    ('date','>=',rec.date_start),('date','<=',rec.date_end),
                    ('contractor_id.contractor_vehicle','=',rec.contractor_vehicle), 
                    ('contractor_id.type','=',rec.type)])
            else:
                records = self.env['lhm.contractor.vehicle.line'].search([('contractor_id.supplier_id','=',rec.supplier_id.id),
                    ('contractor_id','!=',rec.id),
                    ('date','>=',rec.date_start),('date','<=',rec.date_end),
                    ('contractor_id.contractor_vehicle','=',rec.contractor_vehicle), 
                    ('contractor_id.type','=',rec.type)])

            if records:
                
                raise UserError(_('Buku Kontraktor sudah pernah dibuat untuk periode %s.')%rec.account_period_id.name)

    # @api.onchange('supplier_id','account_period_id','payment_type','contractor_vehicle')
    @api.onchange('supplier_id','date_start','date_end','contractor_vehicle')
    def onchange_validate(self):
        if self.env.context.get('is_harian'):
            return
        # if self.supplier_id and self.account_period_id and self.type:
        if self.supplier_id and self.type:
            print(f"berfore Date Start: {self.date_start}")
            print(f"berfore date_end: {self.date_end}")
            # other_ids = self.env['lhm.contractor'].search([('id', '!=', self._origin.id), ('account_period_id', '=', self.account_period_id.id), ('supplier_id', '=', self.supplier_id.id), ('payment_type', '=', self.payment_type), ('type','=',self.type), ('contractor_vehicle','=',self.contractor_vehicle)])
            other_ids = self.env['lhm.contractor'].search([
                ('id', '!=', self._origin.id),
                ('date_start', '<=', self.date_end),
                ('date_end', '>=', self.date_start),
                ('supplier_id', '=', self.supplier_id.id),
                ('payment_type', '=', self.payment_type),
                ('type', '=', self.type),
                ('contractor_vehicle', '=', self.contractor_vehicle)
            ])
            if other_ids:
                # self.account_period_id  = False
                self.supplier_id        = False
                self.date_start         = False
                self.date_end           = False
                return {
                    'warning': {'title': _('Kesalahan Input Data'),
                                'message': _("Dokumen sudah ada: %s.") % other_ids.name, },
                }
            # if self.payment_type:
            #     # month = int(self.account_period_id.date_start.strftime('%m'))
            #     # year = int(self.account_period_id.date_start.strftime('%Y'))
            #     month = self.date_start.strftime('%m')
            #     year = self.date_start.strftime('%Y')
                
            #     last_day = calendar.monthrange(year, month)[1]

            #     if self.payment_type == 'payment1':
            #         self.date_start = datetime(year, month, 1).strftime('%Y-%m-%d')
            #         self.date_end = datetime(year, month, 15).strftime('%Y-%m-%d')

            #     elif self.payment_type == 'payment2':
            #         self.date_start = datetime(year, month, 16).strftime('%Y-%m-%d')
            #         self.date_end = datetime(year, month, last_day).strftime('%Y-%m-%d')

                # else:
                #     self.date_start = self.account_period_id.date_start
                #     self.date_end = self.account_period_id.date_stop

    def unlink(self):
        for contractor in self:
            if contractor.state not in ['draft'] and self.doc_type_id.approval == True:
                raise UserError(_('Status dokumen Buku Kontraktor dengan nomor %s adalah %s.\n'
                                  'Buku Kontraktor hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') %
                                  (contractor.name, contractor.state.title()))
            if contractor.invoice_id:
                raise UserError(_('Buku Kontraktor ini sudah memiliki Vendor Bill'))
            if contractor.move_id:
                raise UserError(_('Buku Kontraktor ini sudah memiliki Journal Entry.\n Silahkan di Cancel terlebih dahulu'))
        contractor = super(lhm_contractor, self).unlink()
        return contractor

    # def button_get_data(self):
    #     self.state = 'draft'
    #     # self.confirmed = True
    
    def button_confirm(self):
        move = self._account_move_entry()
        self.state = 'confirmed'

    # def button_confirm_harian(self):
    #     if not any(line.nilai for line in self.line_ids):
    #         self.state = 'confirmed'
    #         return
    #     for contractor_nap in self.line_nap_ids:
    #         if not contractor_nap.nilai:
    #             raise UserError(_('Salah satu baris di "NAP Kontraktor Harian" tidak memiliki nilai. Silahkan isi melalui Dokumen NAP'))
    #     self.state = 'confirmed'

    def button_confirm_harian(self):
        if not self.is_hasil_2:
            self.state = 'confirmed'
            return
        for contractor_nap in self.line_nap_ids:
            if not contractor_nap.nilai and not contractor_nap.nilai2:
                raise UserError(_('Salah satu baris di "NAP Kontraktor Harian" belum memiliki nilai. Silahkan isi melalui Dokumen NAP'))
        self.state = 'confirmed'

    def button_process(self):
        if not self.date:
            raise UserError(_('Data tanggal kosong, mohon diisi.'))
        self.state = 'process'
        self.env['lhm.contractor.nap.line'].search([('contractor_id', '=', self.id)]).unlink()
        
        contractor_nap_lines = []
        contractor_lines = self.line_ids

        for contractor_line in contractor_lines:
            # if not contractor_line.date:
            #     contractor_line.date = self.date
            nap_line_data = {
                'location_id': contractor_line.location_id.id,
                'activity_id': contractor_line.activity_id.id,
                'product_id': contractor_line.product_id.id,
                'product_id_2': contractor_line.product_id_2.id,
                'nilai': None,
                'nilai2': None,
                'uom_id': contractor_line.uom_id.id,
                'uom2_id': contractor_line.uom2_id.id,
                'contractor_id': self.id,
                'contractor_line_id': contractor_line.id,
                'date': contractor_line.date,
            }
            contractor_nap_lines.append(nap_line_data)

        if contractor_nap_lines:
            self.env['lhm.contractor.nap.line'].create(contractor_nap_lines)
        for line in self.line_ids:
            line._onchange_activity_id()
        # self.line_ids.invalidate_cache(['total'])
        # self.line_ids.invalidate_cache(['uom_id'])
        # self.line_ids.invalidate_cache(['uom2_id'])

    def button_draft(self):
        for contractor in self:
            if contractor.invoice_id:
                raise UserError(_('Buku Kontraktor ini sudah memiliki Vendor Bill'))
            if contractor.move_id:
                raise UserError(_('Buku Kontraktor ini sudah memiliki Journal Entry.\n Silahkan di Cancel terlebih dahulu'))
        self.state = 'draft'

    def button_cancel(self):
        for contractor in self:
            if contractor.invoice_id:
                raise UserError(_('Buku Kontraktor ini sudah memiliki Vendor Bill'))
            if contractor.move_id:
                contractor.move_id.unlink()
            contractor.line_nap_ids.unlink()
        self.state = 'cancel'
        for line in self.line_ids:
            line._onchange_activity_id()
        self.line_ids.invalidate_cache(['total'])
        # self.line_ids.invalidate_cache(['uom_id'])
        # self.line_ids.invalidate_cache(['uom2_id'])

    @api.model
    def create(self, values):
        supplier = self.env['res.partner'].browse(values.get('supplier_id'))
        period = self.env['account.period'].browse(values.get('account_period_id'))

        if self.env.context.get('is_harian'):
            if values.get('date'):
                date_str = fields.Date.from_string(values['date']).strftime('%Y-%m-%d')
                supplier_ref = supplier.ref if supplier.ref else supplier.name
                values['name'] = f"{supplier_ref or 'Unknown Supplier'}/{date_str}"
            else:
                values['name'] = supplier.ref or supplier.name or 'Harian'
        else:
            # if period:
            #     month = period.date_start.strftime('%m')
            #     year = period.date_start.strftime('%Y')
            #     supplier_ref = supplier.ref if supplier.ref else supplier.name
            #     values['name'] = f"{supplier_ref or 'Unknown Supplier'}/{year}-{month}"
            if values.get('date_start'):
                date_obj = fields.Date.from_string(values['date_start'])
                month = date_obj.strftime('%m')
                year = date_obj.strftime('%Y')
                supplier_ref = supplier.ref if supplier.ref else supplier.name
                values['name'] = f"{supplier_ref or 'Unknown Supplier'}/{year}-{month}"
            else:
                values['name'] = supplier.ref or supplier.name or 'Bulanan'

        return super(lhm_contractor, self).create(values)
    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise exceptions.UserError(_("Dokumen dengan status 'Confirmed' tidak dapat dihapus!"))
        return super(lhm_contractor, self).unlink()

    def _account_move_entry(self):
        AccountMove = self.env['account.move']
        AccountMoveLine = self.env['account.move.line']
        grouped_lines = {}
        for buku_kontraktor in self:
            acc_dest = buku_kontraktor.account_payable_contractor_id #untuk credit
            if not acc_dest:
                raise ValidationError(_('Akun Perantara Hutang pada Kontraktor Belum diisi.\n'
                    'Silahkan isi akun tersebut terlebih dahulu'))
            journal_id = buku_kontraktor.contractor_default_journal_id
            if not journal_id:
                raise ValidationError(_('General Jurnal belum didefinisikan.\n'
                    'Silahkan membuat General Jurnal terlebih dahulu'))
            total_lines = 0.0
            for line in buku_kontraktor.line_ids:
                key = (line.location_type_id, line.location_id, line.activity_id)
                if key not in grouped_lines.keys():
                    acc_src = line.activity_id.account_id # untuk debit
                    if not acc_src:
                        raise ValidationError(_('Aktivitas yg digunakan tidak memiliki Account Allocation.\n'
                            'Gunakan Aktivitas lain atau Lengkapi Allocation pada Aktifitas %s %s') % \
                            (line.activity_id.code,line.activity_id.name))
                    # untuk sisi debit
                    grouped_lines.update({key: {
                        'location_type'     : line.location_type_id,
                        'location'          : line.location_id,
                        'activity'          : line.activity_id,
                        'account_id'        : acc_src.id,
                        'journal_id'        : journal_id.id,
                        'partner_id'        : buku_kontraktor.supplier_id.id,
                        'date'              : buku_kontraktor.date_end,
                        'amount'            : 0.0,
                        }})
                grouped_lines[key]['amount'] += line.total
                total_lines += line.total
            for line in buku_kontraktor.line_vehicle_ids:
                key = (line.location_type_id, line.location_id, line.activity_id)
                if key not in grouped_lines.keys():
                    acc_src = line.activity_id.account_id
                    if not acc_src:
                        raise ValidationError(_('Aktivitas yg digunakan tidak memiliki Account Allocation.\n'
                            'Gunakan Aktivitas lain atau Lengkapi Allocation pada Aktifitas %s %s') % \
                            (line.activity_id.code,line.activity_id.name))
                    grouped_lines.update({key: {
                        'location_type'     : line.location_type_id,
                        'location'          : line.location_id,
                        'activity'          : line.activity_id,
                        'account_id'        : acc_src.id,
                        'journal_id'        : journal_id.id,
                        'partner_id'        : buku_kontraktor.supplier_id.id,
                        'date'              : buku_kontraktor.date_end,
                        'amount'            : 0.0,
                        'operating_unit_id' : buku_kontraktor.operating_unit_id and buku_kontraktor.operating_unit_id.id or False,
                        }})
                grouped_lines[key]['amount'] += line.total
                total_lines += line.total
            move_lines = []
            for line in grouped_lines.values():
                move_lines.append((0,0, self._prepare_move_line_entry(line)))
            # counterpart entry for all activity
            # untuk sisi credit
            move_lines.append((0, 0, self._prepare_move_line_entry({
                    'account_id'        : acc_dest.id,
                    'journal_id'        : journal_id.id,
                    'partner_id'        : buku_kontraktor.supplier_id.id,
                    'date'              : buku_kontraktor.date_end,
                    'amount'            : -1*total_lines,
                    'plantation_src_journal_id': journal_id.id,
                    })))
            move = AccountMove.sudo().create({
                'journal_id'    : journal_id.id,
                'date'          : buku_kontraktor.date_end,
                'line_ids'      : move_lines,
                'ref'           : buku_kontraktor.name,
                })
            move.sudo().action_post()
            buku_kontraktor.sudo().write({'move_id': move.id})

    def _prepare_move_line_entry(self, line):
        # convert amount
        amount = line.get('amount', 0.0)
        return {
            'name'                          : line.get('activity', False) and line['activity'].name or '/',
            'plantation_location_type_id'   : line.get('location_type', False) and line['location_type'].id or False,
            'plantation_location_id'        : line.get('location', False) and line['location'].id or False,
            'plantation_activity_id'        : line.get('activity', False) and line['activity'].id or False,
            'account_id'                    : line.get('account_id', False) and line['account_id'] or False,
            'journal_id'                    : line.get('journal_id', False) and line['journal_id'] or False,
            'date'                          : line.get('date', False) and line['date'] or False,
            'debit'                         : amount>0 and amount or 0.0,
            'credit'                        : amount<0 and -1*amount or 0.0,
            # 'amount_currency'               : 0.0,
            # 'currency_id'                   : False,
        }

    def write(self, values):
        supplier_id     = self.env['lhm.utility'].search([('id', '=', values.get('supplier_id', self.supplier_id.id))])
        # period_id       = self.env['account.period'].search([('id', '=', values.get('account_period_id', self.account_period_id.id))])
        # if period_id:
        #     month           = period_id.date_start.strftime('%m')
        #     year            = period_id.date_start.strftime('%Y')
        #     values['name']  = (supplier_id.code or "") + "/" + year + "-" + month
        # Menggunakan date baru jika diubah, atau tetap pakai yang lama jika tidak ada perubahan
        date_value = values.get('date', self.date)
        if date_value:
            date_obj = fields.Date.from_string(date_value)
            month = date_obj.strftime('%m')
            year = date_obj.strftime('%Y')
            values['name'] = f"{supplier_id.code or ''}/{year}-{month}"

        return super(lhm_contractor, self).write(values)

    def get_material(self):
        move_obj            = self.env['stock.move']
        material_line_obj   = self.env['lhm.contractor.material.line']
        for contractor in self:
            # UPDATE line yg sudah terlanjur terbuat
            line_to_update = []
            line_to_delete = []
            
            for mat_line in sorted(contractor.material_line_ids, key=lambda x:x.date):
                if mat_line.realization>0.0 and mat_line.residual_qty>0.0:
                    line_to_update.append(mat_line)
                elif mat_line.realization>0.0 and mat_line.residual_qty==0.0:
                    line_to_delete.append(mat_line)
            for line in contractor.material_line_ids.filtered(lambda x: x.realization==0.0):
                if line.move_id.id in [x.move_id.id for x in line_to_update]:
                    line.write({
                            'stock_qty' : line.move_id.plantation_material_allocation,
                        })
            for line in contractor.material_line_ids.filtered(lambda x: x.realization==0.0):
                if line.move_id.id in [x.move_id.id for x in line_to_delete]:
                    line.unlink()

            # Tambah SKB baru
            for line in sorted(contractor.line_ids.filtered(lambda x: x.location_id \
                        and x.location_id.type_id.skb_declare), key=lambda x:x.date):
                domain = [
                        ('date', '<=', str(line.date) + ' 23:59:59'), 
                        # ('skb', '=', True), 
                        ('picking_type_id.code', '=', 'issue'), 
                        ('state', '=', 'done'), 
                        ('plantation_location_id', '=', line.location_id.id), 
                        ('plantation_activity_id', '=', line.activity_id.id), 
                        ('origin_returned_move_id', '=', False),
                        ('pending_material_allocation', '>', 0.0),
                        ]
                current_material = material_line_obj.search([('line_id','=',line.id)])
                if current_material:
                    current_move = current_material.mapped('move_id')
                    domain.append(('id','not in',current_move.ids))
                pending_moves = move_obj.search(domain)
                for skb in pending_moves:
                    values_skb  = {
                        'name'              : skb.picking_id.bpb_number or '',
                        'date'              : line.date,
                        'product_id'        : skb.product_id.id,
                        'location_id'       : skb.plantation_location_id.id,
                        'activity_id'       : skb.plantation_activity_id.id,
                        'real_stock_qty'    : skb.product_uom_qty,
                        'stock_qty'         : skb.plantation_material_allocation,
                        'product_uom_id'    : skb.product_uom.id,
                        'move_id'           : skb.id,
                        'picking_id'        : skb.picking_id and skb.picking_id.id or False,
                        'contractor_id'     : contractor.id,
                        'line_id'           : line.id,
                    }
                    material_line_obj.create(values_skb)

class lhm_contractor_material_line(models.Model):
    _name           = 'lhm.contractor.material.line'
    _description    = 'LHM Contractor Material Line'

    name            = fields.Char("BPB", readonly=True)
    date            = fields.Date("Tanggal", required="True")
    product_id      = fields.Many2one("product.product", string="Product", ondelete="restrict")
    activity_id     = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    activity_name   = fields.Char(related="activity_id.name", string="Name")
    block_id        = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    location_id     = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    real_stock_qty  = fields.Float('SKB Qty', digits=dp.get_precision('Product Unit of Measure'),)
    product_uom_id  = fields.Many2one("uom.uom", string="UoM", ondelete="restrict")
    stock_qty       = fields.Float('Declared', digits=dp.get_precision('Product Unit of Measure'),)
    realization     = fields.Float('Qty Realisasi', digits=dp.get_precision('Product Unit of Measure'),)
    residual_qty    = fields.Float(compute='_get_residual', string='Residual', digits=dp.get_precision('Product Unit of Measure'),)
    move_id         = fields.Many2one("stock.move", string="Stock Move", ondelete="restrict")
    picking_id      = fields.Many2one("stock.picking", string="Stock Picking", ondelete="restrict")
    line_id         = fields.Many2one("lhm.contractor.line", string="Progress", ondelete="restrict")
    contractor_id   = fields.Many2one("lhm.contractor", "LHM Contractor", ondelete="cascade")

    @api.depends('realization')
    def _get_residual(self):
        for line in self:
            residual = line.real_stock_qty - line.stock_qty - line.realization
            # if residual < 0:
            #     line.residual_qty = residual
            #     raise UserError(_('Realisasi Salah.\n'
            #                     'Realisasi tidak dapat melebihi Jumlah yg di SKB'))
            # else:
            line.residual_qty = residual

class lhm_contractor_line(models.Model):
    _name = 'lhm.contractor.line'
    _description = 'LHM Contractor Line'

    @api.depends("location_type_id","location_id")
    def _get_doc_activity_ids(self):
        for line in self:
            activity_list = []
            if line.contractor_id._context.get('default_type',line.contractor_id.type) == 'vendor':
                doc_id  = self.env['res.doc.type'].search([('code', '=', 'bkt')], limit=1)
            else:
                doc_id  = self.env['res.doc.type'].search([('code', '=', 'bkta')], limit=1)
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
                if avail != []:
                    line.doc_activity_ids = [(6, 0, avail)]
            else:
                line.doc_activity_ids = [(6, 0, activity_list)]

    # Field definitions
    name                = fields.Char(related='activity_id.name', readonly=True)
    date                = fields.Date("Tanggal")
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    no_line             = fields.Boolean(string="Mandatory", related="location_type_id.no_line")
    varieties_validator = fields.Boolean(compute='_set_plantation_validator', store=True, string="Varieties Validator")
    @api.depends('location_type_id')
    def _set_plantation_validator(self):
        for line in self:
            validator = False
            if line.location_type_id:
                # Plantation, GC, IDC, PJ, NS => True (artinya wajib diisi)
                validator = line.location_type_id.code in ('FC','GC','IDC', 'PJ') # 'NS
            line.varieties_validator = validator
    varieties_id        = fields.Many2one('plant.varieties', string="ORG", ondelete='restrict')
    filtered_locations  = fields.Many2many('lhm.location', 'lhm_cont_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    block_id            = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    doc_activity_ids    = fields.Many2many('lhm.activity', store=True, compute=_get_doc_activity_ids)
    filtered_activities = fields.Many2many('lhm.activity', 'lhm_cont_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    nilai               = fields.Float('Hasil 1')
    uom_id              = fields.Many2one("uom.uom", string="Satuan 1", ondelete="restrict")
    nilai2              = fields.Float('Hasil 2')
    uom2_id             = fields.Many2one("uom.uom", string="Satuan 2", ondelete="restrict")
    unit_price          = fields.Float('Tarif Satuan')
    unit_price_2        = fields.Float('Tarif Satuan 2')
    total               = fields.Float('Nilai', compute='_compute_harga_satuan', store=True, readonly=True)
    type                = fields.Selection([('vehicle', 'Alat'), ('vendor', 'Vendor')], string='Type', related="contractor_id.type", readonly=True)
    supplier_id         = fields.Many2one("res.partner", related="contractor_id.supplier_id", readonly=True)
    contractor_vehicle  = fields.Boolean(string="Vehicle", related="contractor_id.contractor_vehicle", readonly=True)
    contractor_id       = fields.Many2one("lhm.contractor", string="Contractor", ondelete="cascade")
    line_nap_ids        = fields.One2many('lhm.contractor.nap.line', 'contractor_line_id', string="NAP Lines")
    lhm_nap_line_id     = fields.Many2one('lhm.nap.line', string="NAP Line", ondelete="cascade")
    tidak_ditagihkan    = fields.Boolean(string="Tidak Ditagihkan")
    skip_constraint     = fields.Boolean(string="Skip Constraint")
    product_id          = fields.Many2one('product.product', string="Product 1", ondelete="restrict")
    product_id_2        = fields.Many2one('product.product', string="Product 2", ondelete="restrict")
    drc_latex_nap       = fields.Float('DRC Latex NAP (%)')
    drc_lump_nap        = fields.Float('DRC Lump NAP (%)')
    hasil_convert_latex = fields.Float(string="Hasil Convert Latex",  digits=(16, 2))
    hasil_convert_lump  = fields.Float(string="Hasil Convert Lump",  digits=(16, 2))

    @api.depends('varieties_id','location_type_id', 'contractor_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.contractor_id.state!='draft':
                line.filtered_locations = []
            else:
                if line.location_type_id.code in ('WS','VH','MA','GC','MC','LB'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'contractor_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.contractor_id.state!='draft':
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','bkt')], limit=1)
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
                            # menambahkan tipe lokasi mills 
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
    
    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            borongan_contractor = self.env['lhm.wage.borongan.contractor'].search([('activity_id', '=', self.activity_id.id)]);
            
            self.unit_price   = borongan_contractor.price if borongan_contractor.price else 0.0
            self.unit_price_2 = borongan_contractor.price2 if borongan_contractor.price2 else 0.0
            if not self.uom_id:
                self.uom_id = self.activity_id.uom_id and self.activity_id.uom_id.id or False
            if not self.uom2_id:
                self.uom2_id = self.activity_id.uom2_id and self.activity_id.uom2_id.id or False
            if self.env.context.get('is_harian'):
                self.product_id   = borongan_contractor.product_id and borongan_contractor.product_id.id or False
                self.product_id_2 = borongan_contractor.product_id2 and borongan_contractor.product_id2.id or False

    @api.onchange('location_type_id')
    def _onchange_location_type_id(self):
        if self.location_type_id:
            self.location_id = False
            self.activity_id = False
            self.varieties_id = self.location_type_id.varieties_id.id

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.activity_id = False

    @api.depends('unit_price', 'nilai', 'product_id', 'product_id_2', 'line_nap_ids.hasil_convert_latex', 'line_nap_ids.hasil_convert_lump')
    def _compute_harga_satuan(self):
        for line in self:
            total_latex = sum(line.line_nap_ids.filtered(lambda l: l.product_id.name == "Lateks").mapped('hasil_convert_latex'))
            total_lump = sum(line.line_nap_ids.filtered(lambda l: l.product_id_2.name == "Lump").mapped('hasil_convert_lump'))
            
            if line.product_id.name == "Lateks" or line.product_id_2.name == "Lump":
                line.total = (line.unit_price * total_latex) + (line.unit_price_2 * total_lump)
            else:
                line.total = (line.unit_price * line.nilai) + (line.unit_price_2 * line.nilai2)
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
        else:
            self.uom_id = False

    @api.onchange('product_id_2')
    def _onchange_product_id_2(self):
        if self.product_id_2:
            self.uom2_id = self.product_id_2.uom_id
        else:
            self.uom2_id = False

    @api.constrains('date', 'location_id', 'activity_id')
    def _check_date_unique(self):
        for rec in self:
            rec._check_date_line()

    def _check_date_line(self):
        if self.skip_constraint:
            return True

        if not (self.date >= self.contractor_id.date_start and self.date <= self.contractor_id.date_end):
            raise UserError(_('Tanggal %s pada Buku Kontraktor tidak dalam Periode Pembayaran \n'
                              '%s - %s.\n'
                              'Ubah tanggal atau hapus baris di Daftar Buku Kontraktor') % (
                            self.date, self.contractor_id.date_start, self.contractor_id.date_end))
        domain = []
        total_domain = 0
        if self.date:
            domain.append(('date', '=', self.date))
            total_domain += 1
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
            total_domain += 1
        if self.activity_id:
            domain.append(('activity_id', '=', self.activity_id.id))
            total_domain += 1
        if self.type:
            domain.append(('type', '=', self.type))
            total_domain += 1
        if self.supplier_id:
            domain.append(('supplier_id', '=', self.supplier_id.id))
            total_domain += 1
        if self.unit_price:
            domain.append(('unit_price', '=', self.unit_price))
            total_domain += 1
        if total_domain == 6 and self.search_count(domain) > 1:
            raise UserError(_('Terjadi Duplikasi Data!!!!.\n'
                              'Tanggal          : %s.\n'
                              'Kode Lokasi      : %s.\n'
                              'Kode Aktivitas   : %s.\n'
                              'Ganti salah satu detail atau hapus baris yang sama') % (self.date, self.location_id.code, self.activity_id.code))
        return True
    
    # validasi tanggal pada buku kontraktor harian
    @api.onchange('date')
    def _onchange_(self):
        for line in self:
            if line.contractor_id and line.contractor_id.date_start and line.contractor_id.date_end:
                date_start  = line.contractor_id.date_start
                date_end    = line.contractor_id.date_end
                if line.date and line.date < date_start:
                    raise ValidationError(f"Tanggal tidak boleh sebelum tanggal : {date_start}")
                if line.date and line.date > date_end:
                    raise ValidationError(f"Tanggal tidak boleh melebihi tanggal : {date_end}")
                
class lhm_contractor_nap_line(models.Model):
    _name = 'lhm.contractor.nap.line'
    _description = 'LHM Contractor NAP Line'

    @api.depends("location_type_id","location_id")
    def _get_doc_activity_ids(self):
        for line in self:
            activity_list = []
            if line.contractor_id._context.get('default_type',line.contractor_id.type) == 'vendor':
                doc_id  = self.env['res.doc.type'].search([('code', '=', 'bkt')], limit=1)
            else:
                doc_id  = self.env['res.doc.type'].search([('code', '=', 'bkta')], limit=1)
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
                if avail != []:
                    line.doc_activity_ids = [(6, 0, avail)]
            else:
                line.doc_activity_ids = [(6, 0, activity_list)]

    # Field definitions
    name                = fields.Char(related='activity_id.name', readonly=True)
    date                = fields.Date("Tanggal")
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    no_line             = fields.Boolean(string="Mandatory", related="location_type_id.no_line")
    varieties_validator = fields.Boolean(compute='_set_plantation_validator', store=True, string="Varieties Validator")
    @api.depends('location_type_id')
    def _set_plantation_validator(self):
        for line in self:
            validator = False
            if line.location_type_id:
                # Plantation, GC, IDC, PJ, NS => True (artinya wajib diisi)
                validator = line.location_type_id.code in ('FC','GC','IDC', 'PJ') # 'NS
            line.varieties_validator = validator
    varieties_id        = fields.Many2one('plant.varieties', string="Varietas", ondelete='restrict')
    filtered_locations  = fields.Many2many('lhm.location', 'lhm_cont_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    block_id            = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    doc_activity_ids    = fields.Many2many('lhm.activity', store=True, compute=_get_doc_activity_ids)
    filtered_activities = fields.Many2many('lhm.activity', 'lhm_cont_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    nilai               = fields.Float('Hasil 1')
    uom_id              = fields.Many2one("uom.uom", string="Satuan 1", ondelete="restrict")
    nilai2              = fields.Float('Hasil 2')
    uom2_id             = fields.Many2one("uom.uom", string="Satuan 2", ondelete="restrict")
    unit_price          = fields.Float('Tarif Satuan')
    total               = fields.Float('Nilai', compute='_compute_harga_satuan', store=True, readonly=True)
    type                = fields.Selection([('vehicle', 'Alat'), ('vendor', 'Vendor')], string='Type', related="contractor_id.type", readonly=True)
    supplier_id         = fields.Many2one("res.partner", related="contractor_id.supplier_id", readonly=True)
    contractor_vehicle  = fields.Boolean(string="Vehicle", related="contractor_id.contractor_vehicle", readonly=True)
    contractor_id       = fields.Many2one("lhm.contractor", string="Contractor", ondelete="cascade")
    contractor_line_id  = fields.Many2one('lhm.contractor.line', string="Contractor Lines", ondelete="cascade")
    tidak_ditagihkan    = fields.Boolean(string="Tidak Ditagihkan")
    skip_constraint     = fields.Boolean(string="Skip Constraint")
    product_id          = fields.Many2one('product.product', string="Product 1", ondelete="restrict")
    product_id_2        = fields.Many2one('product.product', string="Product 2", ondelete="restrict")
    drc_latex_nap       = fields.Float('DRC Latex NAP (%)')
    drc_lump_nap        = fields.Float('DRC Lump NAP (%)')
    hasil_convert_latex = fields.Float(string="Hasil Convert Latex",  digits=(16, 2))
    hasil_convert_lump  = fields.Float(string="Hasil Convert Lump",  digits=(16, 2))

    def convert_karet_contractor(self):
        """
        Fungsi untuk menghitung konversi hasil latex dan lump.
        """
        convert_hasil_latex = 0
        convert_hasil_lump = 0

        drc_latex           = self.drc_latex_nap
        convert_hasil_latex = self.nilai * drc_latex / 100

        drc_lump            = self.drc_lump_nap
        convert_hasil_lump  = self.nilai2 * drc_lump / 100

        self.write({
            'hasil_convert_latex'   : convert_hasil_latex,
            'hasil_convert_lump'    : convert_hasil_lump
        })
        
        return convert_hasil_latex, convert_hasil_lump

    @api.depends('varieties_id','location_type_id', 'contractor_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.contractor_id.state!='draft':
                line.filtered_locations = []
            else:
                if line.location_type_id.code in ('WS','VH','MA','GC','MC','LB'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'contractor_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.contractor_id.state!='draft':
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','bkt')], limit=1)
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
    
    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            borongan_contractor = self.env['lhm.wage.borongan.contractor'].search([('activity_id', '=', self.activity_id.id)]);
            
            self.unit_price = borongan_contractor.price if borongan_contractor.price else 0.0
            self.uom_id     = self.activity_id.uom_id and self.activity_id.uom_id.id or False
            self.uom2_id    = self.activity_id.uom2_id and self.activity_id.uom2_id.id or False

    @api.onchange('location_type_id')
    def _onchange_location_type_id(self):
        if self.location_type_id:
            self.location_id = False
            self.activity_id = False

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.activity_id = False

    @api.depends('unit_price', 'nilai')
    def _compute_harga_satuan(self):
        for harga in self:
            if harga.nilai and harga.unit_price:
                harga.total = harga.unit_price * harga.nilai

    @api.constrains('date', 'location_id', 'activity_id')
    def _check_date_unique(self):
        for rec in self:
            rec._check_date_line()

    def _check_date_line(self):
        if self.skip_constraint:
            return True

        if not (self.date >= self.contractor_id.date_start and self.date <= self.contractor_id.date_end):
            raise UserError(_('Tanggal %s pada Buku Kontraktor tidak dalam Periode Pembayaran \n'
                              '%s - %s.\n'
                              'Ubah tanggal atau hapus baris di Daftar Buku Kontraktor') % (
                            self.date, self.contractor_id.date_start, self.contractor_id.date_end))
        domain = []
        total_domain = 0
        if self.date:
            domain.append(('date', '=', self.date))
            total_domain += 1
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
            total_domain += 1
        if self.activity_id:
            domain.append(('activity_id', '=', self.activity_id.id))
            total_domain += 1
        if self.type:
            domain.append(('type', '=', self.type))
            total_domain += 1
        if self.supplier_id:
            domain.append(('supplier_id', '=', self.supplier_id.id))
            total_domain += 1
        if self.unit_price:
            domain.append(('unit_price', '=', self.unit_price))
            total_domain += 1
        if total_domain == 6 and self.search_count(domain) > 1:
            raise UserError(_('Terjadi Duplikasi Data!!!!.\n'
                              'Tanggal          : %s.\n'
                              'Kode Lokasi      : %s.\n'
                              'Kode Aktivitas   : %s.\n'
                              'Ganti salah satu detail atau hapus baris yang sama') % (self.date, self.location_id.code, self.activity_id.code))
        return True

class lhm_contractor_vehicle_line(models.Model):
    _inherit        = 'lhm.contractor.line'
    _name           = 'lhm.contractor.vehicle.line'
    _description    = 'LHM Contractor Vehicle Line'

    @api.depends("start_value", "end_value")
    def _compute_difference(self):
        for diff in self:
            diff.difference_value = diff.end_value - diff.start_value

    @api.depends("activity_id")
    def _get_charge_activity_ids(self):
        for line in self:
            if line.activity_id and line.activity_id.charge_ids:
                line.filter_charge_ids = [(6, 0, [x.id for x in line.activity_id.charge_ids])]
            else:
                line.filter_charge_ids = []

    start_value         = fields.Float("km/hm Berangkat")
    end_value           = fields.Float("km/hm Kembali")
    difference_value    = fields.Float("km/hm Terpakai", compute="_compute_difference", store=True)
    vehicle_id          = fields.Many2one("lhm.utility", string="Alat", ondelete="restrict")
    charge_value        = fields.Float("Vol. Muatan")
    distance_value      = fields.Float("Jarak")
    filter_charge_ids   = fields.Many2many('lhm.charge.type', store=True, compute=_get_charge_activity_ids)
    charge_id           = fields.Many2one("lhm.charge.type", string="Muatan", ondelete="restrict")
    uom_charge_id       = fields.Many2one("uom.uom", string="Satuan Muatan", ondelete="restrict")
    contractor_id       = fields.Many2one("lhm.contractor", string="Contractor", ondelete="cascade")

    @api.onchange('vehicle_id', 'date')
    def _onchange_vehicle_id(self):
        lhm_contractor_obj = self.env['lhm.contractor']
        context = self._context
        if self.vehicle_id and self.date:
            date = self.date or self.contractor_id.date_start
            # Convert date to datetime.date if it's a string
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()

            if context.get('line_vehicle_ids'):
                line_vehicle_ids = context.get('line_vehicle_ids')
                # Assuming line_vehicle_ids are a list of tuples with command (6, 0, ids) or (0, 0, values)
                if isinstance(line_vehicle_ids, list):
                    lines_with_values = [x[2] for x in line_vehicle_ids if x[0] == 0]
                    last_end_value = 0.0
                    for x in lines_with_values:
                        # Convert x['date'] to datetime.date if it's a string
                        x_date = x['date']
                        if isinstance(x_date, str):
                            x_date = datetime.strptime(x_date, '%Y-%m-%d').date()
                        if x['vehicle_id'] == self.vehicle_id.id and x_date <= date and x['end_value'] > last_end_value:
                            last_end_value = x['end_value']
                    self.start_value = last_end_value
            else:
                other_id = self.search([('vehicle_id', '=', self.vehicle_id.id), ('date', '<=', date)], order="date desc", limit=1)
                if other_id:
                    self.start_value = other_id.end_value


    # @api.onchange('vehicle_id', 'date')
    # def _onchange_vehicle_id(self):
    #     lhm_contractor_obj = self.env['lhm.contractor']
    #     context = self._context
    #     if self.vehicle_id and self.date:
    #         date = self.date and self.date or self.contractor_id.date_start
    #         if context.get('line_vehicle_ids'):
    #             line_dict = lhm_contractor_obj.resolve_2many_commands('line_vehicle_ids', context.get('line_vehicle_ids'))
    #             last_end_value = 0.0
    #             for x in line_dict:
    #                 if x['vehicle_id'] == self.vehicle_id.id and x['date'] <= date and x['end_value'] > last_end_value:
    #                     last_end_value = max([x['end_value'] for x in line_dict])
    #             self.start_value = last_end_value
    #         else:
    #             other_id    = self.search([('vehicle_id','=',self.vehicle_id.id),('date','<=',date),], order="date desc", limit=1)
    #             if other_id:
    #                 self.start_value = other_id.end_value


    @api.depends('unit_price', 'nilai', 'difference_value')
    def _compute_harga_satuan(self):
        for harga in self:
            if harga.nilai:
                harga.total = harga.unit_price * harga.nilai
            if harga.contractor_id and harga.difference_value and harga.unit_price:
                if harga.contractor_id.total_type == 'used' and harga.difference_value:
                    harga.total = harga.unit_price * harga.difference_value
                else:
                    harga.total = harga.unit_price * harga.nilai

    def _check_date_line(self):
        if self.skip_constraint:
            return True
        if not (self.date >= self.contractor_id.date_start and self.date <= self.contractor_id.date_end):
            raise UserError(_('Tanggal %s pada Buku Kontraktor tidak dalam Periode Pembayaran \n'
                              '%s - %s.\n'
                              'Ubah tanggal atau hapus baris di Daftar Buku Kontraktor') % (
                            self.date, self.contractor_id.date_start, self.contractor_id.date_end))
        domain          = []
        total_domain    = 0
        if self.date:
            domain.append(('date', '=', self.date))
            total_domain +=1
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
            total_domain += 1
        if self.activity_id:
            domain.append(('activity_id', '=', self.activity_id.id))
            total_domain += 1
        if self.type:
            domain.append(('type', '=', self.type))
            total_domain += 1
        if self.supplier_id:
            domain.append(('supplier_id', '=', self.supplier_id.id))
            total_domain += 1
        if self.vehicle_id:
            domain.append(('vehicle_id', '=', self.vehicle_id.id))
            total_domain += 1
        if self.unit_price:
            domain.append(('unit_price', '=', self.unit_price))
            total_domain += 1
        if total_domain == 7 and self.search_count(domain) > 1:
            raise UserError(_('Terjadi Duplikasi Data!!!!.\n'
                              'Tanggal          : %s.\n'
                              'Kode Lokasi      : %s.\n'
                              'Kode Aktivitas   : %s.\n'
                              'Ganti salah satu detail atau hapus baris yang sama') % (self.date, self.location_id.code, self.activity_id.code))
        return True
########################################### End Of Transaction Buku Kontraktor ##############################################