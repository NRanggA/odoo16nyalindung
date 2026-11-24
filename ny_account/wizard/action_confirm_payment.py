from odoo import models, api, fields, _
from odoo.exceptions import UserError

class WizardActionConfirmPayment(models.TransientModel):
    _name = 'wizard.action.confirm.payment'
    _description = 'Wizard Action Confirm payment'

    confirmation_message = fields.Char(string="Konfirmasi Pembayaran")

    @api.model
    def default_get(self, fields):
        res = super(WizardActionConfirmPayment, self).default_get(fields)
        confirmation_message = self.env.context.get('confirmation_message', '')
        if confirmation_message:
            res.update({'confirmation_message': confirmation_message})
        return res


    # [FIX 24/11/2026 - Task 20] Recheck all selected payments at confirmation.
    def action_confirm(self):
        self.ensure_one()
        if self.env.context.get('active_model') != 'account.payment':
            raise UserError(_('Model pembayaran tidak sesuai.'))
        ids = self.env.context.get('active_ids') or [self.env.context.get('active_id')]
        ids = list(dict.fromkeys(record_id for record_id in ids if record_id))
        payments = self.env['account.payment'].browse(ids).exists()
        if not payments or len(payments) != len(ids):
            raise UserError(_('Semua pembayaran harus masih tersedia dan Draft.'))
        payments._check_payment_confirmation()
        payments.with_context(from_wizard=True).action_post()
        return {'type': 'ir.actions.act_window_close'}
    # [FIX 24/11/2026] END
