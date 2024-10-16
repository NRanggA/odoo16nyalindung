from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_skb = fields.Boolean(string="is SKB?")
    no_skb = fields.Char(string="No. SKB")
    masa_berlaku = fields.Date(string="Masa Berlaku")
    taxes_exclude = fields.Many2many('account.tax', string="Taxes Exclude")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id', 'order_id.partner_id')
    def _onchange_product_or_partner(self):
        vendor = self.order_id.partner_id
        domain = [('type_tax_use', '=', 'purchase')]

        if vendor.is_skb:
            excluded_taxes = vendor.taxes_exclude.ids
            domain.append(('id', 'not in', excluded_taxes))

        return {'domain': {'taxes_id': domain}}