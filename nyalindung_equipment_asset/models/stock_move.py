from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"


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
        self.ensure_one()
        am_vals = []
        if self.product_id.product_asset:
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