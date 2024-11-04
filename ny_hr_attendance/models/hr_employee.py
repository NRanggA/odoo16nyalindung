from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    mydaya_user_login = fields.Char()
    mydaya_user_pwd = fields.Char()
    # lat_acuan = fields.Char()
    # long_acuan = fields.Char()
    # value_jarak = fields.Char()