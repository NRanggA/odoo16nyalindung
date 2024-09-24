from odoo import models, fields, api, _

class Lhm(models.Model):
    _inherit = 'lhm.transaction'

    assisten_id = fields.Many2one(related='foreman_id.assisten_id', string='Assisten')
    kepala_mandor_id = fields.Many2one(related='foreman_id.kepala_mandor_id', string='Kepala Mandor')
    mandor_id = fields.Many2one(related='foreman_id.mandor_id', string='Mandor')
    tap_kontrol_id = fields.Many2one(related='foreman_id.tap_kontrol_id', string='Tap Kontrol')