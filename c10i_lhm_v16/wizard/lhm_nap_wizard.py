from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class LhmNapWizard(models.TransientModel):
    _name = 'lhm.nap.wizard'
    _description = 'Wizard untuk Mendapatkan Data Karet'

    # date = fields.Date(string="Tanggal", required=True)
    # kemandoran_id = fields.Many2one('hr.foreman', string="Kemandoran", required=True)

    # lhm_ids = fields.Many2many('lhm.transaction', domain="[('is_nap', '=', True)]", string="Pilih LHM")
    lhm_ids = fields.Many2many('lhm.transaction', domain="[('is_hasil_2', '=', True)]", string="Pilih LHM")

    # @api.onchange('lhm_ids')
    # def _onchange_lhm_ids(self):
    #     for rec in self:
    #         for line in rec.lhm_ids :
    #             if line.activity_id.is_hasil_2:
    #                 return {'domain': {'lhm_ids': [('line.is_hasil_2', '!=', False)]}}

    def action_get_data(self):
        """
        Fungsi ini dipanggil saat user menekan tombol 'Dapatkan Data' di wizard.
        Data wizard digunakan untuk menjalankan logika pengambilan dan pemrosesan data.
        """
        lhm_nap_id = self.env.context.get('active_id')
        lhm_nap = self.env['lhm.nap'].browse(lhm_nap_id)
        if lhm_nap:
            selected_lhm_lines = self.env['lhm.transaction.nap.line'].search([
                ('lhm_id', 'in', self.lhm_ids.ids),
                ('lhm_transaction_line_id.state', '=', 'in_progress'),
                # ('lhm_transaction_line_id.activity_id.is_hasil_2', '=', True),
            ])
            lhm_nap.process_data_karet(selected_lhm_lines)

    # def action_get_data(self):
    #     """
    #     Fungsi ini dipanggil saat user menekan tombol 'Dapatkan Data' di wizard.
    #     Data wizard digunakan untuk menjalankan logika pengambilan dan pemrosesan data.
    #     """
    #     lhm_nap_id = self.env.context.get('active_id')
    #     lhm_nap = self.env['lhm.nap'].browse(lhm_nap_id)
    #     if not lhm_nap:
    #         raise UserError("Data LHM NAP tidak ditemukan.")

    #     # Panggil method utama dengan parameter dari wizard
    #     lhm_nap.process_data_karet(self.date, self.kemandoran_id)
