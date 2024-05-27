# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError

class StockMove(models.Model):
    _inherit = "stock.move"

    mr_line_id = fields.Many2one('material.request.line', string='Material Request Line', ondelete='restrict')