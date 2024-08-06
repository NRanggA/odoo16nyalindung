from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id')

    @api.depends('product_id', 'quantity', 'product_uom_id', 'move_id.pricelist_id')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or not line.move_id.pricelist_id:
                line.pricelist_item_id = False
                line.price_unit = 0.0
            else:
                line.pricelist_item_id = line.move_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.quantity or 1.0,
                    uom=line.product_uom_id,
                    date=line.move_id.invoice_date,
                )

    @api.depends('product_id', 'product_uom_id')
    def _compute_price_unit(self):
        res = super(AccountMoveLine, self)._compute_price_unit()
        for line in self:
            if line.pricelist_item_id:
                line.price_unit = line.pricelist_item_id.fixed_price
        return res
            
    # def _set_price_from_pricelist(self):
    #     for line in self:
    #         if line.pricelist_item_id:j
    #             order_date = line.move_id.invoice_date or fields.Date.today()
    #             product = line.product_id
    #             qty = line.quantity or 1.0
    #             uom = line.product_uom_id or line.product_id.uom_id
    #             currency = line.currency_id or line.move_id.company_id.currency_id

    #             price = line.pricelist_item_id._compute_price(
    #                 product, qty, uom, order_date, currency=currency)
    #             line.price_unit = price    

    # def _get_pricelist_price(self):
    #     self.ensure_one()
    #     self.product_id.ensure_one()

    #     grade = self.move_id.pricelist_id
    #     pricelist_rule = self.pricelist_item_id
    #     if grade and self.product_id in grade.item_ids.product_id.ids:

    #     for line in self:
    #         if not line.product_id or line.display_type in ('line_section', 'line_note'):
    #             continue
    #         if line.move_id.is_sale_document(include_receipts=True):
    #             document_type = 'sale'
    #         elif line.move_id.is_purchase_document(include_receipts=True):
    #             document_type = 'purchase'
    #         else:
    #             document_type = 'other'
    #         line.price_unit = line.product_id._get_tax_included_unit_price(
    #             line.move_id.company_id,
    #             line.move_id.currency_id,
    #             line.move_id.date,
    #             document_type,
    #             fiscal_position=line.move_id.fiscal_position_id,
    #             product_uom=line.product_uom_id,
    #         )
    #     return price