from odoo import models, fields, api, _

class SphMove(models.Model):
    _name = 'sph.move'
    _description = 'SPH Move'

    lhm_id              = fields.Many2one('lhm.transaction', string='LHM')
    date                = fields.Date('Tanggal')
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    # location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    qty                 = fields.Float('Qty')
    uom_id              = fields.Many2one('uom.uom', string='Satuan')
    block_tanam_id      = fields.Many2one('lhm.plant.block', string='Block Tanam')
    type                = fields.Selection([
                            ('awal', 'Saldo Awal'),
                            ('pokok_mati', 'Pokok Mati'),
                            ('sisip', 'Sisip'),
                        ], string='Detail')