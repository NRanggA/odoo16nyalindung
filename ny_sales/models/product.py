from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_discount = fields.Boolean(
        related='product_tmpl_id.is_discount',
        string='Is Discount',
        readonly=False,
        store=True,
    )

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_discount = fields.Boolean('Is Discount')
