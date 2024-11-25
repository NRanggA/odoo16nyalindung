from odoo import models, fields, api, _

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    general = fields.Boolean('General', default=False)