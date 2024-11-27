from odoo import models, fields, api, _

class LocationType(models.Model):
    _inherit = 'lhm.location.type'

    laboratorium = fields.Boolean()