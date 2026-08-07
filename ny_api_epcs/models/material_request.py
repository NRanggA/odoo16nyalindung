from odoo import models, fields, api, _

class MaterialRequest(models.Model):
    _inherit = 'material.request'

    origin = fields.Char(string='Origin')