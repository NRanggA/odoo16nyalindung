from odoo import models, fields, api, _

class lhm_project(models.Model):
    _inherit = 'lhm.project'

    code = fields.Char('Code', required=False, copy=False, readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'categ_id' in vals:
                vals['code'] = self.env['lhm.project.type'].browse(vals['categ_id']).sequence_id.next_by_id()
        return super(lhm_project, self).create(vals_list)