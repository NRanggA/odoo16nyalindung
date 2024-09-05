from odoo import models, fields, api, _
from datetime import datetime


class SeedRelease(models.Model):
    _name           = 'seed.release'
    _description    = 'Pengeluaran Bibit' 

    name        = fields.Char('No. Dokumen')
    date        = fields.Date('Tanggal')
    line_ids    = fields.One2many('seed.release.line', 'seed_release_id', string='Pengeluaran Bibit Line')
    product_id  = fields.Many2one('product.product', string='Product', required=True, ondelete="restrict")


    @api.model
    def create(self, vals):
        if not vals.get('name'):
            current_year = datetime.now().year
            sequence_code = f"FPB/{current_year}/"
            vals['name'] = self.env['ir.sequence'].next_by_code('seed.release') or f"{sequence_code}001"

        return super(SeedRelease, self).create(vals)
        

class SeedReleaseLine(models.Model):
    _name        = 'seed.release.line'
    _description = 'Pengeluaran Bibit Line'

    # product_id          = fields.Many2one('product.product', string='Product', required=True, ondelete="restrict")
    product_id          = fields.Many2one(related='seed_release_id.product_id', string='Satuan', store=True)
    satuan_id           = fields.Many2one(related='product_id.uom_id', string='Satuan', store=True)
    seed_release_id     = fields.Many2one('seed.release', string="Pengeluaran Barang", ondelete="cascade")
    mutation_type_id    = fields.Many2one('mutation.type', string='Jenis Mutasi')
    qty                 = fields.Integer('Qty')
    location_id         = fields.Many2one('lhm.location', string='Lokasi')
