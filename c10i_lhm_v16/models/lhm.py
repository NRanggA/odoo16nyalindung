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


#---------------------------------------------------------------------------------------------------------------------------#
#############################################################################################################################
#
#   This is for Configuration Models
#
#############################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------#
#################################################### Config Location Type ###################################################
class lhm_location_type(models.Model):
    _name           = 'plantation.location.reference'
    _description    = 'Plantation Location Reference'
    _order          = 'code, name'

    name            = fields.Char("Name")
    code            = fields.Char("Code")
    active          = fields.Boolean("Active", default=True)
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)

class lhm_location_type(models.Model):
    _name           = 'lhm.location.type'
    _description    = 'LHM Location Type'
    _order          = 'code, name'

    name                    = fields.Char("Name")
    code                    = fields.Char("Code")
    active                  = fields.Boolean("Active", default=True)
    
    indirect                = fields.Boolean("Indirect", default=False)
    general_charge          = fields.Boolean("General Charge", default=False)
    infrastruktur           = fields.Boolean("Infrastruktur", default=False)
    machine                 = fields.Boolean("Machine", default=False)
    nursery                 = fields.Boolean("Nursery", default=False)
    oil_palm                = fields.Boolean("Oil Palm", default=False)
    plantation = fields.Boolean("Upkeep and Harvesting", default=False)
    project                 = fields.Boolean("Project", default=False)
    vehicle                 = fields.Boolean("Vehicle", default=False)
    workshop                = fields.Boolean("Workshop", default=False)
    workshop_line           = fields.Boolean("Workshop Line", default=False, help="Centang jika tipe lokasi ingin ditampilkan di Buku Workshop")
    machine_line            = fields.Boolean("Machine Line", default=False, help="Centang jika tipe lokasi ingin ditampilkan di Buku Mesin")
    no_line                 = fields.Boolean("No Line", default=False, help="Centang jika tipe lokasi tidak ingin ditampilkan di Dokumen Plantation Manabun")
    station = fields.Boolean("Mills Station", default=False)

    varieties_id = fields.Many2one('plant.varieties', string='ORG')
    # Boolean Mils
    mills                   = fields.Boolean('Mills', default=False)

    
    skb_declare             = fields.Boolean("SKB Declare", default=False)
    has_subtype             = fields.Boolean("Sub Tipe?", help="Centang jika memiliki sub tipe")
    # account_activity        = fields.Boolean("Use Account From Activity?", help="Langsung menggunakan account dari aktivitas")
    account_id              = fields.Many2one("account.account", string="Default Activity Allocation Account", ondelete="restrict")
    
    location_ids            = fields.One2many("lhm.location", inverse_name="type_id", string="Daftar Lokasi", )
    activity_ids            = fields.One2many("lhm.activity", inverse_name="type_id", string="Daftar Aktivitas", )
    subtype_ids             = fields.One2many("lhm.sub.location.type", inverse_name="type_id", string="Daftar Sub Type Location")
    
    company_id              = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    beban_closing_account_id = fields.Many2one('account.account', 'Beban Alokasi Closing Account (Default)')

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_location_type = self.search(domain + args, limit=limit)
        return lhm_location_type._name_get()
################################################## End Config Location Type #################################################
################################################# Config Sub Type Location ##################################################
class lhm_sub_location_type(models.Model):
    _name           = 'lhm.sub.location.type'
    _description    = 'LHM Sub Type Location'

    name        = fields.Char("Name")
    code        = fields.Char("Code")
    type_id     = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    company_id  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active      = fields.Boolean("Active", default=True)
############################################## End Of Config Sub Type Location ##############################################
###################################################### Config Location ######################################################
class lhm_location(models.Model):
    _name           = 'lhm.location'
    _description    = 'LHM Location'

    name                = fields.Char("Name")
    code                = fields.Char("Code")
    
    type_id             = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    varieties_id = fields.Many2one('plant.varieties', string='Varietas', ondelete='restrict')

    group_progress_id   = fields.Many2one("plantation.location.reference", string="Grouping LPPH")
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active              = fields.Boolean("Active", default=True)
    owner_type          = fields.Selection([('inti','Inti'),('plasma','Plasma')], 'Tipe Kepemilikan Blok')
    
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_location = self.search(domain + args, limit=limit)
        return lhm_location._name_get()
#################################################### End Config Location ####################################################
######################################################## Config Uom #########################################################
# class lhm_uom(models.Model):
#     _name           = 'lhm.uom'
#     _description    = 'LHM UOM Management'
#
#     name            = fields.Char("Name")
#     code            = fields.Char("Code")
#     rounding        = fields.Float("Pembulatan")
#     factor          = fields.Float("Pengali")
#     active          = fields.Boolean("Active", default=True)
#     company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
#
#   
#     def name_get(self):
#         result = []
#         for record in self:
#             if record.name and record.code:
#                 result.append((record.id, record.code))
#             if record.name and not record.code:
#                 result.append((record.id, record.name))
#         return result
#
#   
#     def _name_get(self):
#         result = []
#         for record in self:
#             if record.name and record.code:
#                 result.append((record.id, record.code + " - " + record.name))
#             if record.name and not record.code:
#                 result.append((record.id, record.name))
#         return result
#
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         args = args or []
#         domain = []
#         if name:
#             domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
#             if operator in expression.NEGATIVE_TERM_OPERATORS:
#                 domain = ['&', '!'] + domain[1:]
#         lhm_uom = self.search(domain + args, limit=limit)
#         return lhm_uom._name_get()
# ###################################################### End Config Uom #######################################################
################################################### Config Beban Muatan #####################################################
class lhm_charge_type(models.Model):
    _name           = 'lhm.charge.type'
    _description    = 'LHM Charge Type'

    name        = fields.Char("Nama")
    code        = fields.Char("Kode")
    uom_id      = fields.Many2one("uom.uom", string="Satuan", ondelete="restrict")
    company_id  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active      = fields.Boolean("Active", default=True)
############################################### End Of Config Beban Muatan ##################################################
################################################### Config Kelas Lahan ######################################################
class lhm_land_class(models.Model):
    _name           = 'lhm.land.class'
    _description    = 'Kelas Lahan'

    name        = fields.Char("Name")
    code        = fields.Char("Code")
    active      = fields.Boolean("Active", default=True)
    company_id  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
############################################### End Of Config Kelas Lahan ###################################################
############################################# Config Kecambah Kelapa Sawit ##################################################
class lhm_palm_oil_sprouts(models.Model):
    _name           = 'lhm.palm.oil.sprouts'
    _description    = 'Kecambah Kelapa Sawit'

    name        = fields.Char("Name")
    code        = fields.Char("Code")
    active      = fields.Boolean("Active", default=True)
    company_id  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
########################################## End Of Config Kecambah Kelapa Sawit ##############################################
############################################## Config Berat Janjang Rata-Rata ###############################################
class lhm_restan_balace(models.Model):
    _name           = 'lhm.restan.balance'
    _description    = 'LHM Restan Saldo Awal'

    tgl_panen = fields.Date(" Tanggal Panen")
    block_id = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    value = fields.Float('Saldo Awal (Janjang)')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
########################################### End Of Config Berat Janjang Rata-Rata  ##########################################
#---------------------------------------------------------------------------------------------------------------------------#
#############################################################################################################################
#
#   This is for Master Models
#
#############################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------#

################################################### Master Indirect Cost ####################################################
class plantation_indirect_cost(models.Model):
    _name           = 'plantation.indirect.cost'
    _description    = 'Master Plantation Indirect Cost'

    def _default_location_type(self):
        location_type_ids   = self.env['lhm.location.type'].search([('indirect','=',True)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False

    name                = fields.Char("Name")
    code                = fields.Char("Code")
    varieties_id = fields.Many2one("plant.varieties", string="Varietas", ondelete='restrict')
    location_id         = fields.Many2one("lhm.location", string="Lokasi")
    location_type_id    = fields.Many2one("lhm.location.type", string="Type Lokasi", ondelete="restrict", default=_default_location_type)
    group_progress_id   = fields.Many2one("plantation.location.reference", string="Grouping LPPH")
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active              = fields.Boolean("Active", default=True)

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_location_type = self.search(domain + args, limit=limit)
        return lhm_location_type._name_get()

    @api.model
    def create(self, values):
        location_name       = values.get('name', False)
        location_code       = values.get('code', False)
        location_type_id    = values.get('location_type_id', False)
        group_progress_id   = values.get('group_progress_id', False)
        location_values = {
            'name'              : location_name or "(NoName)",
            'code'              : location_code or "(NoCode)",
            'type_id'           : location_type_id or False,
            'varieties_id': values.get('varieties_id', False),
            'group_progress_id' : group_progress_id,
        }
        new_location = False
        location = super(plantation_indirect_cost, self).create(values)
        if location:
            new_location = self.env['lhm.location'].create(location_values)
        if new_location:
            location.location_id = new_location.id
        return location

    def write(self, values):
        if 'name' in values and self.location_id:
            self.location_id.write({'name' : values.get('name',False)})
        if 'code' in values and self.location_id:
            self.location_id.write({'code' : values.get('code',False)})
        if 'location_type_id' in values and self.location_id:
            self.location_id.write({'type_id' : values.get('location_type_id',False)})
        if 'varieties_id' in values and self.location_id:
            self.location_id.write({'varieties_id' : values.get('varieties_id',False)})
        if 'group_progress_id' in values and self.location_id:
            self.location_id.write({'group_progress_id' : values.get('group_progress_id',False)})
        if 'active' in values and self.location_id:
            self.location_id.write({'active' : values.get('active',False)})
        return super(plantation_indirect_cost, self).write(values)

    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        location = super(plantation_indirect_cost, self).unlink()
        return location
################################################# End Master Indirect Cost ##################################################
####################################################### Master Utility ######################################################
class lhm_utility(models.Model):
    _name           = 'lhm.utility'
    _description    = 'LHM Utility Management'

    def _default_location_type(self):
        location_type_ids = False
        if self._context.get('default_type',False):
            type    = self._context.get('default_type')
            if type == 'ws':
                location_type_ids   = self.env['lhm.location.type'].search([('workshop','=',True)])
            elif type == 'vh':
                location_type_ids   = self.env['lhm.location.type'].search([('vehicle','=',True)])
            elif type == 'ma':
                location_type_ids   = self.env['lhm.location.type'].search([('machine','=',True)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False

    name                = fields.Char("Name")
    code                = fields.Char("Code")
    location_id         = fields.Many2one("lhm.location", string="Lokasi")
    location_type_id    = fields.Many2one("lhm.location.type", string="Type Lokasi", ondelete="restrict", default=_default_location_type)
    group_progress_id   = fields.Many2one("plantation.location.reference", string="Grouping LPPH")
    reg_number          = fields.Char("Nomor Polisi")
    asset_id            = fields.Many2one('account.asset.asset', string='Asset', ondelete="restrict")
    ownership           = fields.Selection([('inventory', 'Inventaris'), ('rental', 'Rental')], string='Kepemilikan', default='inventory')
    partner_id          = fields.Many2one('res.partner', 'Vendor')
    uom_performance     = fields.Selection([('km', 'KM'), ('hm', 'HM')], string='Satuan', default='km')
    type                = fields.Selection([('ws', 'Workshop'), ('vh', 'Vehicle'), ('ma', 'Machine')], string='Type')
    responsible_id      = fields.Many2one("hr.employee", string="PIC", ondelete="restrict")
    date_purchase       = fields.Date(string="Tanggal Pembelian")
    date_approve        = fields.Date(string="Tanggal Pengesahan")
    approve_by          = fields.Many2one("hr.employee", string="Disahkan Oleh", ondelete="restrict")
    active              = fields.Boolean("Active", default=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_location_type = self.search(domain + args, limit=limit)
        return lhm_location_type._name_get()

    @api.model
    def create(self, values):
        location_name       = values.get('name', False)
        location_code       = values.get('code', False)
        location_type_id    = values.get('location_type_id', False)
        group_progress_id   = values.get('group_progress_id', False)
        location_values     = {
            'name'              : location_name or "(NoName)",
            'code'              : location_code or "(NoCode)",
            'type_id'           : location_type_id or False,
            'group_progress_id' : group_progress_id,
        }
        new_location = False
        location = super(lhm_utility, self).create(values)
        if location:
            new_location = self.env['lhm.location'].create(location_values)
        if new_location:
            location.location_id = new_location.id
        return location

    def write(self, values):
        if 'name' in values and self.location_id:
            self.location_id.write({'name': values.get('name', False)})
        if 'code' in values and self.location_id:
            self.location_id.write({'code': values.get('code', False)})
        if 'location_type_id' in values and self.location_id:
            self.location_id.write({'type_id': values.get('location_type_id', False)})
        if 'group_progress_id' in values and self.location_id:
            self.location_id.write({'group_progress_id' : values.get('group_progress_id',False)})
        if 'active' in values and self.location_id:
            self.location_id.write({'active': values.get('active', False)})
        return super(lhm_utility, self).write(values)

    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        location = super(lhm_utility, self).unlink()
        return location
################################################### End Of Master Utility ###################################################
##################################################### Master Blok Tanah #####################################################
class lhm_land_block(models.Model):
    _name           = 'lhm.land.block'
    _description    = 'Blok Tanah'

    name        = fields.Char("Name")
    code        = fields.Char("Code")
    active      = fields.Boolean("Active", default=True)
    company_id  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_location_type = self.search(domain + args, limit=limit)
        return lhm_location_type._name_get()
############################################### End Of Master Blok Tanah ####################################################
################################################# Master Quality Pabrik #####################################################
class lhm_quality_pabrik(models.Model):
    _name = 'lhm.quality.pabrik'
    _description = 'Quality Pabrik'

    name = fields.Char("Quality", required=True)
    code = fields.Char("Kode Quality", required=True)
    active = fields.Boolean("Active", default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    def name_get(self):
        result = []
        for record in self:
            name = record.name or ''
            code = record.code or ''
            name_display = code if code else name
            result.append((record.id, name_display))
        return result

    def _name_get(self):
        result = []
        for record in self:
            name = record.name or ''
            code = record.code or ''
            name_display = f"{code} - {name}" if code else name
            result.append((record.id, name_display))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_quality_pabrik = self.search(domain + args, limit=limit)
        return lhm_quality_pabrik.name_get()
############################################# End Of Master Quality Pabrik ####################################################
#################################################### Master Infrastruktur ###################################################
class lhm_infrastruktur(models.Model):
    _name           = 'lhm.infrastruktur'
    _description    = 'LHM Infrastruktur'

    def _default_location_type(self):
        location_type_ids = self.env['lhm.location.type'].search([('infrastruktur', '=', True)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False

    name                    = fields.Char("Deskripsi")
    location_id             = fields.Many2one("lhm.location", string="Lokasi")
    location_type_id        = fields.Many2one("lhm.location.type", string="Tipe Lokasi", ondelete="restrict", default=_default_location_type)
    location_subtype_id     = fields.Many2one("lhm.sub.location.type", string="Subtipe", ondelete="restrict")
    group_progress_id       = fields.Many2one("plantation.location.reference", string="Grouping LPPH")
    code                    = fields.Char("Kode")
    afdeling_id             = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict")
    length                  = fields.Float("Panjang")
    width                   = fields.Float("Lebar")
    satuan_id               = fields.Many2one("uom.uom", string="Satuan", ondelete="restrict")
    volume                  = fields.Float("Volume")
    date_finished           = fields.Date("Tanggal Selesai")
    development_value       = fields.Float("Biaya")
    active_rm               = fields.Boolean("Active RM", default=False)
    charge_type             = fields.Selection([('op', 'Oil Palm'), ('gc', 'General Charge'), ('idc', 'Indirect Cost')], string='Tipe Pembebanan')
    charge_op_id            = fields.Many2one("lhm.land.block", string="Charge Oil Palm")
    # charge_gc_id            = fields.Many2one("account.cost.center", string="Charge General Charge")
    charge_idc_id           = fields.Many2one("res.afdeling", string="Charge Indirect Cost")

    beban_infras_account_id = fields.Many2one('account.account', 'Beban Infrastruktur (Default)', \
        help='Akun ini akan digunakan sebagai akun Beban ketika Running Account dan dilawankan pada Kontra Akun Infrastruktur')
    tm_beban_infras_account_id = fields.Many2one('account.account', 'Beban Infrastruktur (Oil Palm Blok TM)', \
        help='Terkhusus pada Pembebanan Oil Palm, akun ini akan digunakan apabila Status Blok Tanam telah menjadi Tanaman Menghasilkan. \n \
            Jika akun ini kosong maka Pembebanan Oil Palm akan masuk ke akun pertama Beban Infrastruktur')
    counterpart_expense_account_id = fields.Many2one('account.account', 'Kontra Beban Infrastruktur', 
        help='Akun ini akan digunakan sebagai lawan akun Beban Infrastruktur')
    active                  = fields.Boolean("Active", default=True)
    company_id              = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, values):
        location_name       = values.get('name', False)
        location_code       = values.get('code', False)
        location_type_id    = values.get('location_type_id', False)
        group_progress_id   = values.get('group_progress_id', False)
        location_values     = {
            'name': location_name or "(NoName)",
            'code': location_code or "(NoCode)",
            'type_id': location_type_id or False,
            'group_progress_id': group_progress_id,
        }
        new_location    = False
        location        = super(lhm_infrastruktur, self).create(values)
        if location:
            new_location = self.env['lhm.location'].create(location_values)
        if new_location:
            location.location_id = new_location.id
        return location

    def write(self, values):
        if 'name' in values and self.location_id:
            self.location_id.write({'name': values.get('name', False)})
        if 'code' in values and self.location_id:
            self.location_id.write({'code': values.get('code', False)})
        if 'location_type_id' in values and self.location_id:
            self.location_id.write({'type_id': values.get('location_type_id', False)})
        if 'group_progress_id' in values and self.location_id:
            self.location_id.write({'group_progress_id' : values.get('group_progress_id',False)})
        if 'active' in values and self.location_id:
            self.location_id.write({'active': values.get('active', False)})
        return super(lhm_infrastruktur, self).write(values)

    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        location = super(lhm_infrastruktur, self).unlink()
        return location

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_location_type = self.search(domain + args, limit=limit)
        return lhm_location_type._name_get()
################################################ End Of Master Infrastruktur ################################################
###################################################### Master Project #######################################################
class lhm_project_type(models.Model):
    _name           = 'lhm.project.type'
    _description    = 'LHM Project Category'

    name = fields.Char('Name', required=True)
    account_id = fields.Many2one('account.account', 'Expense Account', required=True)

class lhm_project(models.Model):
    _name           = 'lhm.project'
    _description    = 'LHM Project'

    def _default_location_type(self):
        location_type_ids = self.env['lhm.location.type'].search([('project', '=', True)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False

    def _default_dest_location_type(self):
        location_type_ids = self.env['lhm.location.type'].search([('project', '=', False)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False

    @api.model
    def _get_user_currency(self):
        currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id
        return currency_id or self.company_id.currency_id

    # @api.depends('line_ids.value', 'line_ids.vat')
    # def _compute_project_value(self):
    #     total_vat   = 0
    #     total_value = 0
    #     for line in self.line_ids:
    #         if line.vat >= 1 and line.value >=1:
    #             total_vat += (line.vat * line.value)/100
    #         if line.value:
    #             total_value += line.value
    #     self.project_value  = total_value
    #     self.project_ppn    = total_vat
    #     self.project_nett   = total_vat + total_value

    name                    = fields.Char("Deskripsi")
    code                    = fields.Char("Nomor Project")
    afdeling_id             = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict")
    location_id             = fields.Many2one("lhm.location", string="Lokasi", copy=False)
    location_type_id        = fields.Many2one("lhm.location.type", string="Tipe Lokasi Project", ondelete="restrict", default=_default_location_type)
    dest_location_type_id   = fields.Many2one("lhm.location.type", string="Tipe Lokasi Tujuan", ondelete="restrict", default=_default_dest_location_type)
    location_code           = fields.Char("Kode Lokasi", related="location_id.code")
    executor                = fields.Selection([('swakelola', 'Swakelola'), ('contractor', 'Kontraktor')], string='Pelaksana')
    pk_number               = fields.Char("Nomor PK", copy=False)
    date_start              = fields.Date("Tanggal Mulai", copy=False)
    date_finished           = fields.Date("Tanggal Selesai", copy=False)
    qty                     = fields.Float("Qty")
    satuan_id               = fields.Many2one("uom.uom", string="Satuan", ondelete="restrict")
    project_value           = fields.Float("Nilai", compute="_compute_project_value", store=False)
    project_ppn             = fields.Float("PPN", compute="_compute_project_value", store=False)
    project_nett            = fields.Float("Nilai Nett", compute="_compute_project_value", store=False)
    date_issue              = fields.Date("Tanggal Terbit", copy=False)
    active                  = fields.Boolean("Active", default=True)
    note                    = fields.Text("Catatan")
    line_ids                = fields.One2many('lhm.project.line', 'project_id', string="Detail Project")
    group_progress_id       = fields.Many2one("plantation.location.reference", string="Grouping LPPH")
    currency_id             = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self._get_user_currency())
    company_id              = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    state                   = fields.Selection(selection=[('draft','New'),('cancel','Cancelled'),('in_progress','Progress'),('done','Done')],
                                                string='Status', copy=False, default='draft', index=False, readonly=False,
                                                help="* New: Project baru.\n"
                                                    "* Cancelled: Project Dibatalkan.\n"
                                                    "* Progress: Project sedang dalam Proses.\n"
                                                    "* Done: Project Sudah Selesai. \n")
    categ_id                = fields.Many2one('lhm.project.type', 'Kategory')

    varieties_id        = fields.Many2one('plant.varieties', string='Varietas', copy=False)
    activity_ids            = fields.One2many('lhm.activity', 'project_id', string="Detail Aktivitas", )

    @api.onchange('activity_ids')
    def _onchange_activity_ids(self):
        if not self.activity_ids:
            self.line_ids = [(5, 0, 0)]
            return

        self.line_ids = [(5, 0, 0)]

        line_data = [(0, 0, {
            'project_id': self.id,
            'activity_id': activity.id,
        }) for activity in self.activity_ids]

        self.line_ids = line_data

    def button_progress(self):
        for project in self:
            if not project.location_id:
                location_name       = project.code
                location_code       = project.name
                location_type_id    = project.location_type_id
                location_values     = {
                    'name'      : location_name or "(NoName)",
                    'code'      : location_code or "(NoCode)",
                    'type_id'   : location_type_id and location_type_id.id or False,
                }
                new_location = project.env['lhm.location'].create(location_values)
                if new_location:
                    project.location_id = new_location.id
            else:
                project.location_id.write({'active': True})
            project.state = 'in_progress'
        return True

    def button_cancel(self):
        for project in self:
            if project.location_id:
                project.location_id.write({'active': False})
            project.state = 'cancel'
        return True

    def button_draft(self):
        if self.location_id:
            self.location_id.write({'active': False})
        self.state = 'draft'

    def button_done(self):
        if self.location_id:
            self.location_id.write({'active': True})
        self.state = 'done'

    # Error karena field subtype_project_id tidak terdapat di model ini
    @api.onchange('location_type_id')
    def onchange_attendance_id(self):
        res = {}
        # if self.location_type_id:
        #     self.subtype_project_id = False
        # return res

    # @api.model
    # def create(self, values):
    #     location_name       = values.get('name', False)
    #     location_code       = values.get('code', False)
    #     location_type_id    = values.get('location_type_id', False)
    #     location_values     = {
    #         'name'      : location_name or "(NoName)",
    #         'code'      : location_code or "(NoCode)",
    #         'type_id'   : location_type_id or False,
    #     }
    #     new_location = False
    #     location = super(lhm_project, self).create(values)
    #     if location:
    #         new_location = self.env['lhm.location'].create(location_values)
    #     if new_location:
    #         location.location_id = new_location.id
    #     return location
    #
    def write(self, values):
        if 'name' in values and self.location_id:
            self.location_id.write({'name': values.get('name', False)})
        if 'code' in values and self.location_id:
            self.location_id.write({'code': values.get('code', False)})
        if 'location_type_id' in values and self.location_id:
            self.location_id.write({'type_id': values.get('location_type_id', False)})
        if 'varieties_id' in values and self.location_id:
            self.location_id.write({'varieties_id': values.get('varieties_id', False)})
        if 'active' in values and self.location_id:
            self.location_id.write({'active': values.get('active', False)})
        return super(lhm_project, self).write(values)

    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        location = super(lhm_project, self).unlink()
        return location

class lhm_project_line(models.Model):
    _name           = 'lhm.project.line'
    _description    = 'LHM Project Line'

    name            = fields.Char("Deskripsi", related="activity_id.name")
    activity_id     = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    vat             = fields.Float("PPN(%)")
    value           = fields.Float("Nilai")
    project_id      = fields.Many2one("lhm.project", string="Project", ondelete="cascade")
################################################### End Of Master Project ###################################################
############################################## Master Berat Janjang Rata-Rata ###############################################
class lhm_bjr(models.Model):
    _name           = 'lhm.bjr'
    _description    = 'LHM BJR'

    name        = fields.Char("Name", related="block_id.name", readonly=True)
    date        = fields.Date("Berlaku Mulai Tanggal", required=False)
    block_id    = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    value       = fields.Float('Penetapan BJR')
    company_id  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active      = fields.Boolean("Active", default=True)
########################################### End Of Master Berat Janjang Rata-Rata ###########################################
#---------------------------------------------------------------------------------------------------------------------------#
#############################################################################################################################
#
#   This is for Transaction Models
#
#############################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------#

################################################## Transaction Buku Mesin ###################################################
class lhm_machine(models.Model):
    _name           = 'lhm.machine'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = 'Buku Mesin'

    def _default_account_period_id(self):
        date        = time.strftime('%Y-%m-%d')
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
                # Plantation, GC, IDC, PJ, NS => True (artinya wajib diisi)
                validator = line.location_type_id.code in ('FC','GC','IDC', 'PJ', 'NS')
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
                if line.location_type_id.code in ('GC','MC','LB'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'lhm_machine_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
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
################################################ Transaction Buku Kendaraan #################################################
class lhm_vehicle(models.Model):
    _name           = 'lhm.vehicle'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = 'Buku Kendaraan'

    def _default_account_period_id(self):
        date        = time.strftime('%Y-%m-%d')
        period_id   = self.env['account.period'].search([('date_start', '<=', date),
                                                         ('date_stop', '>=', date),
                                                         ('special', '=', False)])
        period      = False
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
        doc_id = self.env['res.doc.type'].search([('code', '=', 'bk')], limit=1)
        return doc_id and doc_id.id or False

    def _default_state(self):
        doc_id = self.env['res.doc.type'].search([('code', '=', 'bk')], limit=1)
        if doc_id and doc_id.approval:
            state = 'draft'
        else:
            state = 'confirmed'
        return state


    name                = fields.Char('Nama', required=False)
    vehicle_id          = fields.Many2one("lhm.utility", string="Kendaraan", ondelete="restrict", domain="[('type','=', 'vh')]")
    doc_type_id         = fields.Many2one("res.doc.type", string="Document Type", ondelete="restrict", tracking=True, default=_default_doc_id)
    approval            = fields.Boolean(string="Approval", related="doc_type_id.approval", readonly=1)
    vehicle_code        = fields.Char('Kode', readonly=True, related="vehicle_id.code", store=True)
    account_period_id   = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", tracking=True, default=_default_account_period_id)
    date_start          = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop           = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    reg_number          = fields.Char("Nomor Polisi", readonly=True, related="vehicle_id.reg_number", store=True)
    uom_performance     = fields.Selection([('km', 'KM'), ('hm', 'HM')], string='Satuan', readonly=True, related="vehicle_id.uom_performance", store=True)
    operating_unit_id   = fields.Many2one('operating.unit', string='Operating Unit', compute='_compute_operating_unit_id', readonly=True, store=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    line_ids            = fields.One2many('lhm.vehicle.line', inverse_name='lhm_vehicle_id', string="Detail Buku Kendaraan", )
    user_id             = fields.Many2one('res.users', string='Penanggung Jawab', index=True, tracking=True, default=lambda self: self.env.user)
    state               = fields.Selection([
                                ('draft', 'New'), ('cancel', 'Cancelled'),
                                ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                                copy=False, default=_default_state, index=True, readonly=True,
                                help="* New: Dokumen Baru.\n"
                                     "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                     "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                     "* Done: Dokumen Sudah Selesai Diproses. \n")

    @api.onchange('vehicle_id','account_period_id')
    def onchange_validate(self):
        if self.vehicle_id and self.account_period_id:
            other_ids = self.env['lhm.vehicle'].search([('id', '!=', self._origin.id), ('account_period_id', '=', self.account_period_id.id), ('vehicle_id', '=', self.vehicle_id.id)])
            if other_ids:
                self.account_period_id  = False
                self.vehicle_id         = False
                return {
                    'warning'   : {'title': _('Kesalahan Input Data'),
                                    'message': _("Dokumen sudah ada: %s.") % other_ids[-1].name, },
                }

    def unlink(self):
        for vehicle in self:
            if vehicle.state not in ['draft'] and self.doc_type_id.approval == True:
                raise UserError(_('Status dokumen Buku Kendaraan dengan nomor %s adalah %s.\n'
                                  'Buku Kendaraan hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (vehicle.name, vehicle.state.title()))
        vehicle = super(lhm_vehicle, self).unlink()
        return vehicle

    def button_confirm(self):
        self.state = 'confirmed'

    def button_draft(self):
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, values):
        vehicle     = self.env['lhm.utility'].search([('id', '=', values.get('vehicle_id'))])
        period_id   = self.env['account.period'].search([('id', '=', values.get('account_period_id'))])
        if period_id:
            month           = period_id.date_start.strftime('%m')
            year            = period_id.date_start.strftime('%Y')
            values['name']  = (vehicle.code or "") + "/" + year + "-" + month
        else:
            values['name'] = (vehicle.code or "") + "/"
        return super(lhm_vehicle, self).create(values)

    def write(self, values):
        vehicle     = self.env['lhm.utility'].search([('id', '=', values.get('vehicle_id', self.vehicle_id.id))])
        period_id   = self.env['account.period'].search([('id', '=', values.get('account_period_id', self.account_period_id.id))])
        if period_id:
            month             = period_id.date_start.strftime('%m')
            year              = period_id.date_start.strftime('%Y')
            values['name']    = (vehicle.code or "") + "/" + year + "-" + month
        return super(lhm_vehicle, self).write(values)

class lhm_vehicle_line(models.Model):
    _name           = 'lhm.vehicle.line'
    _description    = 'LHM Vehicle Line'

    @api.depends("start_value", "end_value")
    def  _compute_difference(self):
        for diff in self:
            diff.difference_value = diff.end_value - diff.start_value

    @api.depends("location_type_id","location_id")
    def _get_doc_activity_ids(self):
        for line in self:
            activity_list = []
            doc_id      = self.env['res.doc.type'].search([('code', '=', 'bk')], limit=1)
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

    @api.depends("activity_id")
    def _get_charge_activity_ids(self):
        for line in self:
            if line.activity_id and line.activity_id.charge_ids:
                line.filter_charge_ids = [(6, 0, [x.id for x in line.activity_id.charge_ids])]
            else:
                line.filter_charge_ids = []

    name                = fields.Char("Nama", readonly=True, related="lhm_vehicle_id.name", store=True)
    date                = fields.Date("Tanggal", required=True)
    use_hours           = fields.Float("Jam Kerja")
    start_value         = fields.Float("km/hm Berangkat")
    end_value           = fields.Float("km/hm Kembali")
    difference_value    = fields.Float("km/hm Terpakai", compute="_compute_difference", store=True)
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
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
    filtered_locations  = fields.Many2many('lhm.location', 'lhm_vh_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    filtered_activities = fields.Many2many('lhm.activity', 'lhm_vh_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    doc_activity_ids    = fields.Many2many('lhm.activity', store=True, compute=_get_doc_activity_ids)
    sub_activity_id     = fields.Many2one("lhm.activity", string="Sub Aktivitas", ondelete="restrict")
    performance1        = fields.Float("Prestasi")
    uom_performance1_id = fields.Many2one("uom.uom", string="Satuan 1", ondelete="restrict")
    performance2        = fields.Float("Prestasi 2")
    uom_performance2_id = fields.Many2one("uom.uom", string="Satuan 2", ondelete="restrict")
    filter_charge_ids   = fields.Many2many('lhm.charge.type', store=True, compute=_get_charge_activity_ids)
    charge_id           = fields.Many2one("lhm.charge.type", string="Muatan", ondelete="restrict")
    value_charge        = fields.Float("Vol. Muatan")
    uom_charge_id       = fields.Many2one("uom.uom", string="Satuan Muatan", ondelete="restrict")
    lhm_vehicle_id      = fields.Many2one("lhm.vehicle", string="Buku Kendaraan", ondelete="cascade")

    @api.depends('varieties_id','location_type_id', 'lhm_vehicle_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.lhm_vehicle_id.state!='draft':
                line.filtered_locations = []
            else:
                if line.location_type_id.code in ('MA','GC','MC','LB'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'lhm_vehicle_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.lhm_vehicle_id.state!='draft':
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','bk')], limit=1)
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
    
    @api.model
    def default_get(self, default_fields):
        #default_get should only do the following:
        #   -propose the next amount in start_value in order to reduce user input mistake
        lhm_vehicle_obj = self.env['lhm.vehicle']
        period_obj = self.env['account.period']
        context = self._context

        data = super(lhm_vehicle_line, self).default_get(default_fields)
        if not context.get('line_ids') and context.get('vehicle_id') and context.get('period_id'):
            period = period_obj.browse(context.get('period_id'))
            prev_lhm = self.search([('lhm_vehicle_id.vehicle_id', '=', context['vehicle_id']),
                                                       ('lhm_vehicle_id.state', 'in', ['done','confirmed']),
                                                       ('date','<=',period.date_start)],
                                                       order='date desc', limit=1)
            if prev_lhm:
                last_end_value = prev_lhm.end_value
                default_date = period.date_start

                data['start_value'] = last_end_value
                data['date'] = default_date
        elif context.get('line_ids'):
            line_ids = context.get('line_ids')
            if isinstance(line_ids, list):
                if all(isinstance(i, tuple) and len(i) == 3 for i in line_ids):
                    lines_with_values = [x[2] for x in line_ids if x[0] == 0]
                    last_end_value = max([x['end_value'] for x in lines_with_values if 'end_value' in x])
                    default_date = max([x['date'] for x in lines_with_values if 'date' in x])

                    data['start_value'] = last_end_value
                    data['date'] = default_date
        return data
        # elif context.get('line_ids'):
        #     line_dict = lhm_vehicle_obj.resolve_2many_commands('line_ids', context.get('line_ids'))
        #     last_end_value = max([x['end_value'] for x in line_dict])
        #     default_date = max([x['date'] for x in line_dict])

        #     data['start_value'] = last_end_value
        #     data['date'] = default_date
        # return data

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            self.uom_performance1_id = self.activity_id.uom_id and self.activity_id.uom_id.id or False
            self.uom_performance2_id = self.activity_id.uom2_id and self.activity_id.uom2_id.id or False
            self.charge_id = self.activity_id.charge_ids and  self.activity_id.charge_ids[0].id or False
            self.uom_charge_id = self.activity_id.charge_ids and  self.activity_id.charge_ids[0].uom_id.id or False

    @api.onchange('location_type_id')
    def _onchange_location_type_id(self):
        if self.location_type_id:
            self.location_id        = False
            self.activity_id        = False
            self.sub_activity_id    = False
            self.varieties_id = self.location_type_id.varieties_id.id

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.activity_id        = False
            self.sub_activity_id    = False

    @api.constrains('date')
    def _check_date_unique(self):
        for rec in self:
            rec._check_date_line()

    def _check_date_line(self):
        if not (self.date >= self.lhm_vehicle_id.account_period_id.date_start and self.date <= self.lhm_vehicle_id.account_period_id.date_stop):
            month = [item for item in BULAN_INDONESIA if item[0] == str(fields.Date.from_string(self.lhm_vehicle_id.account_period_id.date_start).month)][0][1]
            raise UserError(_('Tanggal %s pada Buku Kendaraan tidak dalam periode %s %s.\n'
                              'Ubah tanggal atau hapus baris di Daftar Buku Kendaraan') % (
                                self.date, month, str(fields.Date.from_string(self.lhm_vehicle_id.account_period_id.date_start).year)))
        # domain = [('date', '=', self.date)]
        # if self.search_count(domain) > 1:
        #     raise UserError(_('Tidak boleh ada tanggal yang sama.\n'
        #                       'Tanggal: %s') % self.date)
        return True
############################################ End Of Transaction Buku Kendaraan ##############################################
################################################ Transaction Buku Workshop ##################################################
class lhm_workshop(models.Model):
    _name           = 'lhm.workshop'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = 'Buku Workshop'

    def _default_account_period_id(self):
        date        = time.strftime('%Y-%m-%d')
        period_id   = self.env['account.period'].search([('date_start', '<=', date),
                                                       ('date_stop', '>=', date),
                                                       ('special', '=', False)])
        period = False
        if period_id and len(period_id) > 1:
            period = period_id[-1]
        elif period_id and len(period_id) == 1:
            period = period_id
        return period and period.id or False

    @api.depends('user_id')
    def _compute_operating_unit_id(self):
        for plantation_transaction in self:
            if plantation_transaction.user_id:
                plantation_transaction.operating_unit_id = plantation_transaction.user_id.default_operating_unit_id

    def _default_doc_id(self):
        doc_id = self.env['res.doc.type'].search([('code', '=', 'bw')], limit=1)
        return doc_id and doc_id.id or False

    def _default_state(self):
        doc_id = self.env['res.doc.type'].search([('code', '=', 'bw')], limit=1)
        if doc_id and doc_id.approval:
            state = 'draft'
        else:
            state = 'confirmed'
        return state

    name                = fields.Char('Nama', required=False)
    workshop_id         = fields.Many2one("lhm.utility", string="Workshop", ondelete="restrict", domain="[('type','=', 'ws')]")
    workshop_code       = fields.Char('Kode', readonly=True, related="workshop_id.code", store=True)
    doc_type_id         = fields.Many2one("res.doc.type", string="Document Type", ondelete="restrict", tracking=True, default=_default_doc_id)
    account_period_id   = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", tracking=True, default=_default_account_period_id)
    date_start          = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop           = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    approval            = fields.Boolean(string="Approval", related="doc_type_id.approval", readonly=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    operating_unit_id   = fields.Many2one('operating.unit', string='Operating Unit', compute='_compute_operating_unit_id', readonly=True, store=True)
    line_ids            = fields.One2many('lhm.workshop.line', inverse_name='lhm_workshop_id', string="Detail Buku Workshop", )
    note                = fields.Text("Catatan")
    user_id             = fields.Many2one('res.users', string='Penanggung Jawab', index=True, tracking=True, default=lambda self: self.env.user)
    state               = fields.Selection([
                            ('draft', 'New'), ('cancel', 'Cancelled'),
                            ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                            copy=False, default=_default_state, index=True, readonly=True,
                            help="* New: Dokumen Baru.\n"
                                 "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                 "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                 "* Done: Dokumen Sudah Selesai Diproses. \n")

    @api.onchange('workshop_id','account_period_id')
    def onchange_validate(self):
        if self.workshop_id and self.account_period_id:
            other_ids = self.env['lhm.workshop'].search([('id', '!=', self._origin.id), ('account_period_id', '=', self.account_period_id.id), ('workshop_id', '=', self.workshop_id.id)])
            if other_ids:
                self.account_period_id  = False
                self.workshop_id        = False
                return {
                    'warning': {'title': _('Kesalahan Input Data'),
                                'message': _("Dokumen sudah ada: %s.") % other_ids.name, },
                }

    def unlink(self):
        for workshop in self:
            if workshop.state not in ['draft'] and self.doc_type_id.approval == True:
                raise UserError(_('Status dokumen Buku Workshop dengan nomor %s adalah %s.\n'
                                  'Buku Workshop hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (
                                   workshop.name, workshop.state.title()))
        workshop = super(lhm_workshop, self).unlink()
        return workshop

    def button_confirm(self):
        self.state = 'confirmed'

    def button_draft(self):
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, values):
        workshop    = self.env['lhm.utility'].search([('id', '=', values.get('workshop_id'))])
        period_id   = self.env['account.period'].search([('id', '=', values.get('account_period_id'))])
        if period_id:
            month             = period_id.date_start.strftime('%m')
            year              = period_id.date_start.strftime('%Y')
            values['name']  = (workshop.code or "") + "/" + year + "-" + month
        else:
            values['name']  = (workshop.code or "") + "/"
        return super(lhm_workshop, self).create(values)

    def write(self, values):
        workshop    = self.env['lhm.utility'].search([('id', '=', values.get('workshop_id', self.workshop_id.id))])
        period_id   = self.env['account.period'].search([('id', '=', values.get('account_period_id', self.account_period_id.id))])
        if period_id:
            month             = period_id.date_start.strftime('%m')
            year              = period_id.date_start.strftime('%Y')
            values['name']  = (workshop.code or "") + "/" + year + "-" + month
        return super(lhm_workshop, self).write(values)

class lhm_workshop_line(models.Model):
    _name           = 'lhm.workshop.line'
    _description    = 'LHM Workshop Line'

    @api.depends("location_type_id","location_id")
    def _get_doc_activity_ids(self):
        for line in self:
            activity_list = []
            doc_id      = self.env['res.doc.type'].search([('code', '=', 'bw')], limit=1)
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

            if not line.doc_activity_ids:
                line.doc_activity_ids = [(6, 0, [])]

    name                = fields.Char("Nama", readonly=True, related="lhm_workshop_id.name", store=True)
    date                = fields.Date("Tanggal", )
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
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
    filtered_locations  = fields.Many2many('lhm.location', 'lhm_ws_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    doc_activity_ids    = fields.Many2many('lhm.activity', store=True, compute=_get_doc_activity_ids)
    filtered_activities = fields.Many2many('lhm.activity', 'lhm_ws_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    use_hours           = fields.Float("Jam Kerja")
    lhm_workshop_id     = fields.Many2one("lhm.workshop", string="Buku Workshop", ondelete="cascade")

    @api.depends('varieties_id','location_type_id', 'lhm_workshop_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.lhm_workshop_id.state!='draft':
                line.filtered_locations = []
            else:
                if line.location_type_id.code in ('VH','MA','GC','MC','LB'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
                else: # PLANTATION, PJ, NS
                    locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id', 'lhm_workshop_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.lhm_workshop_id.state!='draft':
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','bw')], limit=1)
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

    @api.constrains('date','location_id','activity_id', 'lhm_workshop_id')
    def _check_date_unique(self):
        for rec in self:
            rec._check_date_line()

    def _check_date_line(self):
        if not (self.date >= self.lhm_workshop_id.account_period_id.date_start and self.date <= self.lhm_workshop_id.account_period_id.date_stop):
            month = [item for item in BULAN_INDONESIA if item[0] == str(fields.Date.from_string(self.lhm_workshop_id.account_period_id.date_start).month)][0][1]
            raise UserError(_('Tanggal %s pada Buku Workshop tidak dalam periode %s %s.\n'
                              'Ubah tanggal atau hapus baris di Daftar Buku Workshop') % (
                            self.date, month, str(fields.Date.from_string(self.lhm_workshop_id.account_period_id.date_start).year)))
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
        if total_domain == 3 and self.search_count(domain) > 1:
            raise UserError(_('Terjadi Duplikasi Data!!!!.\n'
                              'Tanggal          : %s.\n'
                              'Kode Lokasi      : %s.\n'
                              'Kode Aktivitas   : %s.\n'
                              'Ganti salah satu detail atau hapus baris yang sama') % (self.date, self.location_id.code, self.activity_id.code))
        return True
############################################ End Of Transaction Buku Workshop ###############################################

############################################### Transaction Nota Angkut Panen ################################################
class lhm_nab(models.Model):
    _name           = 'lhm.nab'
    _description    = 'Nota Angkut Panen'

    @api.depends('timbang_ksg_kbn', 'timbang_isi_kbn', 'timbang_isi_pks', 'timbang_ksg_pks', 'grading')
    def _compute_timbang(self):
        self.timbang_tara_kbn = self.timbang_isi_kbn - self.timbang_ksg_kbn
        self.timbang_tara_pks = self.timbang_isi_pks - self.timbang_ksg_pks
        self.netto = self.timbang_isi_pks - self.timbang_ksg_pks - self.grading

    @api.depends('line_ids')
    def _compute_janjang(self):
        if self.line_ids:
            total_janjang = 0
            for line_nab in self.line_ids:
                total_janjang = total_janjang + line_nab.qty_nab
            self.janjang_jml = total_janjang

    @api.depends('date_nab', 'state')
    def _compute_account_period_id(self):
        for plantation_nab in self:
            if plantation_nab.date_nab:
                period_id = self.env['account.period'].search([('date_start', '<=', plantation_nab.date_nab), ('date_stop', '>=', plantation_nab.date_nab), ('special', '=', False)])
                if period_id:
                    plantation_nab.account_period_id = period_id

    name                = fields.Char('No. Register', required=False)
    date_nab            = fields.Date("Tanggal", readonly=True, states={'draft': [('readonly',False)]})
    account_period_id   = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", compute='_compute_account_period_id', store=True)
    date_start          = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop           = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    no_nab              = fields.Char('No. NAB Manual', readonly=True, states={'draft': [('readonly',False)]})
    afdeling_id         = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    driver              = fields.Char('Nama Supir', readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    vehicle_id          = fields.Many2one("lhm.utility", string="Kendaraan", ondelete="restrict", domain="[('type','=', 'vh')]", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    vehicle_subtitute_id= fields.Many2one("lhm.utility", "Kendaraan Pengganti", ondelete="restrict", domain="[('type','=', 'vh')]", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    reg_number          = fields.Char('Nomor Polisi', readonly=True, related="vehicle_id.reg_number", store=True)
    reg_number_subtitue = fields.Char('Nomor Polisi', readonly=True, related="vehicle_subtitute_id.reg_number", store=True)
    ownership           = fields.Selection('Kepemilikan', readonly=True, related="vehicle_id.ownership", store=True)
    ownership_subtitute = fields.Selection('Kepemilikan', readonly=True, related="vehicle_subtitute_id.ownership", store=True)
    timbang_ksg_kbn     = fields.Float('Timbangan Kosong Kebun', readonly=True, states={'draft': [('readonly',False)]})
    timbang_isi_kbn     = fields.Float('Timbangan Isi Kebun', readonly=True, states={'draft': [('readonly',False)]})
    timbang_tara_kbn    = fields.Float('Timbangan Tara', compute='_compute_timbang', store=True)
    janjang_jml         = fields.Float('Jumlah Janjang', compute='_compute_janjang', store=True)
    pks_id              = fields.Many2one("res.partner", string="Nama PKS", ondelete="restrict", readonly=True, states={'draft': [('readonly',False)]})
    date_pks            = fields.Date("Tanggal PKS", readonly=True, states={'draft': [('readonly',False)]})
    timbang_isi_pks     = fields.Float('Timbangan Isi PKS', readonly=True, states={'draft': [('readonly',False)]})
    timbang_ksg_pks     = fields.Float('Timbangan Kosong PKS', readonly=True, states={'draft': [('readonly',False)]})
    timbang_tara_pks    = fields.Float('Timbangan Tara', compute='_compute_timbang', store=True)
    afkir               = fields.Float('Afkir', readonly=True, states={'draft': [('readonly',False)]})
    grading             = fields.Float('Grading', readonly=True, states={'draft': [('readonly',False)]})
    netto               = fields.Float('Netto', compute='_compute_timbang', store=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    line_ids            = fields.One2many('lhm.nab.line', inverse_name='lhm_nab_id', string="Detail Nota Angkut Panen", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    confirmed           = fields.Boolean('Confirmed')
    cancelled           = fields.Boolean('Cancelled')
    force_edit          = fields.Boolean('Revisi')
    state               = fields.Selection(compute='_get_state', store=True, selection=[
                                ('draft', 'New'), ('cancel', 'Cancelled'),
                                ('confirmed', 'Confirmed'), ('done', 'Done'), ('revision','Revisi')], string='Status',
                                copy=False, default='draft', index=True, readonly=True,
                                help="* New: Dokumen Baru.\n"
                                     "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                     "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                     "* Done: Dokumen Sudah Selesai Diproses. \n")
    invoice_id          = fields.Many2one('account.move', 'NAB Invoice')
    plasma_invoice_id   = fields.Many2one('account.move', 'NAB Invoice Plasma')
    contractor_id       = fields.Many2one('res.partner', 'Kontraktor', readonly=True, states={'draft': [('readonly',False)], 'confirmed': [('readonly',False)], 'revision': [('readonly',False)]})
    lhm_contractor_id   = fields.Many2one('lhm.contractor', 'Contractor Book', readonly=True)
    product_id          = fields.Many2one('product.product', string="Product")
    product_qty         = fields.Integer(string="Quantity")
    uom_id              = fields.Many2one('uom.uom', string="Unit of Measure")
    quality             = fields.Integer(string="Quality")
    kebun_line_ids      = fields.One2many('timbangan.kebun', inverse_name='lhm_nab_id', string="Penamaan")
    pabrik_line_ids     = fields.One2many('timbangan.pabrik', inverse_name='lhm_nab_id', string="Penamaan")
    partner_id          = fields.Many2one('res.partner', string="Partner")
    _order = "date_nab desc"

    @api.depends('confirmed', 'invoice_id', 'invoice_id.state', 'cancelled', 'force_edit')
    def _get_state(self):
        for record in self:
            if record.confirmed:
                if record.sudo().invoice_id and record.sudo().invoice_id.state not in ('draft', 'cancel'):
                    record.state = 'done'
                else:
                    record.state = 'confirmed'
            elif record.cancelled:
                record.state = 'cancel'
            elif record.force_edit:
                record.state = 'revision'
            else:
                record.state = 'draft'

    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'vdata_panen_nab_naf')
    #     self.env.cr.execute("""
    #         CREATE OR REPLACE VIEW vdata_panen_nab_naf AS (
    #         SELECT 'panen' AS grp,
    #             lrb.tgl_panen,
    #             lpb.afdeling_id,
    #             lpb.id AS block_id,
    #             lrb.tgl_panen AS tgl_trans,
    #             sum(lrb.value) AS jjg_qty
    #         FROM lhm_restan_balance lrb
    #         LEFT JOIN lhm_plant_block lpb ON lpb.id = lrb.block_id
    #         GROUP BY lrb.tgl_panen, lpb.afdeling_id, lpb.id
    #         UNION ALL
    #         SELECT 'panen' AS grp,
    #             ltpl.date AS tgl_panen,
    #             lpb.afdeling_id,
    #             lpb.id AS block_id,
    #             ltpl.date AS tgl_trans,
    #             sum(ltpl.nilai) AS jjg_qty
    #         FROM lhm_transaction lt
    #         LEFT JOIN lhm_transaction_process_line ltpl ON lt.id = ltpl.lhm_id
    #         LEFT JOIN lhm_activity la ON la.id = ltpl.activity_id
    #         LEFT JOIN lhm_plant_block lpb ON lpb.location_id = ltpl.location_id
    #         WHERE la.is_panen = TRUE AND lt.state IN ('done', 'close')
    #         GROUP BY ltpl.date, lpb.afdeling_id, lpb.id
    #         UNION ALL
    #         SELECT 'nab' AS grp,
    #             lnl.tgl_panen,
    #             lpb.afdeling_id,
    #             lnl.block_id,
    #             ln.date_pks AS tgl_trans,
    #             - sum(lnl.qty_nab) AS jjg_qty
    #         FROM lhm_nab ln
    #         LEFT JOIN lhm_nab_line lnl ON lnl.lhm_nab_id = ln.id
    #         LEFT JOIN lhm_plant_block lpb ON lpb.id = lnl.block_id
    #         WHERE ln.state IN ('confirmed', 'done') AND lnl.block_id IS NOT NULL
    #         GROUP BY lnl.tgl_panen, lpb.afdeling_id, lnl.block_id, ln.date_pks
    #         UNION ALL
    #         SELECT 'naf' AS grp,
    #             lnal.tgl_panen,
    #             lpb.afdeling_id,
    #             lnal.block_id,
    #             lna.date_naf AS tgl_trans,
    #             - sum(lnal.qty) AS jjg_qty
    #         FROM lhm_nab_afkir lna
    #         LEFT JOIN lhm_nab_afkir_line lnal ON lnal.lhm_nab_afkir_id = lna.id
    #         LEFT JOIN lhm_plant_block lpb ON lpb.id = lnal.block_id
    #         WHERE lna.state IN ('confirmed', 'done') AND lnal.block_id IS NOT NULL
    #         GROUP BY lnal.tgl_panen, lpb.afdeling_id, lnal.block_id, lna.date_naf
    #         )
    #     """)

    @api.onchange('vehicle_id' ,'vehicle_subtitute_id')
    def onchange_vehicle(self):
        if self.vehicle_id:
            self.contractor_id = self.vehicle_id and self.vehicle_id.partner_id and self.vehicle_id.partner_id.id or False
        elif self.vehicle_subtitute_id:
            self.contractor_id = self.vehicle_subtitute_id and self.vehicle_subtitute_id.partner_id and self.vehicle_subtitute_id.partner_id.id or False

    @api.depends('confirmed', 'invoice_id', 'invoice_id.state', 'cancelled', 'force_edit')
    def _get_state(self):
        if self.confirmed:
            if self.sudo().invoice_id and self.sudo().invoice_id.state not in ('draft', 'cancel'):
                self.state = 'done'
            else:
                self.state = 'confirmed'
        elif self.cancelled:
            self.state = 'cancel'
        elif self.force_edit:
            self.state = 'revision'
        else:
            self.state = 'draft'

    def unlink(self):
        for nab in self:
            if nab.state not in ['draft']:
                raise UserError(_('Status Nota Angkut Panen dengan nomor %s adalah %s.\n'
                                  'Nota Angkut Panen hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (nab.name, nab.state.title()))
        nab = super(lhm_nab, self).unlink()
        return nab
    
    def create_material_receipt(self):
        for record in self:
            for line in record.pabrik_line_ids:
                if not line.stock_picking_id:
                    picking_vals = {
                        'partner_id': record.partner_id.id if record.partner_id else False,
                        'location_id': line.env.ref('stock.stock_location_suppliers').id,
                        'location_dest_id': line.env.ref('stock.stock_location_stock').id,
                        'move_ids_without_package': [(0, 0, {
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'product_uom_qty': line.product_qty,
                            'product_uom': line.uom_id.id,
                            'location_id': line.env.ref('stock.stock_location_suppliers').id,
                            'location_dest_id': line.env.ref('stock.stock_location_stock').id,
                        })],
                        'picking_type_id': line.env.ref('stock.picking_type_in').id,  # Receipts picking type
                    }
                    picking = line.env['stock.picking'].create(picking_vals)
                    line.stock_picking_id = picking.id
                else:
                    line.stock_picking_id.write({
                        'move_ids_without_package': [(1, line.stock_picking_id.move_ids_without_package.id, {
                            'product_uom_qty': line.product_qty,
                        })]
                    })

    def button_confirm(self):
        self.state = 'confirmed'
        # if not self.pks_id:
        #     raise UserError(_('Nama PKS masih Kosong.\n'
        #                         'Silahkan isi Nama PKS tersebut terlebih dahulu'))
        # if self.line_ids:
        #     for line in self.line_ids:
        #         if line.qty_nab <= 0 :
        #             raise UserError(_('Total NAB harus lebih dari 0.\n'
        #                         'Perbaiki data pada lokasi %s sebelum diconfirm!!')%(line.block_id.code or '-'))
        # else:
        #     raise UserError(_('Detail Nota Angkut Panen Kosong.\n'
        #                         'Silahkan isi Detail Nota Angkut Panen terlebih dahulu'))
        self.confirmed = True
        self.line_ids.link_to_lhm_progress()
        self.line_ids.allocate_nab_line_to_lhm_line()

    def button_draft(self):
        for nab in self:
            if nab.sudo().invoice_id and nab.sudo().invoice_id.state not in ('draft','cancel'):
                raise UserError(_('Anda tidak dapat meng-Cancel Nota Angkut Panen \n'
                                  'yang telah memiliki Invoice.\n'
                                  'Silahkan Cancel Invoice tersebut terlebih dahulu. Invoice : %s')%nab.invoice_id.internal_number)
            for link_lhm in nab.line_ids.mapped('lhm_line_ids'):
                link_lhm.unlink()
        self.state = 'draft'
        self.confirmed = False
        self.cancelled = False
        self.line_ids.write({'lhm_progress_ids': [(5,False,False)]})

    def button_cancel(self):
        self.state = 'cancel'
        self.confirmed = False
        self.cancelled = True

    def button_revise(self):
        for nab in self:
            for link_lhm in nab.line_ids.mapped('lhm_line_ids'):
                link_lhm.unlink()
        self.confirmed = False
        self.force_edit = True
        self.line_ids.write({'lhm_progress_ids': [(5,False,False)]})

    def button_approve_revision(self):
        self.confirmed = True
        self.force_edit = False
        self.line_ids.link_to_lhm_progress()
        self.line_ids.allocate_nab_line_to_lhm_line()

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('lhm.nab') or _('New')
        return super(lhm_nab, self).create(values)

class lhm_nab_line(models.Model):
    _name               = 'lhm.nab.line'
    _description        = 'LHM Nota Angkut Panen Line'

    @api.depends('block_id', 'tgl_panen')
    def _compute_panen(self):
        if self.block_id and self.tgl_panen:
            total_lhm       = 0
            total_nab       = 0
            if isinstance(self.id, int):
                domain = [
                    ('block_id', '=', self.block_id.id),
                    ('tgl_panen', '=', self.tgl_panen),
                    ('id', '!=', self.id)]
            else:
                domain = [
                    ('block_id', '=', self.block_id.id),
                    ('tgl_panen', '=', self.tgl_panen)]
            other_nab       = self.env['lhm.nab.line'].search(domain)
            progress_ids    = self.env['lhm.transaction.process.line'].search([('date', '=', self.tgl_panen), ('location_id', '=', self.block_id.location_id.id)])
            balance_ids     = self.env['lhm.restan.balance'].search([('tgl_panen', '=', self.tgl_panen), ('block_id', '=', self.block_id.id)])
            if balance_ids:
                for balance in balance_ids:
                    total_lhm += balance.value
            if progress_ids:
                for progress in progress_ids:
                    if progress.activity_id.is_panen:
                        total_lhm += progress.nilai
            if other_nab:
                for nab in other_nab:
                    total_nab += nab.qty_nab
            self.qty_panen_lhm  = total_lhm
            self.qty_akum_nab   = total_nab
            self.qty_sisa_panen = total_lhm - total_nab

    @api.depends('lhm_nab_id.state','lhm_line_ids','lhm_line_ids.lhm_id.state',
        'lhm_line_ids.lhm_line_id.location_id','lhm_line_ids.lhm_line_id.activity_id',
        'lhm_line_ids.lhm_line_id.work_result')
    def _check_allocation_state(self):
        for line in self:
            # total_allocation = sum(line.lhm_line_ids.mapped('nilai'))
            total_panen = sum(line.mapped('lhm_progress_ids').mapped('nilai'))
            total_allocation = 0.0
            for xline in line.lhm_line_ids:
                if xline.lhm_line_id and xline.lhm_line_id.activity_id.is_panen \
                        and xline.lhm_line_id.location_id.id==line.block_id.location_id.id:
                    total_allocation+=(xline.lhm_line_id.work_result/total_panen)*line.qty_nab
            if round(total_allocation,2) < line.qty_nab:
                line.pending_allocation = True
            else:
                line.pending_allocation = False

    name                = fields.Char('Name', related="lhm_nab_id.name", store=True)
    block_id            = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    tgl_panen           = fields.Date("Tgl. Panen")
    qty_panen_lhm       = fields.Float("Total Panen", compute="_compute_panen", store=True)
    qty_akum_nab        = fields.Float("Akumulasi NAB", compute="_compute_panen", store=True)
    qty_sisa_panen      = fields.Float("Sisa Panen", compute="_compute_panen", store=True)
    qty_nab             = fields.Float("Total NAB")
    lhm_nab_id          = fields.Many2one("lhm.nab", string="Nota Buah Angkut", ondelete="cascade")
    lhm_progress_ids    = fields.Many2many('lhm.transaction.process.line', 'lhm_process_nab_line_rel', 'nab_line_id', 'progress_id', 'LHM Progress Ref')
    lhm_line_ids        = fields.One2many('lhm.transaction.line.nab.line', 'nab_line_id', 'LHM Detail')
    pending_allocation  = fields.Boolean('Pending Allocaton', compute='_check_allocation_state', store=True)
    product_id          = fields.Many2one('product.product', string="Product")
    product_qty         = fields.Integer(string="Quantity")
    uom_id              = fields.Many2one('uom.uom', string="Unit of Measure")
    pemanen             = fields.Char(string='Pemanen')
    employee_id         = fields.Many2one("hr.employee", string="Nama", ondelete="restrict")

    def compute_weight(self):
        self.ensure_one()
        weight = 0.0
        weight = (self.qty_nab*self.block_id.with_context({'date': self.lhm_nab_id.date_pks})._get_rate_bjr()) * self.lhm_nab_id.netto \
            / sum([x.qty_nab*x.block_id.with_context({'date': self.lhm_nab_id.date_pks})._get_rate_bjr() for x in self.lhm_nab_id.line_ids])
        return weight

    def link_to_lhm_progress(self):
        for line in self:
            lhm_lines = self.env['lhm.transaction.process.line'].search([ \
                ('location_id','=',line.block_id.location_id.id), 
                ('lhm_id.state','!=','draft'), 
                ('lhm_id.date','=',line.tgl_panen), 
                ('activity_id.is_panen','=',True)
                ])
            if not lhm_lines:
                continue
            else:
                line.write({'lhm_progress_ids': [(6,0,lhm_lines.ids)]})
                #Trigger Function
                lhm_lines.write({'nab_line_ids': []})

    def allocate_nab_line_to_lhm_line(self):
        for nab_line in self.filtered(lambda x: x.pending_allocation):
            vals = []
            total_panen = sum(nab_line.mapped('lhm_progress_ids').mapped('nilai'))
            if not nab_line.mapped('lhm_progress_ids'):
                raise ValidationError(_("Tidak dapat menemukan LHM.\nSilahkan \
                        input LHM dan Progress LHMnya sebelum membuat NAB"))
            if total_panen < nab_line.qty_nab:
                raise ValidationError(_("Total Progress Panen dari LHM untuk Blok %s lebih \n \
                        sedikit dibandingkan dengan NAB yg dikeluarkan"))
                # continue
            for progress in nab_line.lhm_progress_ids:
                lhm_lines = progress.lhm_id.mapped('lhm_line_ids').filtered(lambda x: x.location_id==progress.location_id and x.activity_id==progress.activity_id and x.activity_id.is_panen)
                # total_panen = sum(lhm_lines.mapped('work_result'))
                for line in lhm_lines:
                    janjang = total_panen and (line.work_result/total_panen)*nab_line.qty_nab or 0.0
                    berat = total_panen and (line.work_result/total_panen)*nab_line.compute_weight() or 0.0
                    vals.append((0,0,{
                        'lhm_line_id': line.id,
                        'nab_line_id': nab_line.id,
                        'nilai': janjang,
                        'uom_id': line.satuan_id and line.satuan_id.id or False,
                        'nilai2': berat,
                    }))
                    # self.env['lhm.transaction.line.nab.line'].create(vals)
            if vals:
                nab_line.write({'lhm_line_ids': vals})

    @api.model
    def _cron_linked_to_nab(self):
        pending_line = self.search([('lhm_progress_ids','=',False), ('lhm_nab_id.state','not in',['draft','revision'])])
        pending_line.link_to_lhm_progress()
        pending_line = self.search([('pending_allocation','=',True), ('lhm_nab_id.state','not in',['draft','revision'])])
        pending_line.allocate_nab_line_to_lhm_line()
    
    # @api.constrains('tgl_panen', 'block_id', 'lhm_nab_id')
    # def _check_attendance_id(self):
    #     for record in self:
    #         record._check_parent_one()
	#
    # def _check_parent_one(self):
    #     if self.tgl_panen and self.block_id and self.lhm_nab_id:
    #         if isinstance(self.lhm_nab_id.id, int):
    #             domain = [
    #                 ('tgl_panen', '=', self.tgl_panen),
    #                 ('block_id', '=', self.block_id.id),
    #                 ('lhm_nab_id', '=', self.lhm_nab_id.id),
    #                 ('id','!=',self.id)]
    #             nab_line = self.search(domain)
    #             if nab_line:
    #                 raise UserError(_(
    #                     'Anda tidak dapat membuat nota angkut panen dengan nama blok %s dan tanggal %s karena terjadi duplikasi data!') % (
    #                                 self.block_id.name, self.tgl_panen))
    #     return True

    # @api.onchange('qty_sisa_panen', 'qty_nab')
    # def onchange_qty_nab(self):
    #     if self.qty_sisa_panen and self.qty_nab:
    #         if self.qty_sisa_panen < self.qty_nab:
    #             self.qty_nab = 0.00
    #             return {
    #                 'warning': {'title': _('Kesalahan Input Data'),
    #                             'message': _("Total Tidak boleh lebih besar daripada sisa")},
    #             }

################################################## Link NAB and LHM ####################################################
class lhm_transaction_line_nab_line(models.Model):
    _name = 'lhm.transaction.line.nab.line'

    lhm_line_id = fields.Many2one('lhm.transaction.line','LHM Line Ref', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', related='lhm_line_id.employee_id', string='Karyawan')
    lhm_id = fields.Many2one('lhm.transaction', related='lhm_line_id.lhm_id', string='LHM Ref', readonly=True)
    nab_line_id = fields.Many2one('lhm.nab.line','NAB Line Ref', ondelete='cascade')
    nab_id = fields.Many2one('lhm.nab', related='nab_line_id.lhm_nab_id', string='NAB Ref', readonly=True, store=True)
    nab_date = fields.Date(related='nab_id.date_nab', string='NAB Date', readonly=True, store=True)
    nab_date_pks = fields.Date(related='nab_id.date_pks', string='PKS Date', readonly=True, store=True)
    nilai = fields.Float('Nilai')
    uom_id = fields.Many2one('uom.uom', 'Satuan 1')
    nilai2 = fields.Float('Berat')
    uom_id2 = fields.Many2one('uom.uom', 'Satuan 2')

    @api.constrains('lhm_line_id', 'nab_line_id')
    def _check_double_link(self):
        check = True
        for line in self:
            if line.lhm_line_id:
                other_line = self.search([('id','!=',line.id),('lhm_line_id','=',line.lhm_line_id.id),('nab_line_id','=',line.nab_line_id.id)])
                if other_line:
                    raise ValidationError(_('Alokasi antara Detail NAB dan Detail LHM hanya bisa 1 kali!'))

class lhm_transaction_line_nap_line(models.Model):
    _name = 'lhm.transaction.line.nap.line'

    lhm_line_id = fields.Many2one('lhm.transaction.line','LHM Line Ref', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', related='lhm_line_id.employee_id', string='Karyawan')
    lhm_id = fields.Many2one('lhm.transaction', related='lhm_line_id.lhm_id', string='LHM Ref', readonly=True)
    nap_line_id = fields.Many2one('lhm.nap.line','NAP Line Ref', ondelete='cascade')
    nap_id = fields.Many2one('lhm.nap', related='nap_line_id.lhm_nap_id', string='NAP Ref', readonly=True, store=True)
    nap_date = fields.Date(related='nap_id.date_nap', string='NAP Date', readonly=True, store=True)
    nap_date_pks = fields.Date(related='nap_id.date_pks', string='PKS Date', readonly=True, store=True)
    nilai = fields.Float('Nilai')
    uom_id = fields.Many2one('uom.uom', 'Satuan 1')
    nilai2 = fields.Float('Berat')
    uom_id2 = fields.Many2one('uom.uom', 'Satuan 2')

    @api.constrains('lhm_line_id', 'nap_line_id')
    def _check_double_link(self):
        check = True
        for line in self:
            if line.lhm_line_id:
                other_line = self.search([('id','!=',line.id),('lhm_line_id','=',line.lhm_line_id.id),('nap_line_id','=',line.nap_line_id.id)])
                if other_line:
                    raise ValidationError(_('Alokasi antara Detail NAP dan Detail LHM hanya bisa 1 kali!'))
########################################### End Of Link NAB and LHM #############################################
################################################## Transaction Afkir NAB ####################################################
class lhm_nab_afkir(models.Model):
    _name = 'lhm.nab.afkir'
    _description = 'Nota Afkir Buah'
    
    @api.depends('line_ids')
    def _compute_janjang(self):
        if self.line_ids:
            total_janjang = 0
            for line_nab_afkir in self.line_ids:
                total_janjang = total_janjang + line_nab_afkir.qty
            self.janjang_jml = total_janjang

    @api.depends('date_naf', 'state')
    def _compute_account_period_id(self):
        for plantation_naf in self:
            if plantation_naf.date_naf:
                period_id = self.env['account.period'].search([('date_start', '<=', plantation_naf.date_naf), ('date_stop', '>=', plantation_naf.date_naf), ('special', '=', False)])
                if period_id:
                    plantation_naf.account_period_id = period_id

    name                = fields.Char('No. Register', required=False)
    date_naf            = fields.Date("Tanggal")
    account_period_id   = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", compute='_compute_account_period_id', readonly=True, store=True)
    date_start          = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop           = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    no_naf              = fields.Char('BA Afkir')
    afdeling_id         = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict")
    janjang_jml         = fields.Float('Jumlah Janjang', readonly=True, compute='_compute_janjang', store=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    line_ids            = fields.One2many('lhm.nab.afkir.line', inverse_name='lhm_nab_afkir_id', string="Detail Nota Angkut Panen", )
    state               = fields.Selection([
                                ('draft', 'New'), ('cancel', 'Cancelled'),
                                ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                                copy=False, default='draft', index=True, readonly=True,
                                help="* New: Dokumen Baru.\n"
                                     "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                     "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                     "* Done: Dokumen Sudah Selesai Diproses. \n")

    def unlink(self):
        for nab in self:
            if nab.state not in ['draft']:
                raise UserError(_('Status Nota Angkut Panen dengan nomor %s adalah %s.\n'
                                  'Nota Angkut Panen hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (nab.name, nab.state.title()))
        nab = super(lhm_nab_afkir, self).unlink()
        return nab
    
    def button_confirm(self):
        self.state = 'confirmed'
        self.line_ids.link_to_lhm_progress()
    
    def button_draft(self):
        self.state = 'draft'
    
    def button_cancel(self):
        self.state = 'cancel'
    
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('lhm.nab.afkir') or _('New')
        return super(lhm_nab_afkir, self).create(values)

class lhm_nap_afkir(models.Model):
    _name = 'lhm.nap.afkir'
    _description = 'Nota Afkir Buah'
    
    @api.depends('line_ids')
    def _compute_janjang(self):
        if self.line_ids:
            total_janjang = 0
            for line_nap_afkir in self.line_ids:
                total_janjang = total_janjang + line_nap_afkir.qty
            self.janjang_jml = total_janjang

    @api.depends('date_naf', 'state')
    def _compute_account_period_id(self):
        for plantation_naf in self:
            if plantation_naf.date_naf:
                period_id = self.env['account.period'].search([('date_start', '<=', plantation_naf.date_naf), ('date_stop', '>=', plantation_naf.date_naf), ('special', '=', False)])
                if period_id:
                    plantation_naf.account_period_id = period_id

    name                = fields.Char('No. Register', required=False)
    date_naf            = fields.Date("Tanggal")
    account_period_id   = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", compute='_compute_account_period_id', readonly=True, store=True)
    date_start          = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop           = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    no_naf              = fields.Char('BA Afkir')
    afdeling_id         = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict")
    janjang_jml         = fields.Float('Jumlah Janjang', readonly=True, compute='_compute_janjang', store=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    line_ids            = fields.One2many('lhm.nap.afkir.line', inverse_name='lhm_nap_afkir_id', string="Detail Nota Angkut Panen", )
    state               = fields.Selection([
                                ('draft', 'New'), ('cancel', 'Cancelled'),
                                ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                                copy=False, default='draft', index=True, readonly=True,
                                help="* New: Dokumen Baru.\n"
                                     "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                     "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                     "* Done: Dokumen Sudah Selesai Diproses. \n")

    def unlink(self):
        for nap in self:
            if nap.state not in ['draft']:
                raise UserError(_('Status Nota Angkut Panen dengan nomor %s adalah %s.\n'
                                  'Nota Angkut Panen hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (nap.name, nap.state.title()))
        nap = super(lhm_nap_afkir, self).unlink()
        return nap
    
    def button_confirm(self):
        self.state = 'confirmed'
        self.line_ids.link_to_lhm_progress()
    
    def button_draft(self):
        self.state = 'draft'
    
    def button_cancel(self):
        self.state = 'cancel'
    
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('lhm.nap.afkir') or _('New')
        return super(lhm_nap_afkir, self).create(values)

class lhm_nab_afkir_line(models.Model):
    _name = 'lhm.nab.afkir.line'
    _description = 'LHM Nota Angkut Panen Line'

    block_id            = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    tgl_panen           = fields.Date(" Tanggal Panen")
    qty                 = fields.Float('Jumlah Janjang')
    lhm_nab_afkir_id    = fields.Many2one("lhm.nab.afkir", string="Afkir Nota Buah Angkut", ondelete="cascade")
    lhm_progress_ids    = fields.Many2many('lhm.transaction.process.line', 'lhm_process_nab_afkir_line_rel', 'nab_afkir_line_id', 'progress_id', 'LHM Progress Ref')

    def link_to_lhm_progress(self):
        for line in self:
            lhm_lines = self.env['lhm.transaction.process.line'].search([
                ('location_id','=',line.block_id.location_id.id), 
                ('lhm_id.state','!=','draft'), 
                ('lhm_id.date','=',line.tgl_panen), 
                ('activity_id.is_panen','=',True)])
            if not lhm_lines:
                continue
            else:
                line.write({'lhm_progress_ids': [(6,0,lhm_lines.ids)]})
                #Trigger Function
                lhm_lines.write({'nab_afkir_line_ids': []})

    @api.model
    def _cron_linked_to_nab(self):
        pending_line = self.search([('lhm_progress_ids','=',False), ('lhm_nab_afkir_id.state','!=','draft')])
        pending_line.link_to_lhm_progress()

class lhm_nap_afkir_line(models.Model):
    _name = 'lhm.nap.afkir.line'
    _description = 'LHM Nota Angkut Panen Line'

    block_id            = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    tgl_panen           = fields.Date(" Tanggal Panen")
    qty                 = fields.Float('Jumlah Janjang')
    lhm_nap_afkir_id    = fields.Many2one("lhm.nap.afkir", string="Afkir Nota Buah Angkut", ondelete="cascade")
    lhm_progress_ids    = fields.Many2many('lhm.transaction.process.line', 'lhm_process_nap_afkir_line_rel', 'nap_afkir_line_id', 'progress_id', 'LHM Progress Ref')

    def link_to_lhm_progress(self):
        for line in self:
            lhm_lines = self.env['lhm.transaction.process.line'].search([
                ('location_id','=',line.block_id.location_id.id), 
                ('lhm_id.state','!=','draft'), 
                ('lhm_id.date','=',line.tgl_panen), 
                ('activity_id.is_panen','=',True)])
            if not lhm_lines:
                continue
            else:
                line.write({'lhm_progress_ids': [(6,0,lhm_lines.ids)]})
                #Trigger Function
                lhm_lines.write({'nap_afkir_line_ids': []})

    @api.model
    def _cron_linked_to_nap(self):
        pending_line = self.search([('lhm_progress_ids','=',False), ('lhm_nap_afkir_id.state','!=','draft')])
        pending_line.link_to_lhm_progress()
############################################## End Of Transaction Afkir NAB #################################################

############################################## Config Nomor Awal Rotasi Panen ##############################################
class lhm_rotasi_panen_balace(models.Model):
    _name = 'lhm.rotasi.panen.balance'
    _description = 'LHM Nomor Akhir Rotasi Panen'

    period_id       = fields.Many2one("account.period", string="Periode Rotasi Panen", ondelete="restrict")
    is_manual       = fields.Boolean("Manual", default=False)
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    image           = fields.Binary(string='File Excel')
    image_filename  = fields.Char(string='File Name')
    rotasi_ids      = fields.One2many('lhm.rotasi.panen.balance.nomor', inverse_name='nomor_id', string="Nomor Awal Rotasi", )

    def import_excel(self):
        if self.rotasi_ids:
            for lines in self.rotasi_ids:
                lines.unlink()
    
        data = base64.decodestring(self.image)
        wb = xlrd.open_workbook(file_contents=data)
    
        rotasi_obj = self.env['lhm.rotasi.panen.balance.nomor']
        sh = wb.sheet_by_index(0)
        for rx in range(sh.nrows):
            if rx > 0:
                if sh.cell(rx, 0) is not None:
                    val = sh.cell(rx, 0).value
                
                    if isinstance(val, float):
                        code_new = str(int(val))
                    else:
                        code_new = val
                
                    wt = self.env['lhm.plant.block']
                    block_id = wt.search([('code', '=', code_new)]).id

                    rotasi_obj.create({
                        'block_code': code_new or False,
                        'block_id': block_id,
                        'value': sh.cell(rx, 2).value or False,
                        'nomor_id': self.id
                    })

class lhm_rotasi_panen_balace_nomor(models.Model):
    _name           = 'lhm.rotasi.panen.balance.nomor'
    _description    = 'LHM Nomor Akhir Rotasi Panen Detail'

    block_code  = fields.Char("Kode Blok")
    block_id    = fields.Many2one("lhm.plant.block", string="Nama Blok", ondelete="restrict")
    value       = fields.Integer('Nomor Akhir')
    nomor_id    = fields.Many2one("lhm.rotasi.panen.balance", string="No Akhir Rotasi Panen", ondelete="cascade")
########################################### End Of Config Nomor Awal Rotasi Panen  ##########################################



#---------------------------------------------------------------------------------------------------------------------------#