from hashlib import sha256
from json import dumps

from odoo import models, api, fields, _
from odoo.exceptions import UserError



class account_period(models.Model):
    _inherit      = 'account.period'

    # name            = fields.Char('Period Name', required=True)
    # code            = fields.Char('Code', size=12)
    # special         = fields.Boolean('Opening/Closing Period', help="These periods can overlap.")
    # date_start      = fields.Date('Start of Period', required=True, states={'done': [('readonly', True)]})
    # date_stop       = fields.Date('End of Period', required=True, states={'done': [('readonly', True)]})
    # fiscalyear_id   = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True, states={'done': [('readonly', True)]}, index=True)
    # year            = fields.Integer(string='Year', default=fields.Datetime.now().year)
    # state           = fields.Selection([('draft', 'Open'), ('done', 'Closed')], 'Status', readonly=True, copy=False,
    #                          default='draft',
    #                          help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    # company_id      = fields.Many2one('res.company', string='Company')


    # def close_period(self):
    #     for record in self:
    #         record.state = "done"
    
    # def reopen_period(self):
    #     for record in self:
    #         record.state = "draft"
    

class AccountMove(models.Model):
    _inherit = "account.move"

    # @api.multi
    def post(self):
        default_loc_type = self.env['lhm.location.type'].search([('name', '=', '-')])
        for move in self:
            for line in move.line_ids:
                if not line.plantation_location_type_id:
                    line.plantation_location_type_id = default_loc_type and default_loc_type[0].id or False
        return super(AccountMove, self).post()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")
    plantation_validator = fields.Boolean(string="Plantation Validator", related="plantation_location_type_id.no_line")

    @api.onchange('plantation_location_type_id')
    def _onchange_plantation_location_type_id(self):
        if self.plantation_location_type_id:
            self.plantation_location_id = False
            self.plantation_activity_id = False
            # if self.plantation_location_type_id.no_line and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
            #     self.account_id = False
            # else:
            #     self.account_id = self.plantation_location_type_id.account_id.id if self.plantation_location_type_id.account_id else False

    @api.onchange('plantation_location_id')
    def _onchange_plantation_location_id(self):
        if self.plantation_location_id:
            self.plantation_activity_id = False

    # @api.onchange('plantation_activity_id')
    # def _onchange_plantation_activity_id(self):
    #     if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
    #         self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False


# class AccountInvoice(models.Model):
#     _inherit = "account.invoice"

#     @api.model
#     def invoice_line_move_line_get(self):
#         res = super(AccountInvoice, self).invoice_line_move_line_get()
#         default_loc_type = self.env['lhm.location.type'].search([('name', '=', '-')])
#         for line in res:
#             if line.get('invl_id'):
#                 inv_line = self.env['account.invoice.line'].browse(line['invl_id'])
#                 line.update({
#                     'plantation_location_type_id': inv_line.plantation_location_type_id.id if inv_line.plantation_location_type_id else (default_loc_type and default_loc_type[0].id or False),
#                     'plantation_location_id': inv_line.plantation_location_id.id if inv_line.plantation_location_id else False,
#                     'plantation_activity_id': inv_line.plantation_activity_id.id if inv_line.plantation_activity_id else False,
#                 })
#             else:
#                 line.update({
#                     'plantation_location_type_id': default_loc_type and default_loc_type[0].id or False,
#                     'plantation_location_id': False,
#                     'plantation_activity_id': False,
#                 })
#         return res

#     @api.model
#     def line_get_convert(self, line, part):
#         res = super(AccountInvoice, self).line_get_convert(line, part)
#         default_loc_type = self.env['lhm.location.type'].search([('name', '=', '-')])
#         res.update({
#             'plantation_location_type_id': line.get('plantation_location_type_id', default_loc_type and default_loc_type[0].id or False),
#             'plantation_location_id': line.get('plantation_location_id', False),
#             'plantation_activity_id': line.get('plantation_activity_id', False),
#         })
#         return res

#     # @api.multi
#     def invoice_print_plantation(self):
#         self.ensure_one()
#         return self.env['report'].get_action(self, 'c10i_lhm.report_invoice_lhm')


# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"

#     plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
#     plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
#     plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")
#     plantation_validator = fields.Boolean(string="Plantation Validator", related="plantation_location_type_id.no_line")

#     @api.onchange('plantation_location_type_id')
#     def _onchange_plantation_location_type_id(self):
#         if self.plantation_location_type_id:
#             self.plantation_location_id = False
#             self.plantation_activity_id = False
#             if self.plantation_location_type_id.no_line and self.product_id:
#                 self.account_id = self.product_id.property_stock_account_input.id or (self.product_id.categ_id.property_stock_account_input_categ_id.id if self.product_id.categ_id else False)
#             elif self.plantation_location_type_id.no_line and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#                 self.account_id = False
#             else:
#                 self.account_id = self.plantation_location_type_id.account_id.id if self.plantation_location_type_id.account_id else False

#     @api.onchange('plantation_location_id')
#     def _onchange_plantation_location_id(self):
#         if self.plantation_location_id:
#             self.plantation_activity_id = False

#     @api.onchange('plantation_activity_id')
#     def _onchange_plantation_activity_id(self):
#         if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#             self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False


# class AccountVoucher(models.Model):
#     _inherit = "account.voucher"

#     # @api.multi
#     def first_move_line_get(self, move_id, company_currency, current_currency):
#         default_loc_type = self.env['lhm.location.type'].search([('name', '=', '-')])
#         move_line = super(AccountVoucher, self).first_move_line_get(move_id, company_currency, current_currency)
#         if self.partner_id.commercial_partner_id.id == self.company_id.id:
#             move_line.update({
#                 'partner_id': self.partner_id.id,
#                 'plantation_location_type_id': default_loc_type and default_loc_type[0].id or False,
#             })
#         return move_line

#     # @api.multi
#     def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
#         default_loc_type = self.env['lhm.location.type'].search([('name', '=', '-')])
#         for line in self.line_ids:
#             if not line.price_subtotal:
#                 continue
#             debit = credit = 0.0
#             amount = self._convert_amount(line.price_unit * line.quantity)
#             if self.voucher_type == 'sale':
#                 if amount < 0.0:
#                     debit = abs(amount)
#                 else:
#                     credit = amount
#             elif self.voucher_type == 'purchase':
#                 if amount < 0.0:
#                     credit = abs(amount)
#                 else:
#                     debit = amount
#             sign = debit - credit < 0 and -1 or 1
#             move_line = {
#                 'journal_id': self.journal_id.id,
#                 'name': line.name or '/',
#                 'account_id': line.account_id.id,
#                 'move_id': move_id,
#                 'partner_id': self.partner_id.commercial_partner_id.id,
#                 'analytic_account_id': line.account_analytic_id.id if line.account_analytic_id else False,
#                 'quantity': 1,
#                 'credit': credit,
#                 'debit': debit,
#                 'date': self.account_date,
#                 'tax_ids': [(4, t.id) for t in line.tax_ids],
#                 'amount_currency': sign * line.price_subtotal if current_currency != company_currency else 0.0,
#                 'currency_id': current_currency if company_currency != current_currency else False,
#                 'plantation_location_type_id': line.plantation_location_type_id.id if line.plantation_location_type_id else (default_loc_type and default_loc_type[0].id or False),
#                 'plantation_location_id': line.plantation_location_id.id if line.plantation_location_id else False,
#                 'plantation_activity_id': line.plantation_activity_id.id if line.plantation_activity_id else False,
#                 'payment_id': self._context.get('payment_id'),
#             }
#             self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
#             line_total += (debit - credit)
#         return line_total


# class AccountVoucherLine(models.Model):
#     _inherit = "account.voucher.line"

#     plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
#     plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
#     plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")
#     plantation_validator = fields.Boolean(string="Plantation Validator", related="plantation_location_type_id.no_line")

#     @api.onchange('plantation_location_type_id')
#     def _onchange_plantation_location_type_id(self):
#         if self.plantation_location_type_id:
#             self.plantation_location_id = False
#             self.plantation_activity_id = False
#             if self.plantation_location_type_id.no_line and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#                 self.account_id = False
#             else:
#                 self.account_id = self.plantation_location_type_id.account_id.id if self.plantation_location_type_id.account_id else False

#     @api.onchange('plantation_location_id')
#     def _onchange_plantation_location_id(self):
#         if self.plantation_location_id:
#             self.plantation_activity_id = False

#     @api.onchange('plantation_activity_id')
#     def _onchange_plantation_activity_id(self):
#         if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#             self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False


# class AccountSettlementAdvanceLine(models.Model):
#     _inherit = 'account.settlement.advance.line'

#     plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
#     plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
#     plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")
#     plantation_validator = fields.Boolean(string="Plantation Validator", related="plantation_location_type_id.no_line")

#     @api.onchange('plantation_location_type_id')
#     def _onchange_plantation_location_type_id(self):
#         if self.plantation_location_type_id:
#             self.plantation_location_id = False
#             self.plantation_activity_id = False
#             if self.plantation_location_type_id.no_line and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#                 self.account_id = False
#             else:
#                 self.account_id = self.plantation_location_type_id.account_id.id if self.plantation_location_type_id.account_id else False

#     @api.onchange('plantation_location_id')
#     def _onchange_plantation_location_id(self):
#         if self.plantation_location_id:
#             self.plantation_activity_id = False

#     @api.onchange('plantation_activity_id')
#     def _onchange_plantation_activity_id(self):
#         if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#             self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False

#     def _prepare_expense_move_line(self, move):
#         move_vals = super(AccountSettlementAdvanceLine, self)._prepare_expense_move_line(move)
#         move_vals.update({
#             'plantation_location_type_id': self.plantation_location_type_id.id if self.plantation_location_type_id else False,
#             'plantation_location_id': self.plantation_location_id.id if self.plantation_location_id else False,
#             'plantation_activity_id': self.plantation_activity_id.id if self.plantation_activity_id else False,
#             'plantation_validator': self.plantation_validator,
#         })
#         return move_vals


# class SplitSettlementAdvanceLine(models.Model):
#     _inherit = 'split.settlement.advance.line'

#     plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
#     plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
#     plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")
#     plantation_validator = fields.Boolean(string="Plantation Validator", related="plantation_location_type_id.no_line")

#     @api.onchange('plantation_location_type_id')
#     def _onchange_plantation_location_type_id(self):
#         if self.plantation_location_type_id:
#             self.plantation_location_id = False
#             self.plantation_activity_id = False
#             if self.plantation_location_type_id.no_line and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#                 self.account_id = False
#             else:
#                 self.account_id = self.plantation_location_type_id.account_id.id if self.plantation_location_type_id.account_id else False

#     @api.onchange('plantation_location_id')
#     def _onchange_plantation_location_id(self):
#         if self.plantation_location_id:
#             self.plantation_activity_id = False

#     @api.onchange('plantation_activity_id')
#     def _onchange_plantation_activity_id(self):
#         if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
#             self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False

#     def _prepare_expense_split_move_line(self, settlement_line, move):
#         move_vals = super(SplitSettlementAdvanceLine, self)._prepare_expense_split_move_line(settlement_line, move)
#         move_vals.update({
#             'plantation_location_type_id': self.plantation_location_type_id.id if self.plantation_location_type_id else False,
#             'plantation_location_id': self.plantation_location_id.id if self.plantation_location_id else False,
#             'plantation_activity_id': self.plantation_activity_id.id if self.plantation_activity_id else False,
#             'plantation_validator': self.plantation_validator,
#         })
#         return move_vals
