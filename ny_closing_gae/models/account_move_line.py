from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution')
    gae_distributed = fields.Boolean(string='GAE Distributed', default=False)
    gae_to_location_ids = fields.Many2many('lhm.location', 'move_line_gae_location_rel', string='GAE ke Lokasi', help='Mendistribusikan biaya lainnya ke Lokasi langsung jika TBM')

    def action_set_gae_distribution(self):
        return {
            'name': _('Set GAE Distribution'),
            'type': 'ir.actions.act_window',
            'res_model': 'move.line.set.gae',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_line_ids': self.ids,
            }
        }