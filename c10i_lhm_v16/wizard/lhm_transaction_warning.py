from odoo import models, fields, api, _

class LhmTransactionWarningWizard(models.TransientModel):
    _name = 'lhm.transaction.warning.wizard'
    _description = 'Warning Wizard for Invalid Employees in LHM'

    message = fields.Text("Warning Message", readonly=True)
    invalid_employee_ids = fields.Many2many("hr.employee", string="Invalid Employees", readonly=True)

    def action_continue(self):
        # Mengambil 'active_id' dari context untuk menentukan transaksi yang aktif
        active_id = self.env.context.get('active_id')
        transaction = self.env['lhm.transaction'].browse(active_id)

        # Lanjutkan eksekusi dari run_progress
        transaction.run_progress()

        # Tutup wizard setelah melanjutkan proses
        return {'type': 'ir.actions.act_window_close'}