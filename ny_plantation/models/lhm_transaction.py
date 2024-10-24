from odoo import models, fields, api, _

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