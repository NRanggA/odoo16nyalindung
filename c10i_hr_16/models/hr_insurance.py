from odoo import models,fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class hr_insurance(models.Model):
    _name           = 'hr.insurance'
    _description    = 'C10i Insurance Management'

    name        = fields.Char('Nama', required=False)
    type        = fields.Selection([
                        ('kesehatan', 'Kesehatan'),
                        ('ketenagakerjaan', 'Ketenagakerjaan'),
                        ('pensiun', 'Pensiun'),
                        ('other', 'Lain-lain'),
                        ], string='Tipe Asuransi', default="kesehatan")
    subtype     = fields.Selection([
                        ('none', '-'),
                        ('jht', 'Jaminan Hari Tua'),
                        ('jkk', 'Jaminan Kecelakaan Kerja'),
                        ('jkm', 'Jaminan Kematian'),
                        ('jp', 'Jaminan Pensiun'),
                        ], string='Program', default="none")
    potongan    = fields.Float(string="Pekerja(%)")
    tunjangan   = fields.Float(string="Pemberi Kerja(%)")
    total       = fields.Float(string="Total(%)", compute='_get_total_insurance', store=True)
    date_from   = fields.Date("Tanggal Mulai")
    date_to     = fields.Date("Tanggal Berakhir")
    old_id      = fields.Many2one('hr.insurance', string='Asuransi Sebelumnya')
    company_id  = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    active      = fields.Boolean('Aktif', required=True, default=True)
    setoran_account_id = fields.Many2one('account.account', 'Setoran Account')
    tunjangan_account_id = fields.Many2one('account.account', 'Tunjangan Account')

    @api.depends('potongan', 'tunjangan')
    def _get_total_insurance(self):
        for insurance_total in self:
            insurance_total.total = insurance_total.potongan + insurance_total.tunjangan

    @api.onchange('type', 'subtype')
    def _onchange_type(self):
        self.old_id = False
        if self.type == 'kesehatan':
            insurance_data = self.env['hr.insurance'].search([('type', '=', 'kesehatan'), ('active','=',True)], order="date_to desc", limit=1)
        elif self.type == 'ketenagakerjaan':
            subtype = self.subtype
            insurance_data = self.env['hr.insurance'].search([('type', '=', 'ketenagakerjaan'), ('active', '=', True), ('subtype', '=', subtype)], order="date_to desc", limit=1)
        elif self.type == 'pensiun':
            insurance_data = self.env['hr.insurance'].search([('type', '=', 'pensiun'), ('active','=',True)], order="date_to desc", limit=1)
        else:
            return {'value': {'date_from': False}}

        if insurance_data:
            date_from = fields.Date.from_string(insurance_data.date_to) + relativedelta(days=1)
            self.date_from = date_from
            self.old_id = insurance_data.id
        else:
            return {'value': {'date_from': False}}


    @api.model
    def create(self, values):
        if values.get('date_to') <= values.get('date_from'):
            raise ValidationError("Tanggal berakhir tidak boleh lebih kecil atau sama dengan tanggal awal")

        if values.get('type') == 'kesehatan':
            values['name'] = self.env['ir.sequence'].next_by_code('hr.insurance.kesehatan.sequence.number')
        elif values.get('type') == 'ketenagakerjaan':
            values['name'] = self.env['ir.sequence'].next_by_code('hr.insurance.ketenagakerjaan.sequence.number')
        elif values.get('type') == 'pensiun':
            values['name'] = self.env['ir.sequence'].next_by_code('hr.insurance.pensiun.sequence.number')
        else:
            values['name'] = "Lain - Lain"
        return super(hr_insurance, self).create(values)