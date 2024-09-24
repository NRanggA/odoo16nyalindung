from odoo import models, fields, api, _

class HrForeman(models.Model):
    _inherit = 'hr.foreman'

    assisten_id = fields.Many2one('hr.employee', string='Assisten')
    kepala_mandor_id = fields.Many2one('hr.employee', string='Kepala Mandor')
    mandor_id = fields.Many2one('hr.employee', string='Mandor')
    tap_kontrol_id = fields.Many2one('hr.employee', string='Tap Kontrol')
    blok_tanam_id = fields.Many2one('lhm.plant.block', string='Blok Tanam')

    nik_assisten = fields.Char("NIK Assisten", related='assisten_id.no_induk', readonly=True)
    nik_kepala_mandor = fields.Char("NIK Kepala Mandor", related='kepala_mandor_id.no_induk', readonly=True)
    nik_mandor = fields.Char("NIK Mandor", related='mandor_id.no_induk', readonly=True)
    nik_tap_kontrol = fields.Char("NIK Tap Kontrol", related='tap_kontrol_id.no_induk', readonly=True)