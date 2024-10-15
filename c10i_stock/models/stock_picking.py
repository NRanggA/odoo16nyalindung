from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = 'stock.picking'

    no_kendaraan    = fields.Char('No. Kendaraan')
    no_expedisi     = fields.Char('No. Expedisi')
    