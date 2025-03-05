from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class LhmNapWizard(models.TransientModel):
    _name = 'lhm.nap.wizard'
    _description = 'Wizard untuk Mendapatkan Data Karet'

    lhm_ids = fields.Many2many(
        'lhm.transaction',
        domain="[('is_hasil_2', '=', True), ('nap_line_zero', '=', True)]",
        string="Pilih LHM"
    )

    def action_get_data(self):
        """
        Fungsi ini dipanggil saat user menekan tombol 'Dapatkan Data' di wizard.
        Data wizard digunakan untuk menjalankan logika pengambilan dan pemrosesan data.
        """
        lhm_nap_id = self.env.context.get('active_id')
        lhm_nap = self.env['lhm.nap'].browse(lhm_nap_id)
        if lhm_nap:
            selected_lhm_lines = self.env['lhm.transaction.nap.line'].sudo().search([
                ('lhm_id', 'in', self.lhm_ids.ids),
                ('lhm_transaction_line_id.state', '=', 'in_progress'),
                ('lhm_nap_line_id', '=', False),
            ])
            if not selected_lhm_lines:
                raise ValidationError("Tidak bisa menarik data dokumen tersebut dikarenakan dokumen tersebut sudah memiliki data NAP di dalamnya. Harap Proses ulang dokumen yang terkait.")
            lhm_nap.process_data_karet(selected_lhm_lines)

class LhmNapMelonWizard(models.TransientModel):
    _name = 'lhm.nap.melon.wizard'
    _description = 'Wizard untuk Mendapatkan Data Melon'

    lhm_melon_ids = fields.Many2many(
        'lhm.transaction',
        domain="[('nap_line_melon', '=', True), ('nap_line_zero', '=', True)]",
        string="Pilih LHM"
    )

    def action_get_data_melon(self):
        lhm_nap_id = self.env.context.get('active_id')
        lhm_nap = self.env['lhm.nap'].browse(lhm_nap_id)
        if lhm_nap:
            selected_lhm_melons = self.env['lhm.transaction.nap.line'].sudo().search([
                ('lhm_id', 'in', self.lhm_melon_ids.ids),
                ('lhm_transaction_line_id.state', '=', 'in_progress'),
                ('lhm_transaction_line_id.activity_id.is_panen', '=', True),
                ('lhm_transaction_line_id.activity_id.is_nap', '=', True),
                ('lhm_nap_line_id', '=', False),
            ])
            print(selected_lhm_melons)
            if not selected_lhm_melons:
                raise ValidationError("Tidak bisa menarik data dokumen tersebut dikarenakan dokumen tersebut sudah memiliki data NAP di dalamnya. Harap Proses ulang dokumen yang terkait.")
            lhm_nap.process_data_melon(selected_lhm_melons)