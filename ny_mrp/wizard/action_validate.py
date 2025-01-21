from odoo import models, api, fields, _

class WizardActionValidate(models.TransientModel):
    _name = 'wizard.action.validate'
    _description = 'Wizard Action Validate Manufacturing Order'

    confirmation_message = fields.Char(string="Konfirmasi Pembayaran")

    @api.model
    def default_get(self, fields):
        res = super(WizardActionValidate, self).default_get(fields)
        confirmation_message = self.env.context.get('confirmation_message', '')
        if confirmation_message:
            res.update({'confirmation_message': confirmation_message})
        return res


    def action_confirm(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'mrp.production':
            manufacture_record = self.env[active_model].browse(active_id)
            return manufacture_record.with_context(from_wizard=True).button_mark_done()
            
        # return {'type': 'ir.actions.act_window_close'}