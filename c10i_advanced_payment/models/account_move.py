from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    # advanced_purchase_id = fields.Many2one('purchase.order', string='Advanced Purchase')
    is_advanced = fields.Boolean('Is Advanced')

    has_advanced = fields.Boolean('Has Advanced')
    advanced_purchase_id = fields.Many2one('purchase.order', string='Advance Vendor')
    advanced_sales_id = fields.Many2one('sale.order', string='Advance Customer')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')


    def _prepare_advanced_lines(self,advanced_line,advanced_move_id=False,move_id=False):
        self.ensure_one()
        res = {
            'display_type': advanced_line.display_type,
            'sequence': advanced_line.sequence,
            'name': advanced_line.name,
            'product_id': advanced_line.product_id.id,
            'product_uom_id': advanced_line.product_uom_id.id,
            'quantity': advanced_line.quantity,
            'account_id': advanced_line.account_id.id,
            'price_unit': -advanced_line.price_unit,
            'tax_ids': [(6, 0, advanced_line.tax_ids.ids)],
            'analytic_account_id': advanced_line.analytic_account_id.id,
            # 'debit': advanced_line.price_unit,
            'analytic_tag_ids': [(6, 0, advanced_line.analytic_tag_ids.ids)],
        }
        if advanced_move_id:
            res.update({"advanced_move_id": advanced_move_id.move_id.id})
            res.update({"advanced_move_line_id": advanced_move_id.id})
        return res
    
    def action_post(self):
        res = super(AccountMove,self).action_post()
        if self.has_advanced:
            if self.move_type in ('in_invoice','out_invoice'):
                
                advanced = self.invoice_line_ids.filtered(lambda x: x.advanced_move_id)
                dp = advanced.advanced_move_line_id
                if advanced and dp:
                    (dp + advanced).reconcile()

            # elif self.move_type == 'out_invoice':
            #     customer_advanced = self.invoice_line_ids.filtered(lambda x: x.advanced_move_id)
            #     vendor_dp = vendor_advanced.advanced_move_line_id
            #     if customer_advanced and vendor_dp:
            #         (vendor_dp + vendor_advanced).reconcile()

        return res
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        res = super(AccountMove,self)._compute_amount()
        for move in self:        
            amount = 0
            for this in move.invoice_line_ids:
                if not this.advanced_move_id:
                    amount += this.price_subtotal
                    move.amount_residual = amount
                    move.amount_total = amount            
        return res

    

    def action_add_advanced(self):
        advanced_ids = False
        advanced_lines = []
        self.has_advanced = True
        if self.move_type == 'in_invoice':
            purchase_id = self.invoice_line_ids.filtered(lambda x: x.purchase_order_id.id)
            if purchase_id:

                advanced_ids = self.env['account.move'].search([('advanced_purchase_id', '=', purchase_id[0].purchase_order_id.id),('is_advanced', '=', True)])
                for advanced_id in advanced_ids.invoice_line_ids:

                    advanced_lines.append((0,0,self._prepare_advanced_lines(advanced_id,advanced_move_id=advanced_id)))

                self.write({'invoice_line_ids':advanced_lines})
                
                    
        elif self.move_type == 'out_invoice':
            if self.sale_order_id:
                advanced_ids = self.env['account.move'].search([('advanced_sales_id', '=', self.sale_order_id.id),('is_advanced', '=', True)])
                for advanced_id in advanced_ids.invoice_line_ids:

                    advanced_lines.append((0,0,self._prepare_advanced_lines(advanced_id,advanced_move_id=advanced_id)))

                self.write({'invoice_line_ids':advanced_lines})        
        



    def action_remove_advanced(self):
        self.has_advanced = False
        advanced_ids = self.invoice_line_ids.filtered(lambda x: x.advanced_move_id)
        if advanced_ids:
            for advanced_id in advanced_ids:
                self.write({'invoice_line_ids':[(2,advanced_id.id,0)]})
            



    # @api.onchange('has_advanced')
    # def _onchange_has_advanced(self):
    #     advanced_ids = False
    #     advanced_lines = []
    #     a = self.test_test()
    #     if self.has_advanced:
    #         if self.move_type == 'in_invoice':
    #             purchase_id = self.invoice_line_ids.filtered(lambda x: x.purchase_order_id.id)
    #             if purchase_id:

    #                 advanced_ids = self.env['account.move'].search([('advanced_purchase_id', '=', purchase_id[0].purchase_order_id.id),('is_advanced', '=', True)])
    #                 for advanced_id in advanced_ids.invoice_line_ids:

    #                     advanced_lines.append((0,0,self._prepare_advanced_lines(advanced_id,advanced_move_id=advanced_id)))

    #                     print(">>>>>>>>>>>>>>>>>>>>>>>>>",advanced_lines)
    #                 self._origin.write({'invoice_line_ids':advanced_lines})
    #                 # self._origin.line_ids._onchange_price_subtotal()
    #                 # self._origin._onchange_invoice_line_ids()
    #                 # self._origin._check_balanced()
                    
    #         elif self.move_type == 'out_invoice':
    #             pass
    #         pass

    # @api.model
    # def default_get(self, fields):
    #     vals = super(AccountMove,self).default_get(fields)
    #     print("===================",vals)
    #     return vals
            

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    advanced_purchase_id = fields.Many2one('purchase.order', string='Advanced Vendor')
    advanced_sales_id = fields.Many2one('sale.order', string='Advanced Customer')
    advanced_move_id = fields.Many2one('account.move', string='Advanced Move')
    advanced_move_line_id = fields.Many2one('account.move.line', string='Advanced Move Line')
    is_advanced = fields.Boolean('Is Advanced')
    
    # order_id = fields.Many2one('purchase.order', string='Order Advanced')

    @api.model
    def default_get(self, fields):
        vals = super(AccountMoveLine,self).default_get(fields)
        if 'account_id' in vals:
            if 'advanced_purchase' in self._context:
                account_id = vals.get('account_id')
                vals['account_id'] = self.env.company.vendor_advanced_account_id.id if self.env.company.vendor_advanced_account_id else account_id
                vals['advanced_purchase_id'] = self._context.get('active_id')
            elif 'advanced_sales' in self._context:
                account_id = vals.get('account_id')
                vals['account_id'] = self.env.company.customer_advanced_account_id.id if self.env.company.customer_advanced_account_id else account_id
                vals['advanced_sales_id'] = self._context.get('active_id')

        return vals

   