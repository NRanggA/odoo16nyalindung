from odoo import models, fields, api, _


class TargetProduction(models.Model):
    _name        = 'target.production'
    _description = 'Target Produksi'

    name    = fields.Char('Category', required=True)
    target  = fields.Integer('Target Produksi', required=True)
    uom_id  = fields.Many2one('uom.uom', string='Satuan', required=True)
    volume  = fields.Char('Volume')
