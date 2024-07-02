from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round
from datetime import datetime
from math import copysign


class AccountAssetDisposal(models.Model):
    _name = 'account.asset.disposal'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Sell/Dispose Asset'

    asset_id = fields.Many2one('account.asset', required=True, domain="[('state', '=', 'open')]")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    name = fields.Char(string="Name")
    action = fields.Selection([('sell', 'Sell'), ('dispose', 'Dispose')], required=True, default='sell')
    invoice_id = fields.Many2one('account.move', string="Customer Invoice", help="The disposal invoice is needed in order to generate the closing journal entry.", domain="[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]")
    invoice_line_id = fields.Many2one('account.move.line', help="There are multiple lines that could be the related to this asset", domain="[('move_id', '=', invoice_id), ('exclude_from_invoice_tab', '=', False)]")
    select_invoice_line_id = fields.Boolean(compute="_compute_select_invoice_line_id")
    gain_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", related='company_id.gain_account_id', help="Account used to write the journal item in case of gain", readonly=False)
    loss_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", related='company_id.loss_account_id', help="Account used to write the journal item in case of loss", readonly=False)

    gain_or_loss = fields.Selection([('gain', 'Gain'), ('loss', 'Loss'), ('no', 'No')], compute='_compute_gain_or_loss', help="Technical field to know is there was a gain or a loss in the selling of the asset")

    sell_value = fields.Float(string='Sell Value', digits=0, compute='_get_sell_value', store=True, readonly=False)
    sell_account_move_id = fields.Many2one('account.move', 'Sell Account Move')
    reason = fields.Text(string="Sell/Dispose Reason")
    value_residual = fields.Float(string="Residual Value")
    state = fields.Selection([('draft', 'Draft'), ('closed', 'Closed')], 'Status', readonly=True, copy=False, default='draft')

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        for record in self:
            if record.asset_id:
                record.value_residual = record.asset_id.value_residual
            else:
                record.value_residual = 0

    @api.depends('invoice_id')
    def _get_sell_value(self):
        for record in self:
            if record.invoice_id:
                record.sell_value = record.invoice_id.invoice_line_ids[0].price_subtotal

    @api.depends('invoice_id', 'action')
    def _compute_select_invoice_line_id(self):
        for record in self:
            record.select_invoice_line_id = record.action == 'sell' and len(record.invoice_id.invoice_line_ids) > 1

    @api.onchange('action')
    def _onchange_action(self):
        if self.action == 'sell' and self.asset_id.children_ids.filtered(lambda a: a.state in ('draft', 'open') or a.value_residual > 0):
            raise UserError(_("You cannot automate the journal entry for an asset that has a running gross increase. Please use 'Dispose' on the increase(s)."))

    @api.depends('asset_id', 'invoice_id', 'invoice_line_id', 'sell_value')
    def _compute_gain_or_loss(self):
        for record in self:
            if self.invoice_id:
                line = record.invoice_line_id or len(record.invoice_id.invoice_line_ids) == 1 and record.invoice_id.invoice_line_ids or self.env['account.move.line']
                if record.asset_id.value_residual < abs(line.balance):
                    record.gain_or_loss = 'gain'
                elif record.asset_id.value_residual > abs(line.balance):
                    record.gain_or_loss = 'loss'
                else:
                    record.gain_or_loss = 'no'
            elif self.sell_value:
                line = self.sell_value
                if record.asset_id.value_residual < line:
                    record.gain_or_loss = 'gain'
                elif record.asset_id.value_residual > line:
                    record.gain_or_loss = 'loss'
                else:
                    record.gain_or_loss = 'no'
            else:
                record.gain_or_loss = 'no'

    def do_action(self):
        self.ensure_one()
        invoice_line = self.env['account.move.line'] if self.action == 'dispose' else self.invoice_line_id or self.invoice_id.invoice_line_ids
        res = self.set_to_close(invoice_line_id=invoice_line, date=invoice_line.move_id.invoice_date)
        self.sell_account_move_id = res['res_id']
        return res

    def _get_disposal_moves(self, invoice_line_ids, disposal_date):
        def get_line(asset, amount, account):
            return (0, 0, {
                'name': asset.name,
                'account_id': account.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'analytic_account_id': account_analytic_id.id if asset.asset_type == 'sale' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type == 'sale' else False,
                'currency_id': current_currency.id,
                'amount_currency': -asset.value_residual,
            })

        move_ids = []
        assert len(self.asset_id) == len(invoice_line_ids)
        for asset, invoice_line_id in zip(self.asset_id, invoice_line_ids):
            posted_moves = asset.depreciation_move_ids.filtered(lambda x: (
                not x.reversal_move_id
                and x.state == 'posted'
            ))
            if posted_moves and disposal_date < max(posted_moves.mapped('date')):
                if invoice_line_id:
                    raise UserError('There are depreciation posted after the invoice date (%s).\nPlease revert them or change the date of the invoice.' % disposal_date)
                else:
                    raise UserError('There are depreciation posted in the future, please revert them.')
            account_analytic_id = asset.account_analytic_id
            analytic_tag_ids = asset.analytic_tag_ids
            company_currency = asset.company_id.currency_id
            current_currency = asset.currency_id
            prec = company_currency.decimal_places
            unposted_depreciation_move_ids = asset.depreciation_move_ids.filtered(lambda x: x.state == 'draft')

            old_values = {
                'method_number': asset.method_number,
            }

            # Remove all unposted depr. lines
            commands = [(2, line_id.id, False) for line_id in unposted_depreciation_move_ids]

            # Create a new depr. line with the residual amount and post it
            asset_sequence = len(asset.depreciation_move_ids) - len(unposted_depreciation_move_ids) + 1

            initial_amount = asset.original_value
            initial_account = asset.original_move_line_ids.account_id if len(asset.original_move_line_ids.account_id) == 1 else asset.account_asset_id
            depreciation_moves = asset.depreciation_move_ids.filtered(lambda r: r.state == 'posted' and not (r.reversal_move_id and r.reversal_move_id[0].state == 'posted'))
            depreciated_amount = copysign(sum(depreciation_moves.mapped('amount_total')), -initial_amount)
            depreciation_account = asset.account_depreciation_id
            invoice_amount = copysign(invoice_line_id.price_subtotal, -initial_amount) if self.invoice_id else copysign(self.sell_value, -initial_amount)
            invoice_account = invoice_line_id.account_id if self.invoice_id else self.asset_id.account_asset_id
            difference = -initial_amount - depreciated_amount - invoice_amount
            difference_account = asset.company_id.gain_account_id if difference > 0 else asset.company_id.loss_account_id
            line_datas = [(initial_amount, initial_account), (depreciated_amount, depreciation_account), (invoice_amount, invoice_account), (difference, difference_account)]
            if not invoice_line_id and not self.sell_value:
                del line_datas[2]
            vals = {
                'asset_id': asset.id,
                'ref': asset.name + ': ' + (_('Disposal') if not invoice_line_id and self.action != 'sell' else _('Sale')),
                'asset_remaining_value': 0,
                'asset_depreciated_value': max(asset.depreciation_move_ids.filtered(lambda x: x.state == 'posted'), key=lambda x: x.date, default=self.env['account.move']).asset_depreciated_value,
                'date': disposal_date,
                'journal_id': asset.journal_id.id,
                'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
            }
            commands.append((0, 0, vals))
            asset.write({'depreciation_move_ids': commands, 'method_number': asset_sequence})
            tracked_fields = self.env['account.asset'].fields_get(['method_number'])
            changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
            if changes:
                asset.message_post(body=_('Asset sold or disposed. Accounting entry awaiting for validation.'), tracking_value_ids=tracking_value_ids)
            move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids
        
        return move_ids

    def set_to_close(self, invoice_line_id, date=None):
        self.ensure_one()
        disposal_date = date or fields.Date.today()
        if invoice_line_id and self.asset_id.children_ids.filtered(lambda a: a.state in ('draft', 'open') or a.value_residual > 0):
            raise UserError(_("You cannot automate the journal entry for an asset that has a running gross increase. Please use 'Dispose' on the increase(s)."))
        full_asset = self.asset_id + self.asset_id.children_ids
        move_ids = self._get_disposal_moves([invoice_line_id] * len(full_asset), disposal_date)
        full_asset.write({'state': 'close', 'disposal_id': self.id})
        self.state="closed"
        if move_ids:
            return self.asset_id._return_disposal_view(move_ids)

    def action_create_invoice(self):
        res = self.env.ref('account.action_move_out_invoice_type').read()[0]
        res['context'] = {
            'default_move_type': 'out_invoice',
            # 'default_invoice_line_ids': [{
            #     'product_id': False,
            #     'name'      : self.asset_id.name,
            #     'quantity'  : 1,
            #     'price_unit': self.sell_value,
            #     'account_id': self.loss_account_id.id if self.loss_account_id else self.gain_account_id.id}]
        }
        res['domain']=[('id', '=', False)]
        return res