from odoo import models, fields, api, _

class Users(models.Model):
    _inherit = 'res.users'

    mydaya_api_token = fields.Char(readonly=False)