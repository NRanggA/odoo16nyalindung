from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    plantation_location_type_id = fields.Many2one("lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")