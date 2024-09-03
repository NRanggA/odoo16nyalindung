from odoo import models, fields, api, _

class MutationType(models.Model):
    _name        = 'mutation.type'
    _description = 'Tipe Mutasi'

    code        = fields.Char('Kode', required=True)
    name        = fields.Char('Nama Mutasi', required=True)
    mutation    = fields.Selection([
                    ('tambah', '+'),
                    ('kurang', '-'),
                ], string='Mutasi')


