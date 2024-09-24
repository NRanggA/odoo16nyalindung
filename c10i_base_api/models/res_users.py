from odoo import fields, models, api

class APIKeys(models.Model):
    _inherit = 'res.users.apikeys'

	def _check_credentials(self, *, scope, key):
		return super()._check_credentials(scope=scope, key=key)