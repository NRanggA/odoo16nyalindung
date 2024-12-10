from odoo import fields, models, api, _


class LhmWageBoronganContractor(models.Model):
    _name        = 'lhm.wage.borongan.contractor'
    _description = 'Upah Borongan Contractor'

    activity_id     = fields.Many2one('lhm.activity', string='Aktivitas', required=True)
    activity_code   = fields.Char(related='activity_id.code' ,string='Kode', readonly=True)
    qty             = fields.Integer('Qty', required=True)
    
    #harian
    is_harian       = fields.Boolean(string="Harian")
    product_id      = fields.Many2one('product.product', string="Product 1", ondelete="restrict")
    product_id2     = fields.Many2one('product.product', string="Product 2", ondelete="restrict")
    satuan_id       = fields.Many2one('uom.uom', string='Satuan', ondelete="restrict")
    satuan_id2      = fields.Many2one('uom.uom', string='Satuan', ondelete="restrict")
    price           = fields.Integer('Harga Product 1')
    price2          = fields.Integer('Harga Product 2')
    