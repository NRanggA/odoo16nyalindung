from odoo import models, fields, api, _

class HrForeman(models.Model):
    _inherit = 'hr.foreman'

    production_daily_target = fields.Float(related='blok_tanam_id.production_daily_target', string='Target Panen Karet')
    # production_daily_target_mandor = fields.Float(related='blok_tanam_id.production_daily_target_mandor', string='Target Panen Karet Mandor')
    production_daily_target_mandor = fields.Float(string='Target Panen Karet Mandor')