from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class SeedMove(models.Model):
    _name           = 'seed.move'
    _description    = 'Pembibitan'

    name               = fields.Char('No. Dokumen')
    date               = fields.Date('Tanggal', required=True)
    line_ids           = fields.One2many('seed.move.line', 'seed_move_id', string='Bibitan Line')
    mutation_type_id   = fields.Many2one('mutation.type', string='Jenis Mutasi', ondelete="cascade", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('close', 'Close'),
    ], string='state', default='draft')

    def button_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def button_draft(self):
        for rec in self:
            rec.state = 'draft'

    def button_close(self):
        for rec in self:
            rec.state = 'close'

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            current_year = datetime.now().year
            
            mutation_type = self.env['mutation.type'].browse(vals.get('mutation_type_id'))
            
            if mutation_type and mutation_type.code:
                sequence_code = f"{mutation_type.code}/{current_year}/"
            else:
                sequence_code = f"-/{current_year}/"

            next_seq = self.env['ir.sequence'].next_by_code('seed.move') or '001'

            vals['name'] = f"{sequence_code}{next_seq}"

        return super(SeedMove, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Data tidak dapat dihapus. Untuk menghapus, set status menjadi Draft terlebih dahulu.")
        return super(SeedMove, self).unlink()

class SeedMoveLine(models.Model):
    _name           = 'seed.move.line'
    _description    = 'Pembibitan Line'

    seed_transfer_id             = fields.Many2one(related='seed_transfer_line_id.seed_transfer_id', string='Transfer Bibit', ondelete="cascade") 
    seed_transfer_line_id        = fields.Many2one('seed.transfer.line', string='Transfer Bibit Line', ondelete="cascade") 
    product_id                   = fields.Many2one(related='nursery_id.product_id', string='Product', store=True)
    location_type_id             = fields.Many2one('lhm.location.type', string='Tipe Lokasi')
    location_id                  = fields.Many2one('lhm.location', string='Lokasi')
    activity_id                  = fields.Many2one('lhm.activity', string="Aktivitas")
    seed_move_id                 = fields.Many2one('seed.move', string="Pembibitan", ondelete="cascade")
    mutation_type                = fields.Selection(related='seed_move_id.mutation_type_id.type', string='Tipe Mutasi', ondelete="cascade", store=True)
    date                         = fields.Date(string='Tanggal')
    satuan_id                    = fields.Many2one(related='nursery_id.product_id.uom_id', string='Satuan', store=True)
    mutation_type_id             = fields.Many2one('mutation.type', string='Jenis Mutasi', ondelete="cascade", store=True)
    qty                          = fields.Float('Qty')
    nursery_id                   = fields.Many2one('lhm.nursery', string='Blok Bibit', ondelete="cascade")
    location_src_id              = fields.Many2one('lhm.location', string='From', ondelete="cascade")
    location_dest_id             = fields.Many2one('lhm.location', string='To', ondelete="cascade")
    fil_location_src_ids         = fields.Many2many('lhm.location','rel_seed_location_src', string="Filter From", compute="_get_location")
    fil_location_dest_ids        = fields.Many2many('lhm.location', 'rel_seed_location_dest', string="Filter To", compute="_get_location")

    @api.onchange('nursery_id', 'mutation_type_id')
    def _onchange_nursery_and_mutation_type(self):
        if self.nursery_id:
            if self.mutation_type_id and self.mutation_type_id.type in ['incoming', 'adj_in', 'adj_out']:
                self.location_dest_id = self.nursery_id.location_id
            elif self.mutation_type_id and self.mutation_type_id.type == 'outgoing':
                self.location_src_id = self.nursery_id.location_id 
        else:
            self.location_dest_id = False  


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