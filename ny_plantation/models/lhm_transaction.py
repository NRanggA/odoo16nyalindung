from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Lhm(models.Model):
    _inherit = 'lhm.transaction'

    assisten_id = fields.Many2one(related='kemandoran_id.assisten_id', string='Assisten')
    kepala_mandor_id = fields.Many2one(related='kemandoran_id.kepala_mandor_id', string='Kepala Mandor')
    mandor_id = fields.Many2one(related='kemandoran_id.mandor_id', string='Mandor')
    tap_kontrol_id = fields.Many2one(related='kemandoran_id.tap_kontrol_id', string='Tap Kontrol')

    # Pembaruan NIK pada LHM [Assisten & Tap Kontrol]
    nik_assisten        = fields.Char("NIK Assisten", related="kemandoran_id.nik_assisten", readonly=True)
    nik_tap_kontrol        = fields.Char("NIK Tap Kontrol", related="kemandoran_id.nik_tap_kontrol", readonly=True)


    # update nik kepala mandor (Mandor Besar)
    nik_mandor_1        = fields.Char("NIK Kepala Mandor", related="kemandoran_id.nik_kepala_mandor", readonly=True)

    unique_lhm_nap_ids = fields.Many2many('lhm.nap', string="Nota Angkut Panen", compute='_compute_unique_lhm_naps')

    kepala_mandor_approved = fields.Boolean('Approved By Kepala Mandor')

    @api.depends('lhm_nap_line_ids.lhm_nap_line_id.lhm_nap_id')
    def _compute_unique_lhm_naps(self):
        for lhm in self:
            lhm_naps = lhm.lhm_nap_line_ids.mapped('lhm_nap_line_id.lhm_nap_id')
            unique_ids = list(set(lhm_naps.ids))
            lhm.unique_lhm_nap_ids = [(6, 0, unique_ids)]

    def action_open_related_lhm_naps(self):
        self.ensure_one()
        action = self.env.ref('c10i_lhm_v16.action_lhm_nap_input_button_box').read()[0]
        action['domain'] = [('id', 'in', self.unique_lhm_nap_ids.ids)]
        return action
    
    def action_approve_kepala_mandor(self):
        for rec in self:
            rec.sudo().kepala_mandor_approved = True
    
    def button_approve(self):
        # for rec in self:
        #     if not rec.kepala_mandor_approved:
        #         raise ValidationError("Tidak dapat meng-Approve LHM yang belum di Approve oleh Kepala Mandor")
        return super().button_approve()

    def button_draft(self):
        res = super().button_draft()
        
        self.write({'kepala_mandor_approved': False})

        return res