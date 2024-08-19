from odoo import models, fields, api, _


class TarifPremiProduction(models.Model):
    _name        = 'tarif.premi.production'
    _description = 'Tarif Premi Produksi'

    name        = fields.Char('Category', required=True)
    nilai_rp    = fields.Integer('Nilai Rupiah', required=True)
    uom_id      = fields.Many2one('uom.uom', string='Satuan')
