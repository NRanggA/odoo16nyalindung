from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manual_consume_ids = fields.One2many('mrp.manual.consume', 'component_consume_production_id', string='Manual Consumed')

    # def action_draft(self):
    #     for production in self:
    #         production.state = 'draft'
    #         # production.reservation_state = False
    #         # production.consumption = 'flexible'

    def action_draft(self):
        for production in self:
            for move in production.move_raw_ids | production.move_finished_ids:
                move.state = 'draft'
                move.quantity_done = 0.0
            for workorder in production.workorder_ids:
                workorder.state = 'pending'
            production.state = 'draft'
