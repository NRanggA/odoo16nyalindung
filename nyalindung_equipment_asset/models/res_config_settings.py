from odoo import _, api, fields, models

class Config(models.TransientModel):
    _inherit = 'res.config.settings'

    threshold = fields.Float('Threshold')

    def set_values(self):
        super(Config, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('ny_equipment.threshold', self.threshold or False)

    @api.model
    def get_values(self):
        res = super(Config, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'threshold': float(params.get_param('ny_equipment.threshold', default=0.0)),
        })
        return res
