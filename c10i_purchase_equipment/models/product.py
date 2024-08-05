# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_asset = fields.Boolean('Asset Equipment')

# class Product(models.Model):
#     _inherit = "product.product"

#     product_asset = fields.Boolean('Asset Equipment')