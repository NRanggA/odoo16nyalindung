from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class DirectPayment(models.Model):
    _inherit = 'account.direct.payment'

    settelement_date = fields.Date('Settelement Date')
    contra_account_for_advance = fields.Many2one(
        comodel_name='account.account',
        related='company_id.contra_account_for_advance', readonly=False,
        string="Contra Account for Advance",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('reconcile','=',True)]",
        help='Please complete the help')
    employee_advance_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.employee_advance_journal_id', readonly=False,
        string="Journal")
    employee_expense_journal_count = fields.Integer('Journal Count', compute='_get_count_employee_expense')
    expense_report = fields.Boolean('Expense Report')
    is_advance = fields.Boolean('Employee Advance')

    def _prepare_payable_move_line(self, amount):
        partner =  self.partner_id or self.requested_by.partner_id or False
        credit_account = self.journal_id.outbound_payment_method_line_ids.payment_account_id
        return {
            'partner_id': partner.id if partner else False,
            'name': _("Request of Direct Payment"),
            # 'account_id': self.company_id.partner_id.property_account_payable_id.id,
            'account_id': credit_account.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            # 'product_id': self.product_id.id,
            'debit': amount if amount > 0 else 0.0,
            'credit': abs(amount) if amount < 0 else 0.0,
        }
    
    def _prepare_move(self):
        journal = self.journal_id
        # account_date = self.date or fields.Datetime.now()
        account_date = self.date or fields.Date.context_today.strftime(DF)
        return {
            # 'direct_payment_id' : self.id,
            'move_type' : 'entry',
            'name': '/',
            'date': account_date,
            'journal_id' : journal.id,
            'ref': self.name,
            'company_id': self.company_id.id,
        }

    def action_create_move(self):
        AccountMove = self.env['account.move']
        move_lines = [l._prepare_move_line() for l in self.line_ids]
        move_lines = self.direct_payment_hook(move_lines)
        
        total = sum([ml['debit'] - ml['credit'] for ml in move_lines])
        if total:
            payable_move_lines = self._prepare_payable_move_line(-1*total)
            if not float_is_zero(total + payable_move_lines['debit'] - payable_move_lines['credit'], 
                            precision_digits=self.company_id.currency_id.decimal_places):
                rounding_move_lines = self._prepare_rounding_move_line(total + payable_move_lines['debit'] - payable_move_lines['credit'])
                move_lines.append(rounding_move_lines)
            move_lines.append(payable_move_lines)

        move_dict = self._prepare_move()
        move_dict.update({'line_ids': list(map(lambda l: (0,0,l), move_lines))})
        new_move = AccountMove.create(move_dict)
        self.account_move_id = new_move.id
        new_move._post()

        return True
    
    def action_confirm(self):
        for payment in self:
            if payment.state!='draft':
                raise ValidationError(_('You cannot Confirm payment that is not in a Draft state'))
            for line in payment.line_ids:
                if line.amount is not None and line.amount <= 0:
                    raise ValidationError(_('You cannot confirm payment if any amount in payment lines is equal to or less than 0'))
            # if payment.name == 'New':
            #     payment.name = self.env['ir.sequence'].next_by_code('account.direct.payment')
            payment.state="confirm"

    def action_post(self):
        for payment in self:
            if payment.state!='confirm':
                raise ValidationError(_('You cannot set Post payment that is not in a Confirmed State'))
            payment.action_create_move()
            payment.state="posted"
            payment.name = payment.account_move_id.name

class DirectPaymentLine(models.Model):
    _inherit = 'account.direct.payment.line'

    plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")
    has_plantation = fields.Boolean('Has Plantation')

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

    @api.onchange('plantation_activity_id')
    def _onchange_plantation_activity_id(self):
        if self.plantation_activity_id:
        # if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
            self.has_plantation = True
            self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False