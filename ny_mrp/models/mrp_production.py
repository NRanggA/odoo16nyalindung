from odoo import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manual_consume_ids = fields.One2many('mrp.manual.consume', 'component_consume_production_id', string='Manual Consumed')