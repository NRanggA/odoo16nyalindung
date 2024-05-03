from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    cal_api_key     = fields.Char("Google API Keys")
    cal_id_google   = fields.Char("CalendarId")