from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_a_wip = fields.Boolean(string='Hide Stock Report')



class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_a_wip = fields.Boolean(
        string='Hide Stock Report',
        related='product_tmpl_id.has_a_wip',
        store=True,
        readonly=True
    )
