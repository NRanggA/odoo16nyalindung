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

#################################################### Master Blok Bibitan ####################################################
class lhm_nursery(models.Model):
    _name           = 'lhm.nursery'
    _description    = 'LHM Nursery'

    def _default_location_type(self):
        location_type_ids = self.env['lhm.location.type'].search([('nursery', '=', True)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False

    name                = fields.Char("Deskripsi")
    code                = fields.Char("Kode Batch")
    location_id         = fields.Many2one("lhm.location", string="Lokasi")
    location_type_id    = fields.Many2one("lhm.location.type", string="Type Lokasi", ondelete="restrict", default=_default_location_type)
    date                = fields.Date("Periode Batch")
    varietas            = fields.Char("Varietas")
    qty                 = fields.Float("Jumlah")
    active              = fields.Boolean("Active", default=True)
    group_progress_id   = fields.Many2one("plantation.location.reference", string="Grouping LPPH")
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    account_id          = fields.Many2one("account.account", "Cost Account")
    product_id          = fields.Many2one('product.product', string='Product')
    varieties_id        = fields.Many2one('plant.varieties', string='Varietas')

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
        new_location    = False
        location        = super(lhm_nursery, self).create(values)
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
        return super(lhm_nursery, self).write(values)

    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        location = super(lhm_nursery, self).unlink()
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
################################################# End Of Master Blok Bibitan ################################################