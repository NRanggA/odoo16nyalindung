# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    asset_type = fields.Selection([
        ('lva', 'LVA'),
        ('fa', 'FA'),
    ], string='Asset Type',default='lva')
    asset_category_id = fields.Many2one('account.asset.category', string='Asset Category',ondelete="restrict")
    fix_asset_state = fields.Selection([
        ('registered', 'Registered'),
        ('not_registered', 'Not Registered'),
    ], string='Fix Asset Status')
    prefix_seq = fields.Char('Prefix Sequence',required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence')


    @api.onchange('asset_category_id','asset_type')
    def _onchange_asset_type(self):
        if self.asset_type == 'fa' and not self.asset_category_id:
            self.fix_asset_state = 'not_registered'
        elif self.asset_type == 'fa' and self.asset_category_id:
            self.fix_asset_state = 'registered'

    def _prepare_seq_vals(self,val):
        code = val.get('name').replace(" ","").lower()
        return {
            'name': 'Sequence for Equipment Category %s'%val.get('name'),
            'code': '%s.%s'%(self._name,code),
            'prefix': '%s/'%val.get('prefix_seq') + '%(' +'month)s'+ '/'+ '%(' + 'year)s/',
            'padding': 4
        }

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            code = val.get('name').replace(" ","").lower()
            
            seq_id = self.env['ir.sequence'].search([('code', '=', '%s.%s'%(self._name,code))],limit=1)
            if not seq_id:
                seq_id = self.env['ir.sequence'].create(self._prepare_seq_vals(val))
                val['sequence_id'] = seq_id.id
            else:
                val['sequence_id'] = seq_id.id
            
        return super().create(vals)

    def write(self, vals):
        for val in vals:
            code = self.name.replace(" ","").lower()
            seq_id = self.env['ir.sequence'].search([('code', '=', '%s.%s'%(self._name,code))],limit=1)
            if not seq_id:
                seq_id = self.env['ir.sequence'].create(self._prepare_seq_vals())
                val['sequence_id'] = seq_id.id
            else:
                val['sequence_id'] = seq_id.id
            if 'prefix_seq' in val and val.get('prefix_seq') and self.sequence_id:
                code = self.sequence_id.code
                code_split = code.split('/')[0]
                self.sequence_id.code = code.replace(code_split,val.get('prefix_seq'))
                


        return super().write(vals)

