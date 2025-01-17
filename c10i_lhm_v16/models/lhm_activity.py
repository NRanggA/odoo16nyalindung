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

###################################################### Master Activity ######################################################
class lhm_activity(models.Model):
    _name           = 'lhm.activity'
    _description    = 'LHM Activity Management'

    name                                        = fields.Char("Name")
    code                                        = fields.Char("Code")
    type_id                                     = fields.Many2one("lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    parent_id                                   = fields.Many2one("lhm.activity", string="Parent Activity", ondelete="restrict")
    child_ids                                   = fields.One2many('lhm.activity', 'parent_id', 'Child Activity')
    parent_left                                 = fields.Integer('Left Parent', index=1)
    parent_right                                = fields.Integer('Right Parent', index=1)
    parent_code                                 = fields.Char(related="parent_id.code", string="Parent Activity", readonly=True, store=True)
    uom_id                                      = fields.Many2one("uom.uom", string="Satuan 1", ondelete="restrict")
    uom2_id                                     = fields.Many2one("uom.uom", string="Satuan 2", ondelete="restrict")
    active                                      = fields.Boolean("Active", default=True)
    is_panen                                    = fields.Boolean("Panen", default=False)
    is_variance                                 = fields.Boolean("Is Variance?", default=False, help="centang untuk menghitung variance di laporan progress kerja")
    skb                                         = fields.Boolean("Is SKB?", default=False, help="centang untuk aktivitas yang akan divalidasi untuk penggunaan material")
    bypass                                      = fields.Boolean("Is By Pass?", default=False, help="centang untuk aktivitas tidak akan dirunning")
    vh2vh                                       = fields.Boolean("VH to VH", default=False, help="centang untuk aktivitas khusus untuk running kendaraan ke kendaraan")
    level                                       = fields.Integer("Level", compute="_compute_level", readonly=True, store=True)
    doc_ids                                     = fields.Many2many('res.doc.type', 'rel_doc_type_activity', 'activity_id', 'doc_type_id', string='Documents')
    charge_ids                                  = fields.Many2many('lhm.charge.type', 'rel_chg_type_activity', 'activity_id', 'charge_id', string='Muatan')
    company_id                                  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    account_id                                  = fields.Many2one("account.account", string="Allocation", ondelete="restrict")
    beban_closing_account_id                    = fields.Many2one('account.account', 'Beban Closing Account (TBM)')
    tm_beban_closing_account_id                 = fields.Many2one('account.account', 'Beban Closing Account (TM) - Inti')
    tm_plasma_closing_account_id                = fields.Many2one('account.account', 'Beban Closing Account (TM) - Plasma')
    counterpart_closing_account_id              = fields.Many2one('account.account', 'Kontra Closing Account TBM')
    tm_counterpart_closing_account_id           = fields.Many2one('account.account', 'Kontra Closing Account TM - Inti')
    tm_plasma_counterpart_closing_account_id    = fields.Many2one('account.account', 'Kontra Closing Account TM - Plasma')
    
    # Menambahkan field is hasil 2 untuk menandakan bahwa aktivitas ini hasilnya terdapat 2 hasil
    is_hasil_2                                  = fields.Boolean('Hasil 2', default=False)
    is_nap                                      = fields.Boolean('NAP', default=False)

    # project_id      = fields.Many2one("lhm.project", string="Project")

    product_id                                  = fields.Many2one('product.product', string="Product 1", ondelete="restrict")
    product2_id                                 = fields.Many2one('product.product', string="Product 2", ondelete="restrict")

    parent_path                                 = fields.Char("Parent Path", index=True, unaccent=False)
    _parent_name                                = "parent_id"
    _parent_store                               = True
    _parent_order                               = 'code, name'
    _order                                      = 'code, parent_left asc'

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            if record.code:
                # Cek jika ada karyawan lain dengan no_induk yang sama
                existing_code = self.search([('code', '=', record.code), ('id', '!=', record.id)], limit=1)
                if existing_code:
                    raise ValidationError(f"Code '{record.code}' sudah digunakan oleh Aktivitas '{existing_code.name}', silahkan masukkan kode lain !")

    def get_price_borongan(self, drc=None, product=None):
        price = 0
        for record in self:
            if drc is not None and product is not None: 
                if record.is_panen and record.is_hasil_2:
                    borongan_panen = self.env['lhm.wage.borongan.panen'].search([
                        ('activity_id', '=', record.id),
                        ('product_id', '=', product.id),
                        ('min_drc', '<=', drc),
                        '|', 
                        ('max_drc', '>=', drc), 
                        ('max_drc', '=', 0)
                    ], limit=1) 
                    
                    price = borongan_panen.price
            else:  
                if record.is_panen:
                    borongan_panen = self.env['lhm.wage.borongan.panen'].search([
                        ('activity_id', '=', record.id),
                        ('min_drc', '=', 0), 
                    ], limit=1)  
                    price = borongan_panen.price
                else:
                    borongan_rawat = self.env['lhm.wage.borongan.rawat'].search([
                        ('activity_id', '=', record.id),
                    ], limit=1) 
                    price = borongan_rawat.price
        return price

    @api.depends('parent_id')
    def _compute_level(self):
        for record in self:
            parent_path = record.parent_id.parent_path if record.parent_id else ''
            record.level = parent_path.count('/') + 1 if parent_path else 1

    def _get_account(self):
        self.ensure_one()
        res = False
        if self.account_id:
            res = self.account_id
        elif self.parent_id:
            res = self._get_account(self.parent_id)
        else:
            res = self.type_id and self.type_id.account_id or False
        return res

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, '%s %s'%(record.code, record.name)))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def default_get(self, default_fields):
        """If we're creating a new account through a many2one, there are chances that we typed the account code
        instead of its name. In that case, switch both fields values.
        """
        default_name = self._context.get('default_name')
        default_code = self._context.get('default_code')
        if default_name and not default_code:
            try:
                default_code = int(default_name)
            except ValueError:
                pass
            if default_code:
                default_name = False
        contextual_self = self.with_context(default_name=default_name, default_code=default_code)
        return super(lhm_activity, contextual_self).default_get(default_fields)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_activity = self.search(domain + args, limit=limit)
        return lhm_activity._name_get()
#################################################### End Master Activity ####################################################