
from odoo import models, fields, tools, api, _

class hr_nature(models.Model):
    _name           = 'hr.nature'
    _description    = 'C10i Nature Management'

    @api.depends('ptkp_id')
    def _compute_married(self):
        for nature in self:
            if nature.ptkp_id.marital == 'K':
                nature.married = True
            elif nature.ptkp_id.marital == 'TK':
                nature.married = False
            else:
                nature.married = False

    @api.depends('nature', 'weight', 'weight_married', 'weight_children', 'children')
    def _compute_value_kg(self):
        for nature in self:
            if nature.nature != 0 and nature.weight != 0:
                nature.value_rp = nature.nature / (nature.weight + nature.weight_married + (nature.weight_children * nature.children))

    @api.depends('nature', 'weight', 'weight_married', 'weight_children', 'potongan_kg', 'children')
    def _compute_potongan_kg(self):
        for nature in self:
            if nature.nature != 0 and nature.weight != 0:
                nature.potongan_rp = (nature.nature / (nature.weight + nature.weight_married + (nature.weight_children * nature.children))) * nature.potongan_kg

    name            = fields.Char("Nama", )
    ptkp_id         = fields.Many2one(comodel_name='hr.ptkp', string="PTKP")
    nature          = fields.Float("Natura")
    weight          = fields.Float("Tunjangan Pribadi(Kg)")
    weight_married  = fields.Float("Tunjangan Nikah(Kg)")
    weight_children = fields.Float("Tunjangan Anak(Kg)")
    potongan_kg     = fields.Float("Potongan(Kg)")
    married         = fields.Boolean("Nikah", compute=_compute_married, store=True)
    children        = fields.Integer(string="Jumlah Anak", related="ptkp_id.children", store=True)
    value_rp        = fields.Float("Per Kg(Rp)", compute=_compute_value_kg, store=True)
    potongan_rp     = fields.Float("Potongan(Rp)", compute=_compute_potongan_kg, store=True)
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    active          = fields.Boolean('Aktif', required=True, default=True)

