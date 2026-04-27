from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class MoveLineSetGae(models.TransientModel):
    _name = 'move.line.set.gae'
    _description = 'Move Line Set GAE'

    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution')

    def action_set_gae(self):
        active_ids = self.env.context.get('default_move_line_ids', [])
        if self.env['account.move.line'].search([('id', 'in', active_ids), ('gae_distributed', '=', True)]):
            raise UserError(_('Some of the selected move lines have already been distributed for GAE. Please select only move lines that have not been distributed yet.'))
        
        move_lines = self.env['account.move.line'].browse(active_ids)
        move_lines.write({
            'gae_distribution_id': self.gae_distribution_id.id,
        })