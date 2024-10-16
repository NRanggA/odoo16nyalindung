# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import float_is_zero


class PurchaseOrderAdvancePaymentInv(models.TransientModel):
    _name = 'purchase.order.advance.payment.inv'
    _description = "Purchase Order Advance Payment Invoice"

    advance_payment_method = fields.Selection(
        selection=[
            ('fixed', "Down payment (fixed amount)"),
            ('percentage', "Down payment (percentage)"),
        ],
        string="Create Invoice",
        default='fixed',
        required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing,"
            "according to their invoicing policy (based on ordered or delivered quantity).")
    count = fields.Integer(string="Order Count", compute='_compute_count')
    purchase_order_ids = fields.Many2many(
        'purchase.order', default=lambda self: self.env.context.get('active_ids'))
    amount = fields.Float(
        string="Down Payment Amount",
        help="The percentage of amount to be invoiced in advance, taxes excluded.")
    fixed_amount = fields.Monetary(
        string="Down Payment Amount (Fixed)",
        help="The fixed amount to be invoiced in advance, taxes excluded.")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        compute='_compute_company_id',
        store=True)
    account_id = fields.Many2one('account.account', string='Account', related='company_id.vendor_advanced_account_id')

    @api.depends('purchase_order_ids')
    def _compute_count(self):
        for wizard in self:
            wizard.count = len(wizard.purchase_order_ids)

    @api.depends('purchase_order_ids')
    def _compute_currency_id(self):
        self.currency_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.currency_id = wizard.purchase_order_ids.currency_id

    @api.depends('purchase_order_ids')
    def _compute_company_id(self):
        self.company_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.company_id = wizard.purchase_order_ids.company_id

    @api.onchange('advance_payment_method')
    def _onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}

    @api.constrains('advance_payment_method', 'amount', 'fixed_amount')
    def _check_amount_is_positive(self):
        for wizard in self:
            if wizard.advance_payment_method == 'percentage' and wizard.amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))
            elif wizard.advance_payment_method == 'fixed' and wizard.fixed_amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))

    def create_invoices(self):
        self.ensure_one()
        account_move = self.env['account.move']
        move = account_move.create({
            'move_type': 'in_invoice',
            'partner_id': self.purchase_order_ids[0].partner_id.id,
            'is_advanced': True,
            'advanced_purchase_id': self.purchase_order_ids[0].id,
            'invoice_line_ids': [Command.create({
                'name': 'Advanced Payment',
                'account_id': self.account_id.id,
                'price_unit': self.get_amount(),
            })]
        })

        return self.action_open_move(move)

    def action_open_move(self, move):
        return {
            'name': 'View Move',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_id': move.id,
            'target': 'current',
        }

    def get_amount(self):
        order = self.purchase_order_ids[0]
        tax = self.purchase_order_ids.order_line.mapped('taxes_id')
        if self.advance_payment_method == 'percentage':
            if tax:
                amount = order.amount_untaxed * self.amount / 100
            else:
                amount = order.amount_total * self.amount / 100
        else:
            amount = self.fixed_amount

        return amount
