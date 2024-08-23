from odoo import models, fields, api, _


class LhmWageBoronganPanen(models.Model):
    _name           = 'lhm.wage.borongan.panen'
    _description    = 'Upah Borongan'

    activity_id     = fields.Many2one('lhm.activity', string='Aktivitas', required=True)
    activity_code   = fields.Char(related='activity_id.code' ,string='Kode', readonly=True)
    product_id      = fields.Many2one('product.product', string='Product', required=True)
    qty             = fields.Integer('Qty', required=True)
    satuan_id       = fields.Many2one('uom.uom', string='Satuan')
    min_drc         = fields.Integer('Mulai dari DRC %')
    max_drc         = fields.Integer('Sampai dengan DRC %')
    price           = fields.Integer('Harga')