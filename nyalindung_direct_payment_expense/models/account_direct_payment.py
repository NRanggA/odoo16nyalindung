from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class DirectPayment(models.Model):
    _inherit = 'account.direct.payment'

    settelement_date = fields.Date('Settelement Date', required=True)
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
    is_direct_payment = fields.Boolean('Is Direct Payment')

    def _prepare_payable_move_line(self, amount):
        partner =  self.partner_id or self.requested_by.partner_id or False
        credit_account = self.company_id.partner_id.property_account_payable_id
        if self.is_direct_payment:
            credit_account = self.journal_id.outbound_payment_method_line_ids[0].payment_account_id
        else:
            credit_account = self.employee_advance_journal_id
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
            'journal_id' : self.employee_advance_journal_id.id if self.employee_advance_journal_id else journal.id,
            'ref': self.name,
            'company_id': self.company_id.id,
            'employee_expense_id' : self.id
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
    
    def _get_count_employee_expense(self):
        for record in self:
            journal_count = self.env['account.move'].search_count([('employee_expense_id', '=', record.id)])
            record.employee_expense_journal_count = journal_count

    
    def action_open_employee_expense_journal(self):
        result = self.env["ir.actions.actions"]._for_xml_id('account.action_move_journal_line')
        result['domain'] = [('employee_expense_id', '=', self.id)]
            
        return result
    
    @api.onchange('is_direct_payment')
    def onchange_is_direct_payment(self):
        if self.is_direct_payment:
            account = self.company_id.contra_account_for_advance
            if not account:
                raise ValidationError(_('Please configure Contra Account for Advance on your Accounting Settings'))
            self.line_ids = [(0,0,{
                'name': 'Request of Employee Advance',
                'account_id': account.id,
                })]

    def employee_submit(self):
        res = super().employee_submit()
        self.validation_settlement_date_by_date()
        return res

    def validation_settlement_date_by_date(self):
        for record in self:
            if record.settelement_date < record.date:
                raise ValidationError("Settlement Date cannot be less than Date")
            
    def validation_setteled(self):
        for record in self:
            setteled = self.search([
                ('employee_id', '=', record.employee_id.id),
                ('payment_state', '!=', 'not_paid'),
            ], limit=1, order='settelement_date desc')
            
            if setteled:
                if setteled.settelement_date and record.date > setteled.settelement_date:
                    raise ValidationError("You can't request direct payment if the date is more than the your direct payment that not setteled")
                
    def employee_approve(self):
        res = super().employee_approve()
        for record in self:
            record.action_create_move()
        return res

    @api.model
    def create(self, vals):
        record = super(DirectPayment, self).create(vals)
        record.validation_setteled()
        return record

    def write(self, vals):
        res = super(DirectPayment, self).write(vals)
        self.validation_setteled()
        return res

class DirectPaymentLine(models.Model):
    _inherit = 'account.direct.payment.line'

    plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")    

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