from odoo import fields, models, api, _


class LhmWageBoronganRawat(models.Model):
    _name        = 'lhm.wage.borongan.rawat'
    _description = 'Upah Borongan Rawat'

    activity_id     = fields.Many2one('lhm.activity', string='Aktivitas', required=True)
    activity_code   = fields.Char(related='activity_id.code' ,string='Kode', readonly=True)
    qty             = fields.Integer('Qty', required=True)
    satuan_id       = fields.Many2one('uom.uom', string='Satuan')
    price           = fields.Integer('Harga')