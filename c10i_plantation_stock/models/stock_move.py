from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PlantationMaterialAllocation(models.Model):
    _name = 'lhm.material.consumption'
    _description = "Allocation Material"

    stock_move_id = fields.Many2one('stock.move', 'Source Move')
    lhm_id = fields.Many2one('lhm.transaction', string='LHM ID')
    lhm_material_id = fields.Many2one('lhm.transaction.material.line', string='LHM Material ID')
    mr_id = fields.Many2one('material.request', string='MR ID')
    product_qty = fields.Float('Qty Allocated')
    # plantation_partner_activity_material_id = fields.Many2one('plantation.partner.activity.material', string='Material Partner Activity', ondelete='cascade')

class StockMove(models.Model):
    _inherit = 'stock.move'

    cost_allocation_id = fields.Many2one('plantation.cost.type', string='Cost Allocation')
    cost_center_id = fields.Many2one('plantation.cost.center', string='Cost Center', 
        domain="[('type_id','=',cost_allocation_id)]")
    cost_activity_id = fields.Many2one('plantation.cost.activity', string='Activity', 
        domain="[('type_id','=',cost_allocation_id)]")

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

    def action_plantation_stock_move(self):
        for move in self:
            if move.mr_line_id and move.product_id.fertilizer:
                plantation_product = self.env['plantation.stock.product'].search([('product_type','=','fertilizer'),
                    ('related_product_id','=',move.product_id.id)])
                to_create_vals = {}
                if move.location_id.usage=='internal' and move.location_dest_id.usage!='internal':
                    default_move_type = self.env.ref('c10i_plantation.data_stock_move_tipe_fertilizer_receipt')
                    if not default_move_type:
                        default_move_type = self.env['plantation.stock.move'].search([('type','=','incoming'),('product_type','=','fertilizer')])
                    if not default_move_type:
                        raise UserError(_("Could not find Operation Type for Outgoing Fertilizer"))

                    to_create_vals.update({
                        'move_type_id':  default_move_type.id,
                        'product_id' : plantation_product.id,
                        
                        'cost_activity_id' : move.cost_activity_id.id,
                        'dest_cost_center_id' : move.cost_center_id.id,

                        # 'src_picking_id' : x.picking_id.id,
                        'product_qty' : move.product_qty,
                        'date' : move.date
                    })
                # elif move.location_id.usage!='internal' and move.location_dest_id.usage=='internal':
                #     default_move_type = self.env.ref('c10i_plantation.data_stock_move_tipe_fertilizer_return')
                #     if not default_move_type:
                #         default_move_type = self.env['plantation.stock.move'].search([('type','=','outgoing'),('product_type','=','fertilizer')])
                #     if not default_move_type:
                #         raise UserError(_("Could not find Operation Type for Outgoing Fertilizer"))

                #     to_create_vals.update({
                #         'move_type_id':  default_move_type.id,
                #         'product_id' : plantation_product.id,
                        
                #         'cost_activity_id' : move.cost_activity_id.id,
                #         'src_cost_center_id' : move.cost_center_id.id,

                #         # 'src_picking_id' : x.picking_id.id,
                #         'product_qty' : move.product_qty,
                #         'date' : move.date
                #     })
                
                if to_create_vals:
                    pmoves = self.env['plantation.stock.move'].create(to_create_vals)
                    pmoves.action_confirm()
                    pmoves.action_done()

    # def _action_done(self, cancel_backorder=False):
    #     res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
    #     # Spesial custom untuk membuat jurnal dari Penerimaan Pembelian
    #     # Hanya berlaku bagi product non real_type valuation dan product stockable
    #     for move in self:
    #         if move.product_id.valuation == 'real_time' or move.product_id.type != 'product' \
    #                     or not move.purchase_line_id:
    #             continue
    #         for svl in move.stock_valuation_layer_ids:
    #             unit_cost = abs(move._get_price_unit())
    #             value = move.company_id.currency_id.round(unit_cost * svl.quantity)
    #             svl.stock_move_id._account_entry_move_custom(svl.quantity, svl.description, svl.id, value)

    #         # move.action_plantation_stock_move()
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

    # def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
    #     self.ensure_one()
    #     AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

    #     move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
    #     if move_lines:
    #         date = self._context.get('force_period_date', fields.Date.context_today(self))
    #         new_account_move = AccountMove.sudo().create({
    #             'journal_id': journal_id,
    #             'line_ids': move_lines,
    #             'date': date,
    #             'ref': description,
    #             'stock_move_id': self.id,
    #             'operating_unit_id': self.operating_unit_id.id or self.picking_id.operating_unit_id.id,
    #             'stock_valuation_layer_ids': [(6, None, [svl_id])],
    #             'move_type': 'entry',
    #         })
    #         new_account_move._post()
