from odoo import models, fields, api, _

class SeedMutation(models.Model):
    _name           = 'seed.mutation'
    _description    = 'Mutasi Bibitan'

    product_id          = fields.Many2one('product.product', string='Product')
    date                = fields.Date('Tanggal')
    mutation_type_id    = fields.Many2one('mutation.type', string='Jenis Mutasi')
    mutation            = fields.Selection(related='mutation_type_id.mutation', store=True, string='Jenis Mutasi Terkait')
    location_id         = fields.Many2one('lhm.location', string='Lokasi')
    qty                 = fields.Integer('Qty')
    satuan_id           = fields.Many2one(related='product_id.uom_id', string='Satuan', store=True)
    balance             = fields.Integer('Saldo')

