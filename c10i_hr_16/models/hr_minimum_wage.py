import time
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_minimum_wage(models.Model):
    _name           = 'hr.minimum.wage'
    _description    = 'C10i Minimum Wage Management'
    _order          = 'year desc,date_to desc'

    @api.model
    def _get_state(self):
        for state in self:
            all_umr     = self.env['hr.minimum.wage'].search([('id', '!=', state.id), ('year','=',state.year), ('date_to','>',state.date_to)])
            if all_umr:
                state.state = 'notactive'
            else:
                state.state = 'active'

    # @api.depends('year', 'date_to')
    # def _get_state(self):
    #     for record in self:
    #         all_umr = self.env['hr.minimum.wage'].search([('id', '!=', record.id), ('year', '=', record.year), ('date_to', '>', record.date_to)])
    #         record.state = 'notactive' if all_umr else 'active'

    def _default_year(self):
        return int(time.strftime('%Y'))

    name        = fields.Char('Nama', required=False, default="_(NEW)_UMR")
    year        = fields.Integer(string='Tahun', default=_default_year)
    umr_month   = fields.Float(string="UMR(Bulan)")
    date_from   = fields.Date("Tanggal Mulai")
    date_to     = fields.Date("Tanggal Berakhir")
    company_id  = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    state       = fields.Selection([('active', 'Active'), ('notactive', 'Not Active')], string='Status', compute=_get_state)

    @api.onchange('year','date_from','date_to')
    def onchange_date_and_year(self):
        other_ids   = self.env['hr.minimum.wage'].search([('id','!=',self._origin.id),('year','=',self.year)], order="date_to asc")
        if other_ids:
            other_ids = other_ids[-1] #<--- mengambil tanggal akhir paling besar
        else:
            other_ids = False
        if self.date_to:
            if self.date_to and self.date_to <= self.date_from:
                res = {}
                self.date_to = fields.Date.from_string(self.date_from) + relativedelta(days=1)
                return {
                    'warning': {'title': _('Kesalahan Input Data'),
                                'message': _("Tanggal Berakhir Harus Lebih Besar dari Tanggal Mulai")},
                }
            elif int(fields.Date.from_string(self.date_to).strftime('%Y')) != self.year:
                res             = {}
                res['warning']  = {'title': _('Kesalahan Input Data'),
                                    'message': _("Tanggal %s tidak dalam tahun: %s.") % (self.date_to, self.year)}
                self.date_to    = time.strftime(str(self.year) + '-12-31')
                return res
        elif self.year:
            if other_ids and other_ids.date_to == time.strftime(str(self.year) + '-12-31'):
                res             = {}
                res['warning']  = {'title': _('Kesalahan Input Data'),
                                    'message': _("Semua range tanggal pada tahun %s sudah didefinisikan") % self.year}
                self.year       = False
                return res
            elif self.year and other_ids:
                res = {}
                self.date_from  = fields.Date.from_string(other_ids.date_to) + relativedelta(days=1)
                self.date_to    = time.strftime(str(self.year) + '-12-31')
            else:
                res = {}
                self.date_from  = time.strftime(str(self.year) + '-01-01')
                self.date_to    = time.strftime(str(self.year) + '-12-31')

    @api.model
    def create(self, values):
        if values.get('umr_month') <= 0.0:
            raise ValidationError("UMR harus lebih dari 0")
        return super(hr_minimum_wage, self).create(values)

    def write(self, values):
        if isinstance(values.get('umr_month', False), bool) == False:
            if values.get('umr_month') <= 0.0:
                raise ValidationError("UMR harus lebih dari 0")
        return super(hr_minimum_wage, self).write(values)

    def unlink(self):
        for umr in self:
            if umr.state != 'active':
                raise UserError(_('Dokumen tidak dapat dihapus jika status bukan Aktif'))
        min_wage = super(hr_minimum_wage, self).unlink()
        return min_wage
