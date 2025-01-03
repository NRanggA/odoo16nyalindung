from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    plantation_varieties_id = fields.Many2one('plant.varieties', string="Varietas", ondelete='restrict')
    plantation_location_type_id = fields.Many2one("lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")

    allocation_residual_qty = fields.Float(compute='_compute_residual_qty', store=True, string='Residual Allocation', help='this field only works for Plantation')
    plantation_allocation_ids = fields.One2many('lhm.material.consumption', 'stock_move_id', string='Allocations')

    @api.depends('mr_line_id','state','plantation_allocation_ids')
    def _compute_residual_qty(self):
        for move in self:
            if move.mr_line_id and move.product_id.fertilizer and move.state=='done':
                if move.plantation_allocation_ids:
                    move.allocation_residual_qty = move.product_qty - sum(move.plantation_allocation_ids.mapped('product_qty'))
                else:
                    move.allocation_residual_qty = move.product_qty
            else:
                move.allocation_residual_qty = 0.0

    def _get_accounting_data_for_valuation(self):
        journal_id, acc_src, acc_dest, acc_valuation = super(StockMove, self)._get_accounting_data_for_valuation()
        if self._is_out() and self.plantation_activity_id.account_id:
            acc_dest = self.plantation_activity_id.account_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
    
    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        res = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description)
        res['credit_line_vals']["plantation_varieties_id"] = self.plantation_varieties_id.id
        res['debit_line_vals']["plantation_varieties_id"] = self.plantation_varieties_id.id
        res['credit_line_vals']["plantation_location_type_id"] = self.plantation_location_type_id.id
        res['debit_line_vals']["plantation_location_type_id"] = self.plantation_location_type_id.id
        res['credit_line_vals']["plantation_location_id"] = self.plantation_location_id.id
        res['debit_line_vals']["plantation_location_id"] = self.plantation_location_id.id
        res['credit_line_vals']["plantation_activity_id"] = self.plantation_activity_id.id
        res['debit_line_vals']["plantation_activity_id"] = self.plantation_activity_id.id
        return res

    # def _action_done(self, cancel_backorder=False):
    #     res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
    #     # Spesial custom untuk membuat jurnal dari Penerimaan Pembelian
    #     # Hanya berlaku bagi product non real_type valuation dan product stockable
    #     for move in self:
    #         # if move.product_id.valuation == 'real_time' or move.product_id.type != 'product' \
    #         #             or not move.purchase_line_id:
    #         #     continue
    #         # for svl in move.stock_valuation_layer_ids:
    #         #     unit_cost = abs(move._get_price_unit())
    #         #     value = move.company_id.currency_id.round(unit_cost * svl.quantity)
    #         #     svl.stock_move_id._account_entry_move_custom(svl.quantity, svl.description, svl.id, value)
    #     return res

    # def _account_entry_move_custom(self, qty, description, svl_id, cost):
    #     """ Accounting Valuation Entries """
    #     self.ensure_one()
    #     if self.restrict_partner_id:
    #         # if the move isn't owned by the company, we don't make any valuation
    #         return False

    #     company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
    #     company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

    #     journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
    #     # Create Journal Entry for products arriving in the company; in case of routes making the link between several
    #     # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
    #     # print(">>>>>>>>>>>>>>>>>>>PLANTATION_STOCK", cost, journal_id, acc_src, acc_dest, acc_valuation)
    #     if self._is_in():
    #         if self._is_returned(valued_type='in'):
    #             self.with_company(company_to)._create_account_move_line(acc_dest, acc_valuation, journal_id, qty, description, svl_id, cost)
    #         else:
    #             self.with_company(company_to)._create_account_move_line(acc_src, acc_valuation, journal_id, qty, description, svl_id, cost)

    #     # Create Journal Entry for products leaving the company
    #     if self._is_out():
    #         cost = -1 * cost
    #         if self._is_returned(valued_type='out'):
    #             self.with_company(company_from)._create_account_move_line(acc_valuation, acc_src, journal_id, qty, description, svl_id, cost)
    #         else:
    #             self.with_company(company_from)._create_account_move_line(acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost)

    #     if self.company_id.anglo_saxon_accounting:
    #         # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
    #         self._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=self.product_id)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        fields = [
            'product_id', 'price_unit', 'procure_method', 'location_id', 'location_dest_id',
            'product_uom', 'restrict_partner_id', 'scrapped', 'origin_returned_move_id',
            'package_level_id', 'propagate_cancel', 'description_picking',
            'product_packaging_id',
        ]
        if self.mr_line_id:
            fields.extend(['plantation_varieties_id',
                'plantation_location_type_id',
                'plantation_location_id',
                'plantation_activity_id'])
        return fields