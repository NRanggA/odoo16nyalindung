from odoo import models, fields, tools, api, _

class hr_overtime(models.Model):
    _name           = 'hr.overtime'
    _description    = 'C10i Overtime Management'

    name        = fields.Char("Nama", )
    hours       = fields.Float("Jam")
    normal_day  = fields.Float("Hari Biasa")
    holiday     = fields.Float("Hari Libur")
    work_hours  = fields.Float("Jam Kerja", default=173)
    company_id  = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    active      = fields.Boolean('Aktif', required=True, default=True)

    @api.model
    def create(self, values):
        values['name'] = "OVT/" + (self.env.user.company_id.name or "") + "-" + (str(values.get('hours') or ""))
        return super(hr_overtime, self).create(values)

    def write(self, values):
        if values.get('hours'):
            values['name'] = "OVT/" + (self.env.user.company_id.name or "") + "-" + (str(values.get('hours') or ""))
        return super(hr_overtime, self).write(values)
