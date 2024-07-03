from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import ValidationError, UserError

class DirectPayment(models.Model):
    _inherit = "account.direct.payment"

    employee_expense_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'), 
        ('approved', 'Approved'), 
        ('posted', 'Posted'), 
        ('done', 'Closed'), 
        ('reject', 'Rejected'), 
        ('cancel', 'Cancel')], default="draft", tracking=True)
    expense_report = fields.Boolean('Expense Report')
    is_advance = fields.Boolean('Employee Advance')
    employee_id = fields.Many2one('hr.employee', string='Employee', copy=False)
    approved_by = fields.Many2one("res.users", string="paymented by", 
        tracking=True, index=True,
    )
    advance_residual = fields.Monetary(
        string="Amount to Clear",
        compute="_compute_advance_residual",
        store=True, compute_sudo=True,
        help="Amount to clear of this Advance in company currency",
    )

    # Settlement
    advance_found = fields.Boolean(compute="_check_advance")
    advance_to_settle_ids = fields.Many2many('account.direct.payment', 'account_direct_payment_to_advance_rel',
        'settlement_id', 'advance_id', string="Employee Advance", domain="[('advance_residual','>',0)]")

    advance_amount_settle = fields.Monetary(compute="_compute_settlement_amount", string="Advance Amount", store=True)
    amount_total2 = fields.Monetary(compute="_compute_settlement_amount", string="Amount Total", store=True)

    @api.depends('employee_id')
    def _check_advance(self):
        for payment in self:
            # if payment.expense_report and not payment.is_advance and payment.state=='draft':
            if payment.expense_report and not payment.is_advance:
                advance_count = self.search_count([('employee_id','=',payment.employee_id.id),('advance_residual','>',0.0)])
                payment.advance_found = (advance_count > 0)
            else:
                payment.advance_found = False

    @api.depends("account_move_id.line_ids.amount_residual")
    def _compute_advance_residual(self):
        for payment in self:
            if not payment.is_advance:
                payment.advance_residual = 0.0
                continue
            residual_company = 0.0
            advance_account = payment.company_id.employee_advance_account_id
            if not advance_account:
                raise ValidationError(_('Please configure Employee Advance Account on your Accounting Settings'))
            for line in payment.account_move_id.line_ids:
                if line.account_id == advance_account:
                    residual_company += line.amount_residual
            payment.advance_residual = residual_company

    @api.depends('amount_total', 'advance_to_settle_ids')
    def _compute_settlement_amount(self):
        for payment in self:
            amount_to_settle = -1*sum(payment.advance_to_settle_ids.mapped('advance_residual'))
            payment.write({
                    'advance_amount_settle': amount_to_settle,
                    'amount_total2': payment.amount_total + amount_to_settle,
                })

    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            self.partner_id = self.employee_id.address_home_id.id or self.employee_id.user_id.partner_id.id

    @api.onchange('is_advance')
    def onchange_is_advance(self):
        if self.is_advance:
            account = self.company_id.employee_advance_account_id
            if not account:
                raise ValidationError(_('Please configure Employee Advance Account on your Accounting Settings'))
            self.line_ids = [(0,0,{
                'name': 'Request of Employee Advance',
                'account_id': account.id,
                })]

    def get_advance_move_line(self):
        move_lines = []
        partner =  self.partner_id or self.requested_by.partner_id or False
        for advance in self.advance_to_settle_ids.filtered(lambda a: a.advance_residual > 0):
            amount = advance.advance_residual
            dict_line_adv = {
                'partner_id': partner.id if partner else False,
                'account_id': self.company_id.employee_advance_account_id.id,
                'debit': 0.0 if amount > 0.0 else abs(amount),
                'credit': amount if amount > 0.0 else 0.0,
                'name': "Settlement Advance",
            }
            move_lines.append(dict_line_adv)
        return move_lines

    def direct_payment_hook(self, move_lines):
        move_lines = super().direct_payment_hook(move_lines)
        move_lines.extend(self.get_advance_move_line())
        return move_lines

    def action_create_move(self):
        res = super().action_create_move()
        # Do Reconciliation Adavance
        if self.advance_to_settle_ids.filtered(lambda a: a.advance_residual>0.0):
            settlement_advances = self.account_move_id.line_ids.filtered(lambda l: l.account_id==self.company_id.employee_advance_account_id)
            advances_to_settle = self.advance_to_settle_ids.mapped('account_move_id.line_ids').filtered(lambda l: l.account_id==self.company_id.employee_advance_account_id)
            (settlement_advances + advances_to_settle).reconcile()
        return res

    def employee_submit(self):
        for payment in self:
            if payment.employee_expense_state!='draft':
                raise ValidationError(_('You cannot Submit Expense that is not in a Draft state'))
            payment.employee_expense_state="submit"

    def employee_approve(self):
        for payment in self:
            if payment.employee_expense_state!='submit':
                raise ValidationError(_('You cannot Approve Expense that is not in a Submitted state'))
            payment.write({
                'employee_expense_state': "approved",
                'approved_by': self.env.user.id,
                })
            payment.action_confirm()

    def employee_reject(self):
        for payment in self:
            if payment.employee_expense_state!='submit':
                raise ValidationError(_('You cannot Reject Expense that is not in a Submitted state'))
            payment.write({
                'employee_expense_state': "reject",
                'state': "draft",
                })

    def employee_cancel(self):
        for payment in self:
            if payment.employee_expense_state!='reject':
                raise ValidationError(_('You cannot Cancel Expense that is not in a Rejected state'))
            payment.write({
                'employee_expense_state': "cancel",
                })
            payment.action_cancel()

    def employee_set_draft(self):
        for payment in self:
            if payment.employee_expense_state!='reject':
                raise ValidationError(_('You cannot Set Draft Expense that is not in a Rejected state'))
            payment.action_draft()

    # access_account_direct_payment_buser,account.direct.payment buser,c10i_direct_payment.model_account_direct_payment,base.group_user,1,1,1,1
    # access_account_direct_payment_line_buser,account.direct.payment.line buser,c10i_direct_payment.model_account_direct_payment_line,base.group_user,1,1,1,1
    # access_account_move_buser,account.move buser,account.model_account_move,base.group_user,1,0,0,0
    # access_account_move_line_buser,account.move.line buser,account.model_account_move_line,base.group_user,1,0,0,0
    # access_account_analytic_line_buser,account.analytic.line buser,account.model_account_analytic_line,base.group_user,1,0,0,0
    # access_account_journal_buser,account.journal buser,account.model_account_journal,base.group_user,1,0,0,0
    # access_account_account_buser,account.account buser,account.model_account_account,base.group_user,1,0,0,0
    # access_account_account_type_buser,account.account.type buser,account.model_account_account_type,base.group_user,1,0,0,0
    # access_account_partial_reconcile_buser,account.partial.reconcile buser,account.model_account_partial_reconcile,base.group_user,1,0,0,0