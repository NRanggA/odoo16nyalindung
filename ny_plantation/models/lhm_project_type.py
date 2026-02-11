from odoo import models, fields, api, _

class lhm_project_type(models.Model):
    _inherit = 'lhm.project.type'

    code = fields.Char('Code', required=False, copy=False)
    sequence_id = fields.Many2one('ir.sequence', 'Sequence', required=False, readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'sequence_id' not in vals or not vals['sequence_id']:
                seq = self.env['ir.sequence'].create({
                    'name': 'Sequence' + vals.get('name', 'New Project Type'),
                    'code': 'lhm.project.type.' + vals.get('code', 'pj').lower(),
                    'prefix': vals.get('code', 'PJ').upper(),
                    'padding': 3,
                    'suffix': '/%(month)s/%(year)s',
                    'use_date_range': True,
                    'range_reset': 'monthly',
                    'implementation': 'no_gap'
                })
                vals['sequence_id'] = seq.id
        return super(lhm_project_type, self).create(vals_list)