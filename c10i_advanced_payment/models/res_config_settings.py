from odoo import _, api, fields, models

class Config(models.TransientModel):
    _inherit = 'res.config.settings'

    vendor_advanced_account_id = fields.Many2one('account.account', string='Vendor Advanced Account', related='company_id.vendor_advanced_account_id', readonly=False)
    customer_advanced_account_id = fields.Many2one('account.account', string='Customer Advanced Account', related='company_id.customer_advanced_account_id', readonly=False)
