from odoo import models, api

class ChangePasswordOwn(models.TransientModel):
    _inherit = 'change.password.own'

    @api.model
    def toggle_password_visibility(self, **kwargs):
        self.env['ir.logging'].sudo().create({
            'type': 'server',
            'name': 'Mata Dajjal',
            'message': 'User toggled the visibility of the password field',
            'level': 'info',
            'path': 'change.password.own',
            'func': 'toggle_password_visibility',
            'line': 0,
        })
        return True
