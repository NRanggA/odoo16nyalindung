from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime

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
    expense_report = fields.Boolean('Expense Report')
    is_advance = fields.Boolean('Employee Advance')
    direct_state = fields.Selection([
        ('send', 'Send'),
        ('receive', 'Receive'),
    ], string='Direct State', readonly=True)
    employee_expense_id = fields.Many2one('hr.employee.expense', string='Employee Expense')

    # Partner Bank
    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Partner Bank Account',
        domain="[('partner_id', '=', partner_id)]",
    )

    general             = fields.Boolean(related='partner_id.general',string="general")
    partner_bank_name   = fields.Char('Partner Bank Name')
    partner_bank_number = fields.Char('Partner Bank Number') 


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:  # Pastikan partner_id tidak kosong
            if self.partner_id.general:
                # Jika 'general' True, kosongkan partner_bank_id
                self.partner_bank_id = False
            else:
                # Cari rekening bank partner yang memiliki allow_out_payment = True
                partner_bank = self.env['res.partner.bank'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('allow_out_payment', '=', True),
                ], limit=1)
                self.partner_bank_id = partner_bank.id if partner_bank else False
        else:
            # Kosongkan partner_bank_id jika partner_id dihapus
            self.partner_bank_id = False
        
        if self.direct_state == 'receive':
            return {'domain': {'partner_id': [('customer_category', '!=', False)]}}
        if self.direct_state == 'send':
            return {'domain': {'partner_id': [('vendor_category', '!=', False)]}}


    def _prepare_payable_move_line(self, amount):
        partner =  self.partner_id or self.requested_by.partner_id or False
        if self.direct_state == 'send':
            credit_account = self.journal_id.outbound_payment_method_line_ids.payment_account_id
        else:
            credit_account = self.journal_id.inbound_payment_method_line_ids.payment_account_id
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
            'is_payment' : True,
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
    
    def action_cancel(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for payment in self:
            for payment in self:
                if payment.account_move_id:
                    payment.account_move_id.button_cancel()
            payment.state="cancel"
    
    def action_confirm(self):
        for payment in self:
            if payment.state!='draft':
                raise ValidationError(_('You cannot Confirm payment that is not in a Draft state'))
            
            # Tambahkan pengecekan konteks ketika dari wizard, dan validasi sekali lagi nilai amount tidak boleh 0
            if self.env.context.get('from_wizard'):
                for line in payment.line_ids:
                    if line.amount is not None and line.amount <= 0:
                        raise ValidationError(_('You cannot confirm payment if any amount in payment lines is equal to or less than 0'))
                payment.state = "confirm"
                continue
            
            # Ketika employee_expense_id ada, maka akan memunculkan wizard
            # if self.employee_expense_id:
            confirmation_message = "Apakah Anda yakin ingin memproses dari Rekening: %s?" % self.journal_id.name
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.action.confirm',
                'view_mode': 'form',
                'view_id': self.env.ref('nyalindung_direct_payment_expense.view_wizard_action_confirm').id,
                'target': 'new',
                'context': {
                    'active_id': self.id, 
                    'active_model': self._name,
                    'confirmation_message': confirmation_message  
                },
            }
            
            # Dikomen karena harus memunculkan wizard confirm terus 
            # for line in payment.line_ids:
            #     if line.amount is not None and line.amount <= 0:
            #         raise ValidationError(_('You cannot confirm payment if any amount in payment lines is equal to or less than 0'))
            # # if payment.name == 'New':
            # #     payment.name = self.env['ir.sequence'].next_by_code('account.direct.payment')
            # payment.state="confirm"

    def action_post(self):
        for payment in self:
            if payment.state!='confirm':
                raise ValidationError(_('You cannot set Post payment that is not in a Confirmed State'))
            
            if not payment.account_move_id:
                payment.action_create_move()
            else:
                payment.account_move_id.line_ids.unlink()
                move_lines = [l._prepare_move_line() for l in payment.line_ids]
                total = sum([ml['debit'] - ml['credit'] for ml in move_lines])
                if total:
                    payable_move_lines = self._prepare_payable_move_line(-1*total)
                    if not float_is_zero(total + payable_move_lines['debit'] - payable_move_lines['credit'], 
                                    precision_digits=self.company_id.currency_id.decimal_places):
                        rounding_move_lines = self._prepare_rounding_move_line(total + payable_move_lines['debit'] - payable_move_lines['credit'])
                        move_lines.append(rounding_move_lines)
                    move_lines.append(payable_move_lines)
                payment.account_move_id.write({'line_ids': list(map(lambda l: (0,0,l), move_lines)) })

            if payment.account_move_id and payment.account_move_id.state == 'cancel':
                payment.account_move_id.action_post()

            if payment.name != payment.account_move_id.name:
                if payment.journal_id.type in ['bank', 'cash'] and payment.direct_state in ['receive', 'send']:
                    sequence = None
                    if payment.direct_state == 'receive' and payment.journal_id.sequence_id:
                        sequence = payment.journal_id.sequence_id
                    elif payment.direct_state == 'send' and payment.journal_id.sequence_out_id:
                        sequence = payment.journal_id.sequence_out_id

                    if not sequence:
                        raise ValidationError("Sequence untuk jurnal belum dikonfigurasi.")

                    payment_date = payment.date or datetime.now().date()
                    sequence_number = sequence.with_context(ir_sequence_date=payment_date).next_by_id()

                    if not sequence_number:
                        raise ValidationError("Gagal mendapatkan nomor sequence.")

                    payment.name = sequence_number
                    payment.account_move_id.name = payment.name
            payment.state="posted"

    def unlink(self):
        for payment in self:
            if payment.employee_expense_id:
                if payment.employee_expense_id.state != 'draft':
                    if payment.employee_expense_id.expense_report:
                        raise UserError(_('Kamu tidak bisa mendelete dokument ini karena status dokumen My Reports tidak diposisi draft!'))
                    else: 
                        raise UserError(_('Kamu tidak bisa mendelete dokument ini karena status dokumen My Advance tidak diposisi draft!'))
        return super(DirectPayment, self).unlink()

    # @api.model
    # def create(self, vals):
    #     payment = super(DirectPayment, self).create(vals)

    #     # Logika yang Anda tambahkan
    #     if payment.journal_id.type in ['bank', 'cash'] and payment.direct_state in ['receive', 'send']:
    #         sequence = None
    #         if payment.direct_state == 'receive' and payment.journal_id.sequence_id:
    #             sequence = payment.journal_id.sequence_id
    #         elif payment.direct_state == 'send' and payment.journal_id.sequence_out_id:
    #             sequence = payment.journal_id.sequence_out_id

    #         if not sequence:
    #             raise ValidationError("Sequence untuk jurnal belum dikonfigurasi.")

    #         payment_date = payment.date or datetime.now().date()
    #         sequence_number = sequence.with_context(ir_sequence_date=payment_date).next_by_id()

    #         if not sequence_number:
    #             raise ValidationError("Gagal mendapatkan nomor sequence.")

    #         payment.name = sequence_number


    #     return payment

class DirectPaymentLine(models.Model):
    _inherit = 'account.direct.payment.line'

    plantation_location_type_id = fields.Many2one("lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_varieties_id = fields.Many2one('plant.varieties', string='ORG', ondelete='restrict')
    filtered_locations = fields.Many2many('lhm.location', 'adpl_filtered_locations_rel', compute='_filter_locations', string='Filter Lokasi')
    plantation_location_id = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    filtered_activities = fields.Many2many('lhm.activity', 'adpl_filtered_activities_rel', compute='_filter_activities', string='Filter Activities')
    plantation_activity_id = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    plantation_validator = fields.Boolean(string="Plantation Validator", related="plantation_location_type_id.no_line")
    varieties_validator = fields.Boolean(compute='_set_plantation_validator', store=True, string="Varieties Validator")
    @api.depends('plantation_location_type_id')
    def _set_plantation_validator(self):
        for line in self:
            validator = False
            if line.plantation_location_type_id:
                # Plantation FC, GC, IDC, PJ, NS => True (artinya wajib diisi)
                validator = line.plantation_location_type_id.code in ('FC','GC','IDC','PJ')
            line.varieties_validator = validator
    has_plantation = fields.Boolean('Has Plantation')

    @api.depends('plantation_varieties_id','plantation_location_type_id', 'payment_id.state')
    def _filter_locations(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.payment_id.state!='draft' or not line.plantation_location_type_id:
                line.filtered_locations = []
            else:
                if line.plantation_location_type_id.code in ('WS','VH','MA','LB','NS','GC','MC'):
                    locations = self.env['lhm.location'].sudo().search([('type_id','=',line.plantation_location_type_id.id)])
                else: # PLANTATION, PJ, IDC
                    locations = self.env['lhm.location'].search([('type_id','=',line.plantation_location_type_id.id),('varieties_id','=',line.plantation_varieties_id.id)])
                line.filtered_locations = [(6,0,locations.ids)] if locations else []

    @api.depends('plantation_varieties_id','plantation_location_type_id', 'plantation_location_id', 'payment_id.state')
    def _filter_activities(self):
        # biar tidak di run setiap saat
        for line in self:
            if line.payment_id.state!='draft' or not line.plantation_location_type_id:
                line.filtered_activities = []
            else:
                doc_form = self.env['res.doc.type'].search([('code','=','lhm')], limit=1)
                if line.plantation_location_type_id and line.plantation_location_type_id.project and line.plantation_location_id:
                    projects = self.env['lhm.project'].search([('location_id','=',line.plantation_location_id.id)])
                    project_activity_ids = []
                    for project in projects:
                        # if doc_form:
                        #     project_activity_ids += [x.activity_id.id for x in project.line_ids if doc_form.id in x.doc_ids.ids]
                        # else:
                            project_activity_ids += [x.activity_id.id for x in project.line_ids]

                    if project_activity_ids:
                        line.filtered_activities = [(6, 0, project_activity_ids)]
                    else:
                        line.filtered_activities = []
                else:
                    if line.plantation_location_type_id.code in ('WS','VH','MA','LB','NS'):
                        activities = self.env['lhm.activity'].search([('type_id','=',line.plantation_location_type_id.id)])
                    else: # GC, IDC, PLANTATION FC
                        if line.plantation_varieties_id:
                            if line.plantation_location_type_id.general_charge:
                                activities = line.plantation_varieties_id.general_charges_activity_ids
                            elif line.plantation_location_type_id.indirect:
                                activities = line.plantation_varieties_id.indirect_cost_activity_ids
                            # Menambahkan tipe lokasi Mills (MC)
                            elif line.plantation_location_type_id.mills:
                                activities = line.plantation_varieties_id.mill_costs_ids
                            else:
                                activities = line.plantation_varieties_id.harvest_activity_ids
                                activities |= line.plantation_varieties_id.upkeep_activity_ids
                        else:
                            # activities = self.env['lhm.activity'].search([('type_id','=',line.plantation_location_type_id.id)])
                            activities = []
                    if False: #doc_form:
                        act_ids = []
                        for act in activities:
                            if doc_form.id in act.doc_ids.ids:
                                act_ids.append(act.id)
                        line.filtered_activities = [(6, 0, act_ids)]
                    else:
                        line.filtered_activities = [(6, 0, activities.ids)] if activities else []

    def _prepare_move_line(self):
        amount = self.currency_id.compute(self.amount, self.payment_id.company_id.currency_id)
        partner =  self.payment_id.partner_id or self.payment_id.requested_by.partner_id or False
        return {
            'partner_id': partner.id if partner else False,
            'name': self.name,
            'account_id': self.account_id.id,
            # 'analytic_account_id': self.analytic_account_id.id,
            'product_id': self.product_id.id,
            # 'debit': (abs(amount) if amount < 0 else 0.0) if self.payment_id.expense_report or self.payment_id.direct_state == 'receive' else (amount if amount > 0 else 0.0),
            'debit': (abs(amount) if amount < 0 else 0.0) if self.payment_id.direct_state == 'receive' else (amount if amount > 0 else 0.0),
            # 'credit': (amount if amount > 0 else 0.0) if self.payment_id.expense_report or self.payment_id.direct_state == 'receive' else (abs(amount) if amount < 0 else 0.0),
            'credit': (amount if amount > 0 else 0.0) if self.payment_id.direct_state == 'receive' else (abs(amount) if amount < 0 else 0.0),
            'plantation_location_type_id': self.plantation_location_type_id.id,
            'plantation_varieties_id': self.plantation_varieties_id.id,
            'plantation_location_id': self.plantation_location_id.id,
            'plantation_activity_id': self.plantation_activity_id.id,
        }

    @api.onchange('plantation_location_type_id')
    def _onchange_plantation_location_type_id(self):
        if self.plantation_location_type_id:
            self.plantation_location_id = False
            self.plantation_activity_id = False
            # Menambahkan onchage ORG ketika memilih tipe lokasi
            self.plantation_varieties_id = self.plantation_location_type_id.varieties_id.id
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