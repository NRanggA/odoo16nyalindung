from odoo import models, fields, api, _, Command
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta



class HrEmployeeExpense(models.Model):
    _name = 'hr.employee.expense'
    _description = 'Employee Expense'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search([('type', 'in', ('bank', 'cash')), ('company_id', '=', default_company_id)], limit=1)
        return journal.id

    name = fields.Char(string="Number", default="New")
    date = fields.Date('Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Partner', copy=False, ondelete='restrict')
    # employee_category = fields.Boolean(string="Employee", related="partner_id.employee_category")
    # payment_request_type = fields.Selection([
    #     ('direct_inbound', 'Direct Inbound Payment'), 
    #     ('direct_outbound', 'Direct Outbound Payment')])
    description = fields.Text(string="Description")
    currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda s: s.env.company.currency_id.id,
        required=True, ondelete='restrict')
    journal_id = fields.Many2one('account.journal', string='Expense Journal', 
        check_company=True, domain="[('type', '=', ['bank','cash'])]",
        default=_default_journal_id, help="The journal used when the expense is done.")
    
    line_ids = fields.One2many("hr.employee.expense.line", "payment_id", string="Lines")
    amount_total = fields.Monetary(compute='_amount_total', string='Total Amount', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('posted', 'Posted'), 
        ('done', 'Closed'), 
        ('cancel', 'Cancel')], default="draft", tracking=True)
    
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', 
        copy=False, readonly=True)
    
    payment_state = fields.Selection([('no', 'Nothing To Pay'), 
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        # ('partial', 'Partially Paid'),
        ('paid', 'Paid')], compute='_payment_state', compute_sudo=True, 
        string='Payment Status', store=True)
    
    amount_residual = fields.Monetary(compute='_payment_state', string='Amount to Pay', store=True, compute_sudo=True)
    company_id = fields.Many2one("res.company", string="Company", 
        default=lambda s: s.env.company.id, tracking=True,
    )
    requested_by = fields.Many2one("res.users", string="Requested by", 
        default=lambda s: s.env.uid, tracking=True, index=True,
    )
    settelement_date = fields.Date('Settlement Date')
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
    advance_to_settle_ids = fields.Many2many('hr.employee.expense', 'hr_employee_account_direct_payment_to_advance_rel',
        'settlement_id', 'advance_id', string="Employee Advance", domain="[('advance_residual','>',0)]")
    
    settlement_ids = fields.Many2many('hr.employee.expense','hr_employee_expense_settlement_rel',
        'advance_id','settlement_id', string='Settlement',compute="_compute_settlement")
    
    employee_expense_settlement_count = fields.Integer('Settlement Count', compute='_get_count_employee_expense_settlement')

    advance_amount_settle = fields.Monetary(compute="_compute_settlement_amount", string="Advance Amount", store=True)
    amount_total2 = fields.Monetary(compute="_compute_settlement_amount", string="Amount Total", store=True)
    account_direct_payment_id = fields.Many2one('account.direct.payment', string='Direct Payment')
    has_amount = fields.Boolean('Has Amount', compute='_compute_amount_to_clear')
    employee_expense_direct_payment_count = fields.Integer('Journal Count', compute='_get_count_employee_expense')

    def _compute_settlement(self):
        for record in self:
            settlement_ids = []
            if not record.expense_report:
                report_ids = record.search([('expense_report', '=', True),('employee_id', '=', record.employee_id.id)])
                for report_id in report_ids:
                    advance_id = report_id.advance_to_settle_ids.filtered(lambda adv: adv.id == record.id)
                    if advance_id:
                        settlement_ids.append(report_id.id)
            record.settlement_ids = [Command.set(settlement_ids)]

    @api.depends('advance_amount_settle')
    def _compute_amount_to_clear(self):
        for record in self:
            record.has_amount = True if sum(record.advance_to_settle_ids.mapped('advance_amount_settle')) > 0 else False

    @api.depends('line_ids', 'line_ids.amount')
    def _amount_total(self):
        for payment in self:
            payment.write({
                    'amount_total': sum(payment.line_ids.mapped('amount')),
                })

    @api.depends(
        'amount_total',
        'account_move_id', 
        'account_move_id.line_ids',
        'account_move_id.line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'account_move_id.line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'account_move_id.line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'account_move_id.line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'account_move_id.line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'account_move_id.line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'account_move_id.line_ids.debit',
        'account_move_id.line_ids.credit',
        'account_move_id.line_ids.currency_id',
        'account_move_id.line_ids.amount_currency',
        'account_move_id.line_ids.amount_residual',
        'account_move_id.line_ids.amount_residual_currency',
        'account_move_id.line_ids.payment_id.state',
        'account_move_id.line_ids.full_reconcile_id'
        )
    def _payment_state(self):
        for payment in self:
            new_payment_state = 'no'
            currency = payment.currency_id
            amount_residual = 0.0
            if payment.account_move_id and payment.account_move_id.state=='posted':
                new_payment_state = 'not_paid'
                for line in payment.account_move_id.line_ids.filtered(lambda l : l.account_type in ('receivable', 'payable')):
                    amount_residual += line.amount_residual
                    if not line.full_reconcile_id:
                        continue
                    
                    if currency.is_zero(line.amount_residual):
                        reconciled_payments = payment.account_move_id._get_reconciled_payments()
                        if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                            new_payment_state = 'paid'
                        else:
                            new_payment_state = 'in_payment'
            
            payment.write({
                'payment_state': new_payment_state,
                'amount_residual': amount_residual,
                })

    def unlink(self):
        for payment in self:
            if not payment.state == 'cancel':
                raise UserError(_('In order to delete a Direct Payment, you must cancel it first.'))
        return super(HrEmployeeExpense, self).unlink()

    ##########################
    #      HELPER METHOD     #
    ##########################
    def _prepare_move(self):
        journal = self.journal_id
        # account_date = self.date or fields.Datetime.now()
        account_date = self.date or fields.Date.context_today.strftime(DF)
        return {
            # 'direct_payment_id' : self.id,
            'move_type' : 'entry',
            'name': '/',
            'date': account_date,
            'journal_id' : self.employee_advance_journal_id.id if self.is_advance or self.expense_report else journal.id,
            'ref': self.name,
            'company_id': self.company_id.id,
            'employee_expense' : self.id
        }

    def _prepare_payable_move_line(self, amount): 
        partner =  self.partner_id or self.requested_by.partner_id or False

        return {
            'partner_id': partner.id if partner else False,
            'name': _("Request of Direct Payment"),
            # 'account_id': self.company_id.partner_id.property_account_payable_id.id,
            'account_id': self.contra_account_for_advance.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            # 'product_id': self.product_id.id,
            'debit': amount if amount > 0 else 0.0,
            'credit': abs(amount) if amount < 0 else 0.0,
        }

    def _prepare_rounding_move_line(self, amount):
        partner =  self.partner_id or self.requested_by.partner_id or False
        return {
            'partner_id': partner.id if partner else False,
            'name': _("Unrealized Rounding of Direct Payment"),
            'account_id': partner.property_account_payable_id.id if partner else self.company_id.partner_id.property_account_payable_id.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            # 'product_id': self.product_id.id,
            'debit': amount if amount > 0 else 0.0,
            'credit': abs(amount) if amount < 0 else 0.0,
        }

    # def direct_payment_hook(self, move_lines):
    #     return move_lines

    ##########################
    #     BUSINESS METHOD    #
    ##########################
    
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

        if self.advance_to_settle_ids.filtered(lambda a: a.advance_residual>0.0):
            settlement_advances = self.account_move_id.line_ids.filtered(lambda l: l.account_id==self.company_id.employee_advance_account_id)
            advances_to_settle = self.advance_to_settle_ids.mapped('account_move_id.line_ids').filtered(lambda l: l.account_id==self.company_id.employee_advance_account_id)
            (settlement_advances + advances_to_settle).reconcile()

        return True
    
    def action_get_direct_state(self):
        for record in self:
            this_um = abs(record.advance_amount_settle)
            this_settelement = record.amount_total
            direct_state = False
            if this_um > this_settelement:
                direct_state = 'receive'
            elif this_settelement > this_um:
                direct_state = 'send'

        return direct_state
    
    def action_create_direct_payment(self):
        for record in self:
            direct_payment = self.env['account.direct.payment'].sudo().create({
                'partner_id' : record.partner_id.id,
                'date' : record.date,
                'requested_by' : record.requested_by.id,
                'description' : record.description,
                'journal_id' : record.journal_id.id,
                'currency_id' : record.currency_id.id,
                'is_advance' : record.is_advance,
                'expense_report' : record.expense_report,
                'employee_expense_id' : record.id,
                'direct_state' : record.action_get_direct_state()
            })

            if record.expense_report:
                direct_payment.write({
                        'line_ids' : [Command.create({
                            'product_id' : line.product_id.id,
                            'name' : line.name,
                            'account_id' : record.contra_account_for_advance.id,
                            'amount' : abs(record.amount_total2),
                        }) for line in record.line_ids[0]]
                })
            else:
                direct_payment.write({
                        'line_ids' : [Command.create({
                            'product_id' : line.product_id.id,
                            'name' : line.name,
                            'account_id' : record.contra_account_for_advance.id,
                            'amount' : line.amount if (record.is_advance and not record.expense_report) else record.amount_total2,
                        }) for line in record.line_ids]
                })
            
            record.account_direct_payment_id = direct_payment

        return True

    def action_confirm(self):
        for payment in self:
            # if payment.state!='draft':
            #     raise ValidationError(_('You cannot Confirm payment that is not in a Draft state'))
            for line in payment.line_ids:
                if line.amount is not None and line.amount <= 0:
                    raise ValidationError(_('You cannot confirm payment if any amount in payment lines is equal to or less than 0'))
            if payment.name == 'New':    
                if payment.is_advance == False:
                    payment.name = self.env['ir.sequence'].next_by_code('hr.employee.expense.advance')
                else:
                    payment.name = self.env['ir.sequence'].next_by_code('hr.employee.expense')
            payment.state="confirm"

    def action_cancel(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for payment in self:
            # Hapus jurnal yang sudah dibuat
            if payment.account_move_id:
                move_id = payment.account_move_id.id
                if move_id:
                    payment.account_move_id.button_draft()
                    payment.account_move_id = False
                    self.env['account.move'].browse(move_id).unlink()
                # raise ValidationError(_('You cannot set Cancel payment that is already create a journal entry'))
            # Hapus direct payment yang sudah dibuat
            if payment.account_direct_payment_id:
                direct_payment_id = payment.account_direct_payment_id.id
                if direct_payment_id:
                    payment.account_direct_payment_id.action_cancel()
                    payment.account_direct_payment_id = False
                    self.env['account.direct.payment'].browse(direct_payment_id).unlink()

            payment.state="cancel"

    def action_draft(self):
        for payment in self:
            payment.state="draft"

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
    @api.constrains('date','settelement_date')
    def _constrains_settelement_date(self):
        for record in self:
            if not record.expense_report:
                advanced_ids = record.search([
                    ('id', '!=', record.id),
                    ('expense_report', '=', False),
                    ('employee_id', '=', record.employee_id.id),
                    ('state', 'not in', ('done','reject','cancel')),

                    ])
                if advanced_ids:
                    for advanced_id in advanced_ids:
                        if advanced_id.settelement_date < fields.Date.today():
                            for settle_id in record.settlement_ids:
                                if settle_id.state not in ('done'):
                                    raise ValidationError('Cash advance number %s has not been settled yet. Please finalize the settlement before continuing'%(advanced_id.name))




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
        move_lines.extend(self.get_advance_move_line())
        return move_lines

    def employee_submit(self):
        for payment in self:
            if payment.employee_expense_state!='draft':
                raise ValidationError(_('You cannot Submit Expense that is not in a Draft state'))
            payment.employee_expense_state="submit"
            payment.validation_settlement_date_by_date()
            payment.validation_setteled()

    def employee_approve(self):
        for payment in self:
            if payment.employee_expense_state!='submit':
                raise ValidationError(_('You cannot Approve Expense that is not in a Submitted state'))
            payment.write({
                'employee_expense_state': "approved",
                'approved_by': self.env.user.id,
                })
            payment.validation_setteled()
            payment.action_confirm()
            payment.action_create_move()
            this_um = abs(self.advance_amount_settle)
            this_settelement = self.amount_total
            if (payment.is_advance and not payment.expense_report) or payment.expense_report and (this_um > this_settelement or this_um < this_settelement):
                payment.action_create_direct_payment()

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
            # if payment.employee_expense_state!='reject':
            #     raise ValidationError(_('You cannot Cancel Expense that is not in a Rejected state'))
            payment.write({
                'employee_expense_state': "cancel",
                })
            payment.action_cancel()

    def employee_set_draft(self):
        for payment in self:
            # if payment.employee_expense_state != 'reject':
            # # if payment.employee_expense_state in ['reject', 'cancel']:
            #     raise ValidationError(_('You cannot Set Draft Expense that is not in a Rejected state'))
            payment.write({
                'employee_expense_state': "draft",
                })
            # payment.action_draft()

    def _get_count_employee_expense(self):
        for record in self:
            journal_count = self.env['account.move'].search_count([('employee_expense', '=', record.id)])
            direct_count = self.env['account.direct.payment'].search_count([('employee_expense_id', '=', record.id)])
            record.employee_expense_journal_count = journal_count
            record.employee_expense_direct_payment_count = direct_count
    def _get_count_employee_expense_settlement(self):
        for record in self:
            record.employee_expense_settlement_count = len(record.settlement_ids.ids)
    
    def action_open_employee_expense_journal(self):
        result = self.env["ir.actions.actions"]._for_xml_id('account.action_move_journal_line')
        result['domain'] = [('employee_expense', '=', self.id)]
            
        return result
    
    def action_open_direct_payment(self):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_direct_payment.account_direct_payment_action')
        result['domain'] = [('employee_expense_id', '=', self.id)]
            
        return result

    def action_open_settlement(self):
        result = self.env["ir.actions.actions"]._for_xml_id('nyalindung_direct_payment_expense.hr_account_employee_expense_action_all')
        if len(self.settlement_ids.ids) == 1:
            result['res_id'] = self.settlement_ids.id
            result['view_mode'] = 'form'
            result['views'] = [(self.env.ref('nyalindung_direct_payment_expense.account_employee_expense_form').id, 'form')]
        else:
            result['domain'] = [('id', 'in', self.settlement_ids.ids)]
            
        return result

    def validation_settlement_date_by_date(self):
        for record in self:
            if record.settelement_date and record.settelement_date < record.date:
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
    
class HrEmployeeExpenseLine(models.Model):
    _name = "hr.employee.expense.line"
    _description = "Employee Expense Line"

    payment_id = fields.Many2one("hr.employee.expense", string="Direct Payment", ondelete="cascade")
    currency_id = fields.Many2one("res.currency", related="payment_id.currency_id", string="Currency", store=True)
    product_id = fields.Many2one("product.product", string="Product", ondelete="restrict", domain=[('detailed_type','!=','product')])
    account_id = fields.Many2one("account.account", "Account", ondelete="restrict", required=True)
    analytic_account_id = fields.Many2one("account.analytic.account", "Analytic Account", ondelete="restrict")
    name = fields.Char(string="Description", required=True)
    amount = fields.Monetary('Amount')

    varieties_id = fields.Many2one('plant.varieties', string="ORG", ondelete='restrict')
    location_type_id    = fields.Many2one("lhm.location.type", string="Tipe", ondelete="restrict")
    location_id         = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    activity_id         = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    varieties_validator = fields.Boolean(compute='_set_plantation_validator', store=True, string="Varieties Validator")
    @api.depends('location_type_id')
    def _set_plantation_validator(self):
        for line in self:
            validator = False
            if line.location_type_id:
                # Plantation, GC, IDC, PJ, NS => True (artinya wajib diisi)
                validator = line.location_type_id.code in ('FC','GC','IDC', 'PJ') #, 'NS'
            line.varieties_validator = validator
    filtered_activities = fields.Many2many('lhm.activity', 'lhm_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    filtered_locations = fields.Many2many('lhm.location', 'lhm_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')

    
    @api.depends('varieties_id','location_type_id')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.location_type_id.code in ('WS','VH','MA','GC','MC','LB'):
                locations = self.env['lhm.location'].sudo().search([('type_id','=',line.location_type_id.id)])
            else: # PLANTATION, PJ, NS
                locations = self.env['lhm.location'].search([('type_id','=',line.location_type_id.id),('varieties_id','=',line.varieties_id.id)])
            line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('varieties_id','location_type_id', 'location_id')
    def _filter_activities(self):
        for line in self:
            # doc_form = self.env['res.doc.type'].search([('code','=','lhm')], limit=1)
            if line.location_type_id and line.location_type_id.project and line.location_id:
                projects = self.env['lhm.project'].search([('location_id','=',line.location_id.id)])
                project_activity_ids = []
                for project in projects:
                        project_activity_ids += [x.activity_id.id for x in project.line_ids]

                if project_activity_ids:
                    line.filtered_activities = [(6, 0, project_activity_ids)]
                else:
                    line.filtered_activities = []
            else:
                if line.location_type_id.code in ('WS','VH','MA','NS','LB'):
                    activities = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])
                else: # GC, IDC, PLANTATION
                    if line.varieties_id:
                        if line.location_type_id.general_charge:
                            activities = line.varieties_id.general_charges_activity_ids
                        elif line.location_type_id.indirect:
                            activities = line.varieties_id.indirect_cost_activity_ids
                        # menambahkan tipe lokasi mills 
                        elif line.location_type_id.mills:
                            activities = line.varieties_id.mill_costs_ids
                        else:
                            activities = line.varieties_id.harvest_activity_ids
                            activities |= line.varieties_id.upkeep_activity_ids
                    else:
                        # activities = self.env['lhm.activity'].search([('type_id','=',line.location_type_id.id)])
                        activities = []
                if False: 
                    act_ids = []
                    for act in activities:
                        if doc_form.id in act.doc_ids.ids:
                            act_ids.append(act.id)
                    line.filtered_activities = [(6, 0, act_ids)]
                else:
                    line.filtered_activities = [(6, 0, activities.ids)] if activities else []

    # Menambahkan onchange tipe lokasi yang otomatis akan mengisi ke varieties_id 
    @api.onchange('location_type_id')
    def _onchange_location_type_id(self):
        if self.location_type_id:
            self.varieties_id = self.location_type_id.varieties_id.id

    # onchange untuk membuat account terisi otomatis ketika memilih aktivitas
    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            self.account_id = self.activity_id.account_id.id


    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.account_id = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            self.name = self.product_id.name

    def _prepare_move_line(self):
        amount = self.currency_id.compute(self.amount, self.payment_id.company_id.currency_id)
        partner =  self.payment_id.partner_id or self.payment_id.requested_by.partner_id or False
        return {
            'partner_id': partner.id if partner else False,
            'name': self.name,
            'account_id': self.account_id.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            'product_id': self.product_id.id,
            'debit': amount if amount > 0 else 0.0,
            'credit': abs(amount) if amount < 0 else 0.0,
        }

    def unlink(self):
        for line in self:
            if line.payment_id.state!='draft':
                raise UserError(_('Cannot delete a Direct Payment line which is in state \'%s\'.') % (line.payment_id.state,))
        return super(HrEmployeeExpenseLine, self).unlink()