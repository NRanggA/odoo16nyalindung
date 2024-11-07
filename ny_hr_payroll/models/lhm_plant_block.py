from odoo import models, api, fields

class Block(models.Model):
    _inherit = 'lhm.plant.block'

    with_ongkos_pikul = fields.Boolean()