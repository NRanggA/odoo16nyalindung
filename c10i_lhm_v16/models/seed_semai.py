from odoo import models, fields, api, _
from datetime import datetime


class SeedSemai(models.Model):
    _name           = 'seed.semai'
    _description    = 'Semai/Sisit Bibitan' 

    name        = fields.Char('No. Dokumen')
    date        = fields.Date('Tanggal')
    line_ids    = fields.One2many('seed.semai.line', 'seed_semai_id', string='Pengeluaran Bibit Line')
    product_id  = fields.Many2one('product.product', string='Product', required=True, ondelete="restrict")


    @api.model
    def create(self, vals):
        if not vals.get('name'):
            current_year = datetime.now().year
            sequence_code = f"FSB/{current_year}/"
            vals['name'] = self.env['ir.sequence'].next_by_code('seed.semai') or f"{sequence_code}001"

        return super(SeedSemai, self).create(vals)
        

class SeedSemaiLine(models.Model):
    _name        = 'seed.semai.line'
    _description = 'Semai/Sisit Bibitan Line'

    # product_id          = fields.Many2one('product.product', string='Product', required=True, ondelete="restrict")
    product_id          = fields.Many2one(related='seed_semai_id.product_id', string='Satuan', store=True)
    satuan_id           = fields.Many2one(related='product_id.uom_id', string='Satuan', store=True)
    seed_semai_id       = fields.Many2one('seed.semai', string="Semai", ondelete="cascade")
    mutation_type_id    = fields.Many2one('mutation.type', string='Jenis Mutasi')
    qty                 = fields.Integer('Qty')
    location_id         = fields.Many2one('lhm.location', string='Lokasi')
