from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError

class SeedTransfer(models.Model):
    _name        = 'seed.transfer'
    _description = 'Seed Transfer'

    name               = fields.Char('No. Dokumen')
    date               = fields.Date('Tanggal', required=True)
    line_ids           = fields.One2many('seed.transfer.line', 'seed_transfer_id', string='Transfer Bibitan Line')
    mutation_type_id   = fields.Many2one('mutation.type', string='Jenis Mutasi', ondelete="cascade", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('close', 'Close'),
    ], string='state', default='draft')

    def button_draft(self):
        for rec in self:
            move_lines = self.env['seed.move.line'].search([('seed_transfer_id', '=', rec.id)])
            if move_lines:
                move_lines.unlink()

            rec.state = 'draft'


    def button_close(self):
        for rec in self:
            rec.state = 'close'
    
    def button_confirm(self):
        for rec in self:
            for line in rec.line_ids:
                location_dest = line.location_dest_id.location_id
                location_src = line.location_src_id.location_id

                move_line_1 = self.env['seed.move.line'].create({
                    'seed_transfer_line_id' : line.id,
                    'nursery_id'            : line.location_src_id.id,  
                    'location_src_id'       : location_src.id,               
                    'location_dest_id'      : False,   
                    'qty'                   : line.qty,
                    'date'                  : line.date,
                    'mutation_type_id'      : line.mutation_type_id.id,
                })

                move_line_2 = self.env['seed.move.line'].create({
                    'seed_transfer_line_id' : line.id,
                    'nursery_id'            : line.location_dest_id.id,  
                    'location_src_id'       : False,      
                    'location_dest_id'      : location_dest.id,               
                    'qty'                   : line.qty,
                    'date'                  : line.date,
                    'mutation_type_id'      : line.mutation_type_id.id,
                })

                line.move_line_ids = [(4, move_line_1.id), (4, move_line_2.id)]

            rec.state = 'confirm'

    def action_show_move(self):
        for rec in self:
            move_line_ids = []
            for line in rec.line_ids:
                move_line_ids.extend(line.move_line_ids.ids)  

            return {
                'type': 'ir.actions.act_window',
                'name': 'Seed Move Line',
                'res_model': 'seed.move.line',
                'view_id': self.env.ref('c10i_plantation_seed.seed_move_line_transfer_view_tree').id,
                'view_mode': 'tree',
                'target': 'current',
                'domain': [('id', 'in', move_line_ids)],
            }

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

        return super(SeedTransfer, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Data tidak dapat dihapus. Untuk menghapus, set status menjadi Draft terlebih dahulu.")
        return super(SeedTransfer, self).unlink()

class SeedTransferLine(models.Model):
    _name        = 'seed.transfer.line'
    _description = 'Seed Transfer Line'

    seed_transfer_id             = fields.Many2one('seed.transfer', string="Transfer Bibit", ondelete="cascade")
    mutation_type                = fields.Selection(related='seed_transfer_id.mutation_type_id.type', string='Tipe Mutasi', ondelete="cascade", store=True)
    date                         = fields.Date(string='Tanggal')
    mutation_type_id             = fields.Many2one(related='seed_transfer_id.mutation_type_id', string='Jenis Mutasi', ondelete="cascade", store=True)
    qty                          = fields.Float('Qty')
    location_src_id              = fields.Many2one('lhm.nursery', string='From', ondelete="cascade")
    location_dest_id             = fields.Many2one('lhm.nursery', string='To', ondelete="cascade")
    move_line_ids                = fields.One2many('seed.move.line', 'seed_transfer_line_id', string='Related Move Lines')  # Relasi ke seed.move.line