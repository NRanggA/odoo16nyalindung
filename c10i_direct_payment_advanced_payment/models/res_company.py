from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    vendor_advanced_account_id = fields.Many2one('account.account', string='Vendor Advanced Account')
    customer_advanced_account_id = fields.Many2one('account.account', string='Customer Advanced Account')