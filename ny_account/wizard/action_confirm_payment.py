from odoo import models, api, fields, _

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


    def action_confirm(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'account.payment':
            payment_record = self.env[active_model].browse(active_id)
            # if payment_record.employee_expense_id:
            payment_record.with_context(from_wizard=True).action_post()
            
        return {'type': 'ir.actions.act_window_close'}