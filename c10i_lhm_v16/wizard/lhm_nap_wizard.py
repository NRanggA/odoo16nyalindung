from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class LhmNapWizard(models.TransientModel):
    _name = 'lhm.nap.wizard'
    _description = 'Wizard untuk Mendapatkan Data Karet'

    # date = fields.Date(string="Tanggal", required=True)
    # kemandoran_id = fields.Many2one('hr.foreman', string="Kemandoran", required=True)
    lhm_ids = fields.Many2many('lhm.transaction', string="Pilih LHM")

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
