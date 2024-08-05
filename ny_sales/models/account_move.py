from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    pricelist_id = fields.Many2one('product.pricelist', string='Grade')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = self.env['product.pricelist'].search([('partner_id', '=', self.partner_id.id)], limit=1)
        else:
            self.pricelist_id = False
