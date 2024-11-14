
import logging
import time
# import datetime
import calendar
from odoo.tools.translate import _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons import decimal_precision as dp
from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import base64
import xlrd
from datetime import datetime

from decimal import Decimal, getcontext

################################################## Master Blok Tanam ##########################################################
class lhm_plant_block(models.Model):
    _name           = 'lhm.plant.block'
    _description    = 'LHM Planting Block'

    def _default_location_type(self):
        location_type_ids   = self.env['lhm.location.type'].search([('plantation','=',True)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False

    def _default_year(self):
        return int(time.strftime('%Y'))

    @api.depends('year', 'tm_year')
    def _compute_time_plant(self):
        for block in self:
            current_year = int(time.strftime('%Y'))
            block_age    = int(time.strftime('%Y')) - block.year
            if block.tm_year:
                block.status                = 'tm'
                block.tm_age                = 'TM%s'%str(current_year - block.tm_year + 1)
                block.tbm_age               = 'TBM%s'%str(block.tm_year - block.year - 1)
                block.planting_time         = block_age 

                tm_category = self.env['lhm.tm.category'].search([
                    ('min_age', '<=', block_age),
                    ('max_age', '>=', block_age)
                ], limit=1)

                tm_category = self.env['lhm.tm.category'].search([
                    ('min_age', '<=', block_age + 1),
                    '|',
                    ('max_age', '>=', block_age + 1),
                    ('max_age', '=', 0)
                ], limit=1)

                block.tm_category_id        = tm_category.id if tm_category else False
                block.need_to_be_approved   = False
            else:
                block.status                = 'tbm'
                block.planting_time         = block_age 
                block.tm_age                = ''
                block.tbm_age               = 'TBM%s'%str(block_age and 0 or block_age - 1)
                block.tm_category_id        = False
                if block_age >= 4:
                    block.need_to_be_approved = True
            
    name                = fields.Char("Deskripsi")
    code                = fields.Char("Kode")
    varieties_id        = fields.Many2one('plant.varieties', string='Varietas')
    land_block_id       = fields.Many2one("lhm.land.block", string="Blok Tanah", ondelete="restrict")
    afdeling_id         = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict")
    owner_type          = fields.Selection([('inti','Inti'),('plasma','Plasma')], 'Tipe Kepemilikan', default='inti')
    plasma_pricelist_id = fields.Many2one('product.pricelist', 'Harga TBS Plasma')
    location_id         = fields.Many2one("lhm.location", string="Lokasi")
    location_type_id    = fields.Many2one("lhm.location.type", string="Type Lokasi", ondelete="restrict", default=_default_location_type)
    group_progress_id   = fields.Many2one("plantation.location.reference", string="Grouping LPPH")
    planted             = fields.Float("Planted")
    plantable           = fields.Float("Plantable")
    koefisien_luas      = fields.Float("Koefisien Luasan")
    total_plant         = fields.Float("Jumlah Pokok",  compute="_compute_total_plant", store=True)
    status              = fields.Selection(selection=[('tbm','Tanaman Belum Menghasilkan'),('tm','Tanaman Menghasilkan')],string="Status", compute="_compute_time_plant", store=True)
    need_to_be_approved = fields.Boolean('Butuh Approval untuk masuk ke Kategori Tanaman Menghasilkan', compute='_compute_time_plant', store=True)
    tm_year             = fields.Integer(string='Tahun Menjadi TM')
    # tm_category         = fields.Selection([('young', 'Young'), ('prime', 'Prime'), ('old','Old')], string='TM Category', compute='_compute_time_plant', store=True)
    tm_category_id      = fields.Many2one('lhm.tm.category', string='TM Category', compute='_compute_time_plant', store=True)
    tm_age              = fields.Char('Umur TM', compute='_compute_time_plant', store=True)
    tbm_age             = fields.Char('Umur TBM', compute='_compute_time_plant', store=True)
    planting_time       = fields.Integer(string="Lama Tanam", compute="_compute_time_plant", store=True)
    block_uom           = fields.Many2one('uom.uom', string="Satuan")
    date_start          = fields.Date('Tanggal Awal Tanam')
    year                = fields.Integer(string='Tahun Tanam', default=fields.Datetime.now().year)
    land_class_id       = fields.Many2one("lhm.land.class", string="Kelas Lahan", ondelete="restrict")
    sprouts_id          = fields.Many2one("lhm.palm.oil.sprouts", string="Kecambah Kelapa Sawit", ondelete="restrict")
    section             = fields.Char("Seksi")
    active              = fields.Boolean("Active", default=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    sph_move_ids        = fields.One2many('sph.move', 'block_tanam_id', string='SPH Move')
    opening             = fields.Float('Opening')

    _sql_constraints = [('name_company_uniq', 'unique (name, company_id)', "Blok Tanam Sudah ada percompany!"),]

    @api.depends('sph_move_ids.qty', 'sph_move_ids.type')
    def _compute_total_plant(self):
        for block in self:
            total_awal = 0.0
            total_pokok_mati = 0.0
            total_sisip = 0.0

            for sph_move in block.sph_move_ids:
                if sph_move.type == 'awal':
                    total_awal += sph_move.qty
                elif sph_move.type == 'pokok_mati':
                    total_pokok_mati += sph_move.qty
                elif sph_move.type == 'sisip':
                    total_sisip += sph_move.qty

            block.total_plant = total_awal - total_pokok_mati + total_sisip

    @api.model
    def _get_rate_bjr(self):
        context = self.env.context
        rate = self.env['lhm.bjr'].search([('block_id','=',self.id), ('date','<=', context.get('date', time.strftime('%Y-%m-%d')))])
        return rate and rate[-1].value or 0.0

    @api.onchange('afdeling_id')
    def _onchange_afdeling_id(self):
        if self.afdeling_id:
            print("Error Karena field block tidak ada di model ini !")
            # self.block = self.afdeling_id.code or False

    def button_set_as_tm(self):
        self.status = 'tm'
        self.tm_year = int(time.strftime('%Y'))

    @api.model
    def create(self, values):
        location = super(lhm_plant_block, self).create(values)
        
        if location and not location.location_id:
            location_values = {
                'name' : values.get('name', "(NoCode)"),
                'code' : values.get('code', "(NoCode)"),
                'type_id' : values.get('location_type_id', False),
                'varieties_id' : values.get('varieties_id', False),
                'group_progress_id' : values.get('group_progress_id', False),
            }
            new_location = self.env['lhm.location'].create(location_values)
            if new_location:
                location.location_id = new_location.id

        opening = values.get('opening', False)
        if opening:
            opening_vals = {
                'type': 'awal',
                'date': fields.Date.today(),
                'qty': opening,
                'block_tanam_id': location.id  
            }
            self.env['sph.move'].create(opening_vals)

        return location


    def write(self, values):
        opening             = values.get('opening', False)
        if opening:
            sph_awal = self.sph_move_ids.filtered(lambda x: x.type == 'awal')
            if sph_awal:
                opening_vals       = {
                    'date': fields.Date.today(),
                    'qty' : opening or False,
                }
                sph_awal.write(opening_vals)
            else:
                opening_vals       = {
                    'type': 'awal',
                    'date': fields.Date.today(),
                    'qty' : opening or False,
                    'block_tanam_id': self.id
                }
                self.env['sph.move'].create(opening_vals)

        if 'name' in values and self.location_id:
            self.location_id.write({'name': values.get('name', False)})
        if 'code' in values and self.location_id:
            self.location_id.write({'code': values.get('code', False)})
        if 'location_type_id' in values and self.location_id:
            self.location_id.write({'type_id': values.get('location_type_id', False)})
        if 'varieties_id' in values and self.location_id:
            self.location_id.write({'varieties_id': values.get('varieties_id', False)})
        if 'group_progress_id' in values and self.location_id:
            self.location_id.write({'group_progress_id' : values.get('group_progress_id',False)})
        if 'active' in values and self.location_id:
            self.location_id.write({'active': values.get('active', False)})
        return super(lhm_plant_block, self).write(values)

    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        location = super(lhm_plant_block, self).unlink()
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

    @api.model
    def _cron_update_tahun_tanam(self):
        blocks_to_check = self.search([('id','>',0)])
        for block in blocks_to_check:
            # Triggering Function Field to be Executed to check and update Block Status
            block.write({'year': block.year})
################################################## End Of Master Blok Tanam #################################################