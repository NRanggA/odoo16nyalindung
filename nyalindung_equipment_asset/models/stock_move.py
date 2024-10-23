from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        self.ensure_one()

        # Get the threshold value from settings
        threshold = self.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold_from', default=0)
        
        # Prepare debit and credit line values
        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'balance': debit_value,
            'account_id': debit_account_id,
        }

        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'balance': -credit_value,
            'account_id': credit_account_id,
        }
        if self.picking_type_id.code=='issue':
            credit_line_vals.update({
                'plantation_varieties_id': self.plantation_varieties_id.id,
                'plantation_location_type_id': self.plantation_location_type_id.id,
                'plantation_location_id': self.plantation_location_id.id,
                'plantation_activity_id': self.plantation_activity_id.id,
            })

        # Initialize the result dictionary
        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}

        # Get the associated purchase order line if available
        purchase_order_line = self.purchase_line_id
        asset_category = self.purchase_line_id.product_id.categ_id.asset


        # Check if there is an associated purchase order line and retrieve the product price
        if purchase_order_line:
            order_line_price = purchase_order_line.price_unit  # Get the price from the order line

            # Check if the order line price is below the threshold
            if asset_category and order_line_price < float(threshold):
                expense_account_id = self.product_id.categ_id.property_account_expense_categ_id.id
                if not expense_account_id:
                    raise UserError(_('No expense account defined for this product category.'))

                # Create additional debit and credit lines
                additional_debit_line_vals = {
                    'name': description,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': description,
                    'partner_id': partner_id,
                    'balance': debit_value,  # You may want to set a specific value for expense
                    'account_id': expense_account_id,
                }
                additional_credit_line_vals = {
                    'name': description,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': description,
                    'partner_id': partner_id,
                    'balance': -credit_value,  # You may want to set a specific value for expense
                    'account_id': expense_account_id,
                }

                rslt['additional_debit_line_vals'] = additional_debit_line_vals
                rslt['additional_credit_line_vals'] = additional_credit_line_vals

        # Handle price difference if needed
        if credit_value != debit_value:
            diff_amount = debit_value - credit_value
            price_diff_account = self.env.context.get('price_diff_account')
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }

        return rslt


    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        self = self.with_company(self.company_id)
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

        acc_src = self._get_src_account(accounts_data)
        acc_dest = self._get_dest_account(accounts_data)

        # Custom logic to check for asset field in category
        if self.product_id.product_asset and self.product_id.categ_id.asset:
            acc_valuation = accounts_data.get('stock_asset', False)
        else:
            acc_valuation = accounts_data.get('stock_valuation', False)

        if acc_valuation:
            acc_valuation = acc_valuation.id

        if not accounts_data.get('stock_journal', False):
            raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
        if not acc_src:
            raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_dest:
            raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_valuation:
            raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
        journal_id = accounts_data['stock_journal'].id
        return journal_id, acc_src, acc_dest, acc_valuation
    

    def _account_entry_move(self, qty, description, svl_id, cost):
        """ Accounting Valuation Entries """
        res = super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)
        # self.ensure_one()
        if self.product_id.product_asset:
            am_vals = []
            if self.restrict_partner_id and self.restrict_partner_id != self.company_id.partner_id:
                # if the move isn't owned by the company, we don't make any valuation
                return am_vals

            company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
            company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            # Create Journal Entry for products arriving in the company; in case of routes making the link between several
            # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
            if self._is_in():
                if self._is_returned(valued_type='in'):
                    am_vals.append(self.with_company(company_to)._prepare_account_move_vals(acc_dest, acc_valuation, journal_id, qty, description, svl_id, cost))
                else:
                    am_vals.append(self.with_company(company_to)._prepare_account_move_vals(acc_src, acc_valuation, journal_id, qty, description, svl_id, cost))

            # Create Journal Entry for products leaving the company
            if self._is_out():
                cost = -1 * cost
                if self._is_returned(valued_type='out'):
                    am_vals.append(self.with_company(company_from)._prepare_account_move_vals(acc_valuation, acc_src, journal_id, qty, description, svl_id, cost))
                else:
                    am_vals.append(self.with_company(company_from)._prepare_account_move_vals(acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost))

            if self.company_id.anglo_saxon_accounting:
                # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
                if self._is_dropshipped():
                    if cost > 0:
                        am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(acc_src, acc_valuation, journal_id, qty, description, svl_id, cost))
                    else:
                        cost = -1 * cost
                        am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost))
                elif self._is_dropshipped_returned():
                    if cost > 0:
                        am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(acc_valuation, acc_src, journal_id, qty, description, svl_id, cost))
                    else:
                        cost = -1 * cost
                        am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(acc_dest, acc_valuation, journal_id, qty, description, svl_id, cost))

            return am_vals
        else:
            return res