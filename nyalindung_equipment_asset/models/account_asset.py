from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round
from datetime import datetime, date
from math import copysign
import re


class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'

    register_id = fields.Many2one('equipment.register', string='Register', compute='get_register_id', store=True)

    @api.depends('acquisition_line_ids')
    def get_register_id(self):
        for record in self:
            register_acq_ids = record.acquisition_line_ids.mapped('equipment_register_line_id')
            record.register_id = register_acq_ids[0].register_id.id if register_acq_ids else False

    def name_get(self):
        result = []        
        for rec in self:
            if rec.register_id:
                result.append((rec.id, '%s - %s' % (rec.name,rec.register_id.name)))
        return result
    
class AccountAssetDisposal(models.Model):
    _inherit = 'account.asset.disposal'

    action = fields.Selection([('sell', 'Sell'), ('dispose', 'Dispose')], required=True, default=False)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    lva = fields.Boolean('LVA')
    gross_value = fields.Monetary('Gross Value', related='asset_id.value')
    commulative_depreciation = fields.Float('Commulative Depreciation', compute='get_amount_commulative_depreciation')
    gain_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", related='company_id.gain_on_asset_sales_account_id', help="Account used to write the journal item in case of gain", readonly=False)
    loss_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", related='company_id.loss_on_asset_sales_account_id', help="Account used to write the journal item in case of loss", readonly=False)
    write_on_asset_sales_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", related='company_id.write_on_asset_sales_account_id', help="Account used to write the journal item in case of loss", readonly=False)
    income_from_lva_sales_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", related='company_id.income_from_lva_sales_account_id', help="Account used to write the journal item in case of loss", readonly=False)
    equip_id = fields.Many2one('maintenance.equipment', string='Asset')
    asset_id = fields.Many2one('account.asset.asset', required=False, domain="[('state', '=', 'open')]")
    income_from_lva_sales_account_id = fields.Many2one('account.account', string='Income From LVA Sales Account',related='company_id.income_from_lva_sales_account_id', readonly=False)

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        for record in self:
            if record.asset_id:
                move_posted_check = any(line.move_posted_check for line in record.asset_id.depreciation_line_ids)
                record.value_residual = record.asset_id.value_residual if move_posted_check else record.asset_id.value
            else:
                record.value_residual = 0

    @api.onchange('lva')
    def _onchange_lva(self):
        if self.lva:
            self.asset_id = False            

    @api.depends('asset_id')
    def get_amount_commulative_depreciation(self):
        for record in self:
            record.commulative_depreciation = 0.0
            if record.asset_id and record.asset_id.depreciation_line_ids:
                depreciated_lines = record.asset_id.depreciation_line_ids.filtered(lambda x: x.move_posted_check)
                if depreciated_lines:
                    record.commulative_depreciation = sum(depreciated_lines.mapped('depreciated_value'))
    
    def _get_disposal_moves(self, invoice_line_ids, disposal_date):
        if self.lva and self.equip_id:
            self.equip_id.unlink()
        else:
            def get_line(asset, amount, account):
                return (0, 0, {
                    'name': asset.name,
                    'account_id': account.id,
                    'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                    'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    # 'analytic_account_id': account_analytic_id.id if asset.category_id.type == 'sale' else False,
                    # 'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type == 'sale' else False,
                    'currency_id': current_currency.id,
                    # 'amount_currency': -asset.value_residual,
                    'amount_currency': -amount,
                })

            move_ids = []
            assert len(self.asset_id) == len(invoice_line_ids)
            for asset, invoice_line_id in zip(self.asset_id, invoice_line_ids):
                posted_moves = asset.depreciation_line_ids.filtered(lambda x: (
                    # not x.reversal_move_id and 
                    x.move_posted_check == True
                    # x.move_posted_check == 'posted'
                ))
                if posted_moves and disposal_date < max(posted_moves.mapped('depreciation_date')):
                    if invoice_line_id:
                        raise UserError('There are depreciation posted after the invoice date (%s).\nPlease revert them or change the date of the invoice.' % disposal_date)
                    else:
                        raise UserError('There are depreciation posted in the future, please revert them.')
                account_analytic_id = asset.account_analytic_id
                # analytic_tag_ids = asset.analytic_tag_ids
                company_currency = asset.company_id.currency_id
                current_currency = asset.currency_id
                prec = company_currency.decimal_places
                unposted_depreciation_move_ids = asset.depreciation_line_ids.filtered(lambda x: not x.move_posted_check)
                # unposted_depreciation_move_ids = asset.depreciation_line_ids.filtered(lambda x: x.state == 'draft')

                old_values = {
                    'method_number': asset.method_number,
                }

                # Remove all unposted depr. lines
                commands = [(2, line_id.id, False) for line_id in unposted_depreciation_move_ids]

                # Create a new depr. line with the residual amount and post it
                asset_sequence = len(asset.depreciation_line_ids) - len(unposted_depreciation_move_ids) + 1

                initial_amount = asset.value
                # initial_amount = asset.original_value
                initial_account = asset.invoice_id.line_ids[-1].account_id if len(asset.invoice_id) == 1 else asset.category_id.account_asset_id
                # initial_account = asset.original_move_line_ids.account_id if len(asset.original_move_line_ids.account_id) == 1 else asset.account_asset_id
                depreciation_moves = asset.depreciation_line_ids.filtered(lambda r: r.move_posted_check) # and not (r.reversal_move_id and r.reversal_move_id[0].state == 'posted')
                depreciated_amount = copysign(sum(depreciation_moves.mapped('amount')), -initial_amount)
                depreciation_account = asset.category_id.account_depreciation_id
                invoice_amount = copysign(invoice_line_id.price_subtotal, -initial_amount) if self.invoice_id else copysign(self.sell_value, -initial_amount)
                invoice_account = invoice_line_id.account_id if self.invoice_id else self.asset_id.category_id.account_asset_id
                difference = -initial_amount - depreciated_amount - invoice_amount

                difference_account = asset.company_id.gain_on_asset_sales_account_id if difference > 0 else asset.company_id.loss_on_asset_sales_account_id	
                if self.action != 'sell' and self.write_on_asset_sales_account_id:
                    line_datas = [(initial_amount, initial_account), (depreciated_amount, depreciation_account), (invoice_amount, invoice_account), (difference, self.write_on_asset_sales_account_id)]
                else:
                    line_datas = [(initial_amount, initial_account), (depreciated_amount, depreciation_account), (invoice_amount, invoice_account), (difference, difference_account)]
                if not invoice_line_id and not self.sell_value:
                    del line_datas[2]
                vals = {
                    'asset_id': asset.id,
                    'name': asset.name + ': ' + (_('Disposal') if not invoice_line_id and self.action != 'sell' else _('Sale')),
                    'sequence' : asset_sequence,
                    'remaining_value': 0,
                    'depreciated_value': asset.depreciation_line_ids[-1].filtered(lambda x: x.move_posted_check == True).depreciated_value,
                    'amount': asset.depreciation_line_ids[-1].filtered(lambda x: x.move_posted_check == True).amount,
                    # 'asset_depreciated_value': max(asset.depreciation_line_ids.filtered(lambda x: x.state == 'posted'), key=lambda x: x.date, default=self.env['account.move']).asset_depreciated_value,
                    'depreciation_date': disposal_date,
                    # 'journal_id': asset.category_id.journal_id.id,
                    # 'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
                }
                commands.append((0, 0, vals))
                asset.write({'depreciation_line_ids': commands, 'method_number': asset_sequence})
                # tracked_fields = self.env['account.asset.asset'].fields_get(['method_number'])
                # changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
                # if changes:
                #     asset.message_post(body=_('Asset sold or disposed. Accounting entry awaiting for validation.'), tracking_value_ids=tracking_value_ids)
                # move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids
                tracked_fields = self.env['account.asset.asset'].fields_get(['method_number', 'method_end'])
                changes, tracking_value_ids = asset._mail_track(tracked_fields, old_values)
                if changes:
                    asset.message_post(subject=_('Asset sold or disposed. Accounting entry awaiting for validation.'), tracking_value_ids=tracking_value_ids)
                # move_ids += asset.depreciation_line_ids[-1].create_move(post_move=False)
                move = self.env['account.move'].create({
                    'date': disposal_date,
                    'journal_id': asset.category_id.journal_id.id,
                    'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
                })
                move_ids += [move.id]
            return move_ids
    
    def action_create_invoice(self):
        if self.lva:
            self.action_create_invoice_lva()
        else:
            def get_line(asset, amount, account):
                return (0, 0, {
                    'name': f"{asset.name} - {asset.register_id.name}",
                    'account_id': account.id,
                    'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                    'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    'currency_id': current_currency.id,
                    'amount_currency': -amount,
                })

            asset = self.asset_id
            company_currency = asset.company_id.currency_id
            current_currency = asset.currency_id
            prec = company_currency.decimal_places

            initial_amount = asset.value
            initial_account = asset.invoice_id.line_ids[-1].account_id if len(asset.invoice_id) == 1 else asset.category_id.account_asset_id
            commulative_depreciation = -self.value_residual
            # depreciated_amount = copysign(sum(depreciation_moves.mapped('amount')), -initial_amount)
            depreciation_account = asset.category_id.account_depreciation_id
            difference = self.sell_value - self.commulative_depreciation
            sell_amount = -self.sell_value
            asset_receivable_account = self.env['account.account'].search([('account_type','=','asset_receivable')],limit=1)

            difference_account = self.gain_account_id if self.sell_value > self.value_residual else self.loss_account_id
            line_datas = [(sell_amount, asset_receivable_account),(initial_amount, initial_account), (commulative_depreciation, depreciation_account), (difference, difference_account)]
            print("=======================", line_datas)
            invoice_lines = [(0,0,{
                'product_id': False,
                'name': f"{self.asset_id.name} - {self.asset_id.register_id.name}",
                'quantity': 1,
                'price_unit': self.sell_value,
                'account_id': asset.category_id.account_asset_id.id,
                'currency_id': self.company_id.currency_id.id,
                'display_type' : 'product'
            })]
            sale_journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            move = self.env['account.move'].create({
                'move_type' : 'out_invoice',
                'date': date.today(),
                'journal_id': sale_journal.id,
                'invoice_line_ids' : invoice_lines,
                # 'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
            })
            return self.action_open_invoice(move)
    
    def action_create_invoice_lva(self):
        income_account = self.income_from_lva_sales_account_id
        if not income_account:
            raise ValueError("Income From LVA Sales Account not found, please configure in equipment settings")
        invoice_lines = [(0,0,{
            'product_id': False,
            'name': f"{self.equip_id.name} - {self.equip_id.seq_no}",
            'quantity': 1,
            'price_unit': self.sell_value,
            'account_id': income_account.id,
            'currency_id': self.company_id.currency_id.id,
        })]
        move = self.env['account.move'].create({
            'move_type' : 'out_invoice',
            'date': date.today(),
            'invoice_line_ids' : invoice_lines,
        })
        return self.action_open_invoice(move)
            
    
    # def action_create_invoice(self):
    #     def get_line(asset, amount, account):
    #         company_currency = asset.company_id.currency_id
    #         current_currency = asset.currency_id
    #         prec = company_currency.decimal_places

    #         return (0, 0, {
    #             'name': f"{asset.name} - {asset.register_id.name}",
    #             'account_id': account.id,
    #             'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
    #             'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
    #             'currency_id': current_currency.id,
    #             'amount_currency': amount if current_currency != company_currency else 0.0,
    #         })
        
    #     asset = self.asset_id
    #     initial_amount = asset.value
    #     initial_account = asset.invoice_id.line_ids[-1].account_id if asset.invoice_id else asset.category_id.account_asset_id
    #     depreciation_moves = asset.depreciation_line_ids.filtered(lambda r: r.move_posted_check)
    #     # depreciated_amount = copysign(sum(depreciation_moves.mapped('amount')), -initial_amount)
    #     depreciated_amount = self.commulative_depreciation
    #     depreciation_account = asset.category_id.account_depreciation_id
    #     sell_amount = self.sell_value
    #     sell_account = self.env['account.account'].search([('account_type','=','liability_payable')], limit=1)

    #     gain_account_parameter = self.env['ir.config_parameter'].sudo().get_param('gain.on.asset.sales.account.id')
    #     loss_account_parameter = self.env['ir.config_parameter'].sudo().get_param('loss.on.asset.sales.account.id')
    #     gain_account = self.env['account.account'].browse(gain_account_parameter)
    #     loss_account = self.env['account.account'].browse(loss_account_parameter)
        
    #     difference = self.sell_value - self.value_residual
    #     difference_account = gain_account if difference > 0 else loss_account
        
    #     line_datas = [
    #         # (sell_amount, sell_account),
    #         (initial_amount, initial_account),
    #         (depreciated_amount, depreciation_account),
    #         (difference, difference_account)
    #     ]

    #     line_data = [get_line(asset, amount, account) for amount, account in line_datas if account],
    #     print("=========================", line_data)
        
    #     if not sell_account:
    #         line_datas = line_datas[1:]
    #     if not gain_account and not loss_account:
    #         line_datas.pop()

    #     account_asset = self.asset_id.category_id.account_asset_id
    #     invoice_lines = [{
    #         'product_id': False,
    #         'name': f"{self.asset_id.name} - {self.asset_id.register_id.name}",
    #         'quantity': 1,
    #         'price_unit': self.sell_value,
    #         'account_id': account_asset.id if account_asset else False,
    #         'currency_id': self.company_id.currency_id.id,
    #     }]

    #     line_ids = [(0,0,{
    #         'name': f"{asset.name} - {asset.register_id.name}",
    #         'account_id': account_asset.id,
    #         'debit': 1000000,
    #         'credit': 0.0,
    #         'currency_id': self.company_id.currency_id.id,
    #         'amount_currency': 0.0,
    #     })]

    #     # journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
    #     # if not journal:
    #     #     raise UserError("No sale journal found. Please configure a sale journal.")
    #     move = self.env['account.move'].create({
    #         # 'move_type': 'out_invoice',
    #         'date': date.today(),
    #         'journal_id': asset.category_id.journal_id.id,
    #         # 'invoice_line_ids': [(0, 0, line) for line in invoice_lines],
    #         'line_ids' : line_ids
    #     })
    #     for data in move.line_ids:
    #         print("=======================data",data.debit)
    #         print("=======================data",data.credit)
    #     # move.write({
    #     # })

    #     return self.action_open_invoice(move)
    
    # def action_create_invoice(self):
    #     def get_line(asset, amount, account):
    #         company_currency = asset.company_id.currency_id
    #         current_currency = asset.currency_id
    #         prec = company_currency.decimal_places

    #         return (0, 0, {
    #             'name': f"{asset.name} - {asset.register_id.name}",
    #             'account_id': account.id,
    #             'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
    #             'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
    #             'currency_id': current_currency.id,
    #             'amount_currency': amount if current_currency != company_currency else 0.0,
    #         })
        
    #     asset = self.asset_id
    #     move_lines = []
    #     move_vals = {
    #         'move_type' : 'out_invoice',
    #         'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id,
    #         'date': date.today(),
    #     }

    #     # debit_lines
    #     move_line_vals_asset = {
    #         'account_id': asset.category_id.account_asset_id.id,
    #         'name': 'Reclass Asset to SPM',
    #         'debit': 1000000,
    #         'credit': 0.0,
    #     }
    #     move_lines.append((0, 0, move_line_vals_asset))
    #     # credit_lines
    #     credit_account = asset.category_id.account_asset_id
    #     move_line_vals = {
    #         'account_id': credit_account.id,
    #         'name': 'Reclass SPM to Asset',
    #         'credit': 1000000,
    #         'debit': 0.0,
    #     }
    #     move_lines.append((0, 0, move_line_vals))
    #     invoice_lines = [(0,0,{
    #         'product_id': False,
    #         'name': f"{self.asset_id.name} - {self.asset_id.register_id.name}",
    #         'quantity': 1,
    #         'price_unit': self.sell_value,
    #         'account_id': asset.category_id.account_asset_id.id,
    #         'currency_id': self.company_id.currency_id.id,
    #     })]
    #     # create move
    #     move_vals.update({'line_ids': move_lines, 'invoice_line_ids' : invoice_lines})
    #     move = self.env['account.move'].create(move_vals)
    #     return self.action_open_invoice(move)
    
    
    def action_open_invoice(self, move=False):
        if move:
            if len(move) == 1:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Invoice',
                    'res_model': 'account.move',
                    'view_mode': 'form',
                    'res_id': move.id,
                    'view_id': self.env.ref('account.view_move_form').id,
                    'target': 'current',
                }
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Invoices',
                    'res_model': 'account.move',
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', move.ids)],
                    'target': 'current',
                }
        else:
            return self.env["ir.actions.actions"]._for_xml_id('account.action_move_out_invoice_type')
