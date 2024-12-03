from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    general = fields.Boolean('General', default=False)