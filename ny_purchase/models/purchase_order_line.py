from odoo import models, fields, api
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # def _get_gross_price_unit(self):
    #     price_unit = super()._get_gross_price_unit()
    #     if self.order_id.non_credit:
    #         price_unit = self.price_unit
    #         if self.taxes_id:
    #             qty = self.product_qty or 1
    #             price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
    #             tax_result = self.taxes_id.with_context(round=False).compute_all(price_unit, currency=self.order_id.currency_id, quantity=qty)
    #             price_unit_including_tax = tax_result['total_included'] / qty
    #             price_unit = float_round(price_unit_including_tax, precision_digits=price_unit_prec)
    #         if self.product_uom.id != self.product_id.uom_id.id:
    #             price_unit *= self.product_uom.factor / self.product_id.uom_id.factor

    #     return price_unit

    # def _prepare_account_move_line(self, move=False):
    #     res = super()._prepare_account_move_line(move=move)
    #     if self.order_id.non_credit:
    #         aml_currency = move.currency_id if move else self.currency_id
    #         date = move.date if move else fields.Date.today()
    #         price_unit = self.price_unit
    #         if self.taxes_id:
    #             tax_result = self.taxes_id.compute_all(price_unit, currency=self.order_id.currency_id, quantity=self.qty_to_invoice)
    #             price_unit_including_tax = tax_result['total_included'] / self.qty_to_invoice
    #             price_unit = float_round(price_unit_including_tax, precision_digits=self.env['decimal.precision'].precision_get('Product Price'))
    #         res = {
    #             'display_type': self.display_type or 'product',
    #             'name': '%s: %s' % (self.order_id.name, self.name),
    #             'product_id': self.product_id.id,
    #             'product_uom_id': self.product_uom.id,
    #             'quantity': self.qty_to_invoice,
    #             'price_unit': self.currency_id._convert(price_unit, aml_currency, self.company_id, date, round=False),
    #             'tax_ids': False,
    #             'purchase_line_id': self.id,
    #         }
    #         if self.analytic_distribution and not self.display_type:
    #             res['analytic_distribution'] = self.analytic_distribution
    #     return res

    def _get_gross_price_unit(self):
        price_unit = super()._get_gross_price_unit()
        if self.order_id.non_credit:
            price_unit = self.price_unit
            ppn_taxes = self.taxes_id.filtered(lambda tax: 'PPN' in tax.name)
            if ppn_taxes:
                qty = self.product_qty or 1
                price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
                tax_result = ppn_taxes.with_context(round=False).compute_all(price_unit, currency=self.order_id.currency_id, quantity=qty)
                price_unit_including_tax = tax_result['total_included'] / qty
                price_unit = float_round(price_unit_including_tax, precision_digits=price_unit_prec)
            if self.product_uom.id != self.product_id.uom_id.id:
                price_unit *= self.product_uom.factor / self.product_id.uom_id.factor

        return price_unit
    
    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move=move)
        if self.order_id.non_credit:
            aml_currency = move.currency_id if move else self.currency_id
            date = move.date if move else fields.Date.today()
            price_unit = self.price_unit
            ppn_taxes = self.taxes_id.filtered(lambda tax: 'PPN' in tax.name)
            non_ppn_taxes = self.taxes_id - ppn_taxes
            
            res = {
                'display_type': self.display_type or 'product',
                'name': '%s: %s' % (self.order_id.name, self.name),
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'quantity': self.qty_to_invoice,
                'price_unit': self.currency_id._convert(price_unit, aml_currency, self.company_id, date, round=False),
                'tax_ids': [(6, 0, non_ppn_taxes.ids)],  # Hanya pajak yang bukan PPN
                'purchase_line_id': self.id,
            }
            if self.analytic_distribution and not self.display_type:
                res['analytic_distribution'] = self.analytic_distribution
            
        return res
    
    # def action_create_invoice(self):
    #     res = super(action_create_invoice)
    
    # def _prepare_account_move_line(self, move=False):
    #     res = super()._prepare_account_move_line()
    #     if self.order_id.non_credit:
    #         aml_currency = move and move.currency_id or self.currency_id
    #         date = move and move.date or fields.Date.today()
    #         res = {
    #             'display_type': self.display_type or 'product',
    #             'name': '%s: %s' % (self.order_id.name, self.name),
    #             'product_id': self.product_id.id,
    #             'product_uom_id': self.product_uom.id,
    #             'quantity': self.qty_to_invoice,
    #             'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
    #             'tax_ids': False,
    #             'purchase_line_id': self.id,
    #         }
    #         if self.analytic_distribution and not self.display_type:
    #             res['analytic_distribution'] = self.analytic_distribution
    #     return res

#    def _get_gross_price_unit(self):
#         self.ensure_one()
#         price_unit = self.price_unit
#         if self.taxes_id:
#             qty = self.product_qty or 1
#             price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
#             price_unit = self.taxes_id.with_context(round=False).compute_all(price_unit, currency=self.order_id.currency_id, quantity=qty)['total_void']
#             price_unit = float_round(price_unit / qty, precision_digits=price_unit_prec)
#         if self.product_uom.id != self.product_id.uom_id.id:
#             price_unit *= self.product_uom.factor / self.product_id.uom_id.factor
#         return price_unit


