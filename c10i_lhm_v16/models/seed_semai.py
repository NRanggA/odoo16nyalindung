from odoo import models, fields, api, _
from datetime import datetime


class SeedSemai(models.Model):
    _name           = 'seed.semai'
    _description    = 'Pemasukan Bibitan' 

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


    product_id                   = fields.Many2one(related='seed_semai_id.product_id', string='Product', store=True)
    seed_semai_id                = fields.Many2one('seed.semai', string="Semai", ondelete="cascade")
    date                         = fields.Date(related='seed_semai_id.date', string='Tanggal', store=True)
    nursery_id                   = fields.Many2one('lhm.nursery', string='Blok Bibit', ondelete="cascade")
    satuan_id                    = fields.Many2one(related='seed_semai_id.product_id.uom_id', string='Satuan', store=True)
    mutation_type_id             = fields.Many2one('mutation.type', string='Jenis Mutasi', ondelete="cascade")
    qty                          = fields.Integer('Qty')
    location_src_id              = fields.Many2one('lhm.location', string='From', ondelete="cascade")
    location_dest_id             = fields.Many2one('lhm.location', string='To', ondelete="cascade")
    fil_location_src_ids         = fields.Many2many('lhm.location','rel_semai_location_src', string="Filter From", compute="_get_location")
    fil_location_dest_ids        = fields.Many2many('lhm.location', 'rel_semai_location_dest', string="Filter To", compute="_get_location")

    @api.depends('mutation_type_id')
    def _get_location(self):
        for rec in self:
            if rec.mutation_type_id:
                nursery_ids = self.env['lhm.nursery'].search([]).location_id.ids
                
                if rec.mutation_type_id.type in ['incoming', 'adj_in']:
                    rec.fil_location_src_ids = [(6, 0, [])]
                    rec.fil_location_dest_ids = [(6, 0, nursery_ids)]
                
                elif rec.mutation_type_id.type == 'outgoing':
                    plant_block_ids = self.env['lhm.plant.block'].search([]).location_id.ids
                    rec.fil_location_src_ids =  [(6, 0, nursery_ids)]
                    rec.fil_location_dest_ids = [(6, 0, plant_block_ids)]
                
                elif rec.mutation_type_id.type == 'transfer':
                    rec.fil_location_src_ids =  [(6, 0, nursery_ids)]
                    rec.fil_location_dest_ids = [(6, 0, nursery_ids)]
                
                elif rec.mutation_type_id.type == 'adj_out':
                    rec.fil_location_src_ids =  [(6, 0, nursery_ids)]
                    rec.fil_location_dest_ids = [(6, 0, [])]
            else:
                rec.fil_location_src_ids = []
                rec.fil_location_dest_ids = []

