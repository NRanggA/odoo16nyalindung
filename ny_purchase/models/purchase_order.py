from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    non_credit = fields.Boolean('Non Credit')
