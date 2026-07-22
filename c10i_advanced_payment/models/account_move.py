from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    # advanced_purchase_id = fields.Many2one('purchase.order', string='Advanced Purchase')
    is_advanced = fields.Boolean('Is Advanced')

    has_advanced = fields.Boolean('Has Advanced')
    advanced_purchase_id = fields.Many2one('purchase.order', string='Advance PO')
    advanced_sales_id = fields.Many2one('sale.order', string='Advance Customer')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    is_po_advanced = fields.Boolean('is PO Advanced', compute='get_po_advanced', store=True)
    vendor_advanced_account_id = fields.Many2one('account.account', string='Vendor Advanced Account', related='company_id.vendor_advanced_account_id')


    # Tambah field amount residual
    advance_residual = fields.Monetary(
        string='Advance Residual',
        compute='_compute_advance_residual',
        currency_field='currency_id',
        store=True
    )

    # @api.depends('line_ids.account_id', 'line_ids.amount_residual')
    # def _compute_advance_residual(self):
    #     purchase_advance_account = self.env.company.vendor_advanced_account_id
    #     if not purchase_advance_account:
    #         raise ValidationError(_('Please configure Purchase Advance Account on your Accounting Settings'))

    #     for move in self:
    #         move.advance_residual = 0.0
    #         if not move.is_advanced and not move.has_advanced:
    #             continue

    #         advance_lines = move.line_ids.filtered(lambda l: l.account_id == purchase_advance_account)
    #         # move.advance_residual = sum(advance_lines.mapped('amount_residual'))
            
    #         residual_total = 0.0
            
    #         for line in advance_lines:
    #             credit_balance_total = 0.0
    #             partials = line.matched_debit_ids

    #             if not partials:
    #                 move.advance_residual =  line.amount_residual

    #                 print(f"==== Tidak ada reconcile : {move.advance_residual} ====")
    #                 # print(f"==== Tidak ada reconcile : {mo} ====")
    #                 continue

    #             for partial in partials:
    #                 credit_balance_total += partial.credit_move_id.balance
                
    #             final_residual = line.amount_residual - credit_balance_total
    #             residual_total += final_residual
            
    #         move.advance_residual = residual_total

    #         print(f"Advance Residual for move {move.name}: {move.advance_residual}")

    # @api.depends(
    # 'line_ids.account_id',
    # 'line_ids.amount_residual',
    # )
    # def _compute_advance_residual(self):
    #     purchase_advance_account = self.env.company.vendor_advanced_account_id
    #     if not purchase_advance_account:
    #         raise ValidationError(_('Please configure Purchase Advance Account on your Accounting Settings'))

    #     for move in self:
    #         move.advance_residual = 0.0

    #         if not move.is_advanced and not move.has_advanced:
    #             continue

    #         residual_total = 0.0
    #         advance_lines = move.line_ids.filtered(lambda l: l.account_id == purchase_advance_account)

    #         for line in advance_lines:
    #             partials = line.matched_debit_ids

    #             if not partials:
    #                 residual_total += line.amount_residual
    #                 continue

    #             total_reconciled = sum(part.credit_move_id.balance for part in partials)
    #             final_residual = line.balance - total_reconciled
    #             residual_total += final_residual

    #         move.advance_residual = residual_total


    @api.depends(
        'line_ids.account_id',
        'line_ids.amount_residual',
        'state',
    )
    def _compute_advance_residual(self):
        purchase_advance_account = self.env.company.vendor_advanced_account_id
        if not purchase_advance_account:
            raise ValidationError(_('Please configure Purchase Advance Account on your Accounting Settings'))

        for move in self:
            # Default value
            move.advance_residual = 0.0

            # Skip kalau masih draft atau bukan advance
            if move.state != 'posted':
                continue

            if not move.is_advanced and not move.has_advanced:
                continue

            residual_total = 0.0
            advance_lines = move.line_ids.filtered(lambda l: l.account_id == purchase_advance_account)

            for line in advance_lines:
                partials = line.matched_debit_ids

                if not partials:
                    residual_total += line.amount_residual
                    continue

                total_reconciled = sum(part.credit_move_id.balance for part in partials)
                final_residual = line.balance - total_reconciled
                residual_total += final_residual

            move.advance_residual = residual_total




    def _prepare_advanced_lines(self,advanced_line,advanced_move_id=False,move_id=False):
        self.ensure_one()
        res = {
            'display_type': advanced_line.display_type,
            'sequence': advanced_line.sequence,
            'name': advanced_line.name,
            'product_id': advanced_line.product_id.id,
            'product_uom_id': advanced_line.product_uom_id.id,
            'quantity': 1,
            'account_id': advanced_line.account_id.id,
            'price_unit': -advanced_line.move_id.advance_residual,
            'tax_ids': [(6, 0, advanced_line.tax_ids.ids)],
            # 'analytic_account_id': advanced_line.analytic_account_id.id,
            # 'debit': advanced_line.price_unit,
            # 'analytic_tag_ids': [(6, 0, advanced_line.analytic_tag_ids.ids)],
        }
        if advanced_move_id:
            res.update({"advanced_move_id": advanced_move_id.move_id.id})
            res.update({"advanced_move_line_id": advanced_move_id.id})
        return res
    
    def action_post(self):
        res = super(AccountMove,self).action_post()
        for move in self:
            if move.has_advanced:
                if move.move_type in ('in_invoice','out_invoice'):
                    
                    advanced = move.invoice_line_ids.filtered(lambda x: x.advanced_move_id)
                    dp = advanced.advanced_move_line_id
                    if advanced and dp:
                        (dp + advanced).reconcile()

            # elif self.move_type == 'out_invoice':
            #     customer_advanced = self.invoice_line_ids.filtered(lambda x: x.advanced_move_id)
            #     vendor_dp = vendor_advanced.advanced_move_line_id
            #     if customer_advanced and vendor_dp:
            #         (vendor_dp + vendor_advanced).reconcile()

        return res
    
    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id')
    # def _compute_amount(self):
    #     res = super(AccountMove,self)._compute_amount()
    #     for move in self:        
    #         amount = 0
    #         for this in move.invoice_line_ids:
    #             if not this.advanced_move_id:
    #                 amount += this.price_subtotal
    #                 move.amount_residual = amount
    #                 move.amount_total = amount            
    #     return res

    

    def action_add_advanced(self):
        advanced_ids = False
        advanced_lines = []
        self.has_advanced = True
        if self.move_type == 'in_invoice':
            purchase_id = self.invoice_line_ids.filtered(lambda x: x.purchase_order_id.id)
            if purchase_id:

                advanced_ids = self.env['account.move'].search([('advanced_purchase_id', '=', purchase_id[0].purchase_order_id.id),('is_advanced', '=', True),('state', '=', 'posted')])
                for advanced_id in advanced_ids.invoice_line_ids:

                    advanced_lines.append((0,0,self._prepare_advanced_lines(advanced_id,advanced_move_id=advanced_id)))

                self.write({'invoice_line_ids':advanced_lines})
                
                    
        elif self.move_type == 'out_invoice':
            if self.sale_order_id:
                advanced_ids = self.env['account.move'].search([('advanced_sales_id', '=', self.sale_order_id.id),('is_advanced', '=', True),('state', '=', 'posted')])
                for advanced_id in advanced_ids.invoice_line_ids:

                    advanced_lines.append((0,0,self._prepare_advanced_lines(advanced_id,advanced_move_id=advanced_id)))

                self.write({'invoice_line_ids':advanced_lines})        
        



    def action_remove_advanced(self):
        self.has_advanced = False
        advanced_ids = self.invoice_line_ids.filtered(lambda x: x.advanced_move_id)
        if advanced_ids:
            for advanced_id in advanced_ids:
                self.write({'invoice_line_ids':[(2,advanced_id.id,0)]})

    # def action_register_payment(self):
    #     ''' Open the account.payment.register wizard to pay the selected journal entries.
    #     :return: An action opening the account.payment.register wizard.
    #     '''
    #     return {
    #         'name': _('Register Payment'),
    #         'res_model': 'account.payment.register',
    #         'view_mode': 'form',
    #         'context': {
    #             'active_model': 'account.move',
    #             'active_ids': self.ids,
    #             'default_payment_line_ids' : [(0,0,{ 
    #                 'move_id' : self.id,
    #                 'origin' : self.name,
    #                 'invoice_date' : self.date,
    #                 'amount_to_pay' : self.amount_residual
    #             })]
    #         },
    #         'target': 'new',
    #         'type': 'ir.actions.act_window',
    #     }

    # @api.onchange('advanced_purchase_id')
    # def _onchange_line_move_lines(self):
    #     if self.advanced_purchase_id:
    #         # self.invoice_line_ids = [(5, 0, 0)]
    #         line_vals = []
    #         for line in self.advanced_purchase_id.order_line:
    #             if line not in line_vals:
    #                 line_vals.append((0, 0, {
    #                     'order_line_id' : line.id,
    #                     'product_id': line.product_id.id,
    #                     'purchase_order_id': line.order_id.id,
    #                     'quantity': line.product_qty,
    #                     'price_unit': line.price_unit,
    #                     'tax_ids': [(6, 0, line.taxes_id.ids)],
    #                 }))
    #         self.invoice_line_ids = line_vals

    @api.depends('invoice_line_ids')
    def get_po_advanced(self):
        for record in self:
            record.is_po_advanced = False
            for line in record.invoice_line_ids:
                if any(line and line.purchase_order_id) and line.purchase_order_id.count_advanced_purchase > 0:
                    record.is_po_advanced = True


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
    # order_line_id = fields.Many2one('purchase.order.line', string='Order Line')
    
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
    
    # PUNYA RISFAN
    # @api.depends('display_type', 'company_id')
    # def _compute_account_id(self):
    #     if self.move_id.is_advanced:
    #         term_lines = self.filtered(lambda line: line.display_type == 'payment_term')
    #         if term_lines:
    #             moves = term_lines.move_id
    #             self.env.cr.execute("""
    #                 WITH previous AS (
    #                     SELECT DISTINCT ON (line.move_id)
    #                         'account.move' AS model,
    #                         line.move_id AS id,
    #                         NULL AS account_type,
    #                         line.account_id AS account_id
    #                     FROM account_move_line line
    #                     WHERE line.move_id = ANY(%(move_ids)s)
    #                     AND line.display_type = 'payment_term'
    #                     AND line.id != ANY(%(current_ids)s)
    #                 ),
    #                 properties AS(
    #                     SELECT DISTINCT ON (property.company_id, property.name)
    #                         'res.partner' AS model,
    #                         SPLIT_PART(property.res_id, ',', 2)::integer AS id,
    #                         CASE
    #                             WHEN property.name = 'property_account_receivable_id' THEN 'asset_receivable'
    #                             ELSE 'liability_payable'
    #                         END AS account_type,
    #                         SPLIT_PART(property.value_reference, ',', 2)::integer AS account_id
    #                     FROM ir_property property
    #                     JOIN res_company company ON property.company_id = company.id
    #                     WHERE property.name IN ('property_account_receivable_id', 'property_account_payable_id')
    #                     AND property.company_id = ANY(%(company_ids)s)
    #                     AND property.res_id = ANY(%(partners)s)
    #                 ORDER BY property.company_id, property.name, account_id
    #                 ),
    #                 default_properties AS(
    #                     SELECT DISTINCT ON (property.company_id, property.name)
    #                         'res.partner' AS model,
    #                         company.partner_id AS id,
    #                         CASE
    #                             WHEN property.name = 'property_account_receivable_id' THEN 'asset_receivable'
    #                             ELSE 'liability_payable'
    #                         END AS account_type,
    #                         SPLIT_PART(property.value_reference, ',', 2)::integer AS account_id
    #                     FROM ir_property property
    #                     JOIN res_company company ON property.company_id = company.id
    #                     WHERE property.name IN ('property_account_receivable_id', 'property_account_payable_id')
    #                     AND property.company_id = ANY(%(company_ids)s)
    #                     AND property.res_id IS NULL
    #                 ORDER BY property.company_id, property.name, account_id
    #                 ),
    #                 fallback AS (
    #                     SELECT DISTINCT ON (account.company_id, account.account_type)
    #                         'res.company' AS model,
    #                         account.company_id AS id,
    #                         account.account_type AS account_type,
    #                         account.id AS account_id
    #                     FROM account_account account
    #                     WHERE account.company_id = ANY(%(company_ids)s)
    #                     AND account.account_type IN ('asset_receivable', 'liability_payable')
    #                 )
    #                 SELECT * FROM previous
    #                 UNION ALL
    #                 SELECT * FROM properties
    #                 UNION ALL
    #                 SELECT * FROM default_properties
    #                 UNION ALL
    #                 SELECT * FROM fallback
    #             """, {
    #                 'company_ids': moves.company_id.ids,
    #                 'move_ids': moves.ids,
    #                 'partners': [f'res.partner,{pid}' for pid in moves.commercial_partner_id.ids],
    #                 'current_ids': term_lines.ids
    #             })
    #             accounts = {
    #                 (model, id, account_type): account_id
    #                 for model, id, account_type, account_id in self.env.cr.fetchall()
    #             }
    #             for line in term_lines:
    #                 account_type = 'asset_receivable' if line.move_id.is_sale_document(include_receipts=True) else 'liability_payable'
    #                 move = line.move_id
    #                 account_id = (
    #                     accounts.get(('account.move', move.id, None))
    #                     or accounts.get(('res.partner', move.commercial_partner_id.id, account_type))
    #                     or accounts.get(('res.partner', move.company_id.partner_id.id, account_type))
    #                     or accounts.get(('res.company', move.company_id.id, account_type))
    #                 )
    #                 if line.move_id.fiscal_position_id:
    #                     account_id = self.move_id.fiscal_position_id.map_account(self.env['account.account'].browse(account_id))
    #                 line.account_id = account_id

    #         product_lines = self.filtered(lambda line: line.display_type == 'product' and line.move_id.is_invoice(True))
    #         for line in product_lines:
    #             if line.product_id:
    #                 fiscal_position = line.move_id.fiscal_position_id
    #                 accounts = line.with_company(line.company_id).product_id\
    #                     .product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
    #                 if line.move_id.is_sale_document(include_receipts=True):
    #                     line.account_id = accounts['income'] or line.account_id
    #                 elif line.move_id.is_purchase_document(include_receipts=True):
    #                     line.account_id = accounts['expense'] or line.account_id
    #             elif line.partner_id:
    #                 line.account_id = self.env['account.account']._get_most_frequent_account_for_partner(
    #                     company_id=line.company_id.id,
    #                     partner_id=line.partner_id.id,
    #                     move_type=line.move_id.move_type,
    #                 )
    #         for line in self:
    #             if not line.account_id and line.display_type not in ('line_section', 'line_note'):
    #                 previous_two_accounts = line.move_id.line_ids.filtered(
    #                     lambda l: l.account_id and l.display_type == line.display_type
    #                 )[-2:].account_id
    #                 account_id = self.move_id.vendor_advanced_account_id
    #                 if len(previous_two_accounts) == 1:
    #                     line.account_id = previous_two_accounts
    #                 else:
    #                     line.account_id = account_id.id if account_id else line.move_id.journal_id.default_account_id
    #     else:
    #         return super(AccountMoveLine, self)._compute_account_id()

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
        for line in self:
            # Hanya untuk purchase advance
            if line.move_id.is_advanced and line.move_id.is_purchase_document(include_receipts=True):
                if line.display_type == 'payment_term':
                    # Payment term wajib pakai payable account (bawaan Odoo)
                    super(AccountMoveLine, line)._compute_account_id()
                else:
                    # Semua line lain pakai vendor advance account
                    account_id = line.company_id.vendor_advanced_account_id
                    if account_id:
                        line.account_id = account_id.id
                    else:
                        line.account_id = line.move_id.journal_id.default_account_id.id
            else:
                # Kalau bukan purchase advance → pakai default Odoo
                super(AccountMoveLine, line)._compute_account_id()

    def unlink(self):
        for line in self:
            company = line.company_id or self.env.company
            if (
                line.move_id.is_advanced
                and line.move_id.advanced_purchase_id
                and line.account_id == company.vendor_advanced_account_id
            ):
                raise ValidationError(_("Anda Tidak bisa menghapus baris ini karena invoice advanced."))
        return super().unlink()