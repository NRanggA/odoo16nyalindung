from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    pricelist_id = fields.Many2one('product.pricelist', string='Grading')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = self.env['product.pricelist'].search([('partner_id', '=', self.partner_id.id)], limit=1)
        else:
            self.pricelist_id = False

    # @api.model
    # def _recompute_tax_lines(self, recompute_tax_base_amount=False):
    #     super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount)

    #     for line in self.invoice_line_ids:
    #         customer = self.partner_id
    #         if customer.l10n_id_pkp and customer.l10n_id_kode_transaksi == '08':
    #             line.tax_ids = [(6, 0, [])]

    #     self.line_ids = self.line_ids.filtered(lambda l: not l.tax_line_id)