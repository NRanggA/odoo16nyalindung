from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_state = fields.Selection(selection_add=[('written_off', 'Dihapus')])

class AccountWriteOff(models.Model):
    _name = 'account.write.off'
    _description = 'Account Write Off'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char('Name', copy=False)
    move_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill')], string='Move Type', required=True)
    date = fields.Date('Write-off Date', required=True, tracking=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Partner', required=False, ondelete="restrict")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], string='Status', default='draft', tracking=True)

    line_ids = fields.One2many('account.write.off.line', 'account_write_off_id', string="Invoice/Bills")
    # account_write_off = fields.Many2one('account.account', related='company_id.account_write_off', 
    #         readonly=False, string="Account Write Off")
    write_off_account_id = fields.Many2one('account.account', required=True, string='Write-off Account')
    
    write_off_default_journal_id = fields.Many2one('account.journal', 
            related='company_id.write_off_default_journal_id', 
            required=True, string="Journal")
    # write_off_default_journal_id = fields.Many2one('account.journal',  required=True, string="Journal")
    
    # Field to store journal entry
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, tracking=True)

    ############################################################################
    #                HELPER
    ############################################################################

    def get_outstanding(self):
        self.ensure_one()
        for rec in self.filtered(lambda x: x.state=='draft'):
            domain = [
                ('partner_id', '=', rec.partner_id.id),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'in_payment', 'partial']),
                ('amount_residual', '>', 0)
            ]
            if rec.move_type == 'out_invoice':
                domain.append(('move_type', '=', 'out_invoice'))
            elif rec.move_type == 'in_invoice':
                domain.append(('move_type', '=', 'in_invoice'))

            moves = self.env['account.move'].search(domain)
            line_to_add = []
            for move in moves:
                move_line = move.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable','liability_payable'))
                if move not in rec.line_ids.mapped('move_id'):
                    line_to_add.append((0, 0, {
                        'move_id': move.id,
                        'amount_residual': move.amount_residual,
                        'move_line_id': move_line.id,
                        'write_off_account_id': rec.write_off_account_id.id,
                    }))
                else:
                    line_to_add((1, rec.line_ids.filtered(lambda l: l.move_id.id == move.id).id, {
                        'move_line_id': move_line.id,
                        'amount_residual': move.amount_residual,
                        'write_off_account_id': rec.write_off_account_id.id,
                    }))
            rec.line_ids = line_to_add
            
    ############################################################################
    #                BUSINESS METHOD
    ############################################################################

    def action_post(self):
        for rec in self:
            writeoff_move_lines = []
            writeoff_amount_total = 0
            account_counterpart = False
            for writeoff_line in rec.line_ids:
                # Validate if the residual is not valid anymore
                if writeoff_line.move_id.amount_residual != writeoff_line.amount_residual:
                    raise UserError(_('The residual amount of the invoice has changed. Please click "Get Outstanding" to get the latest residual amount.'))
                account_counterpart = writeoff_line.move_line_id.account_id
                if writeoff_line.write_off_amount and writeoff_line.write_off_account_id:
                    # write_off_amount = self.currency_id._convert(pline.write_off_amount, self.move_id.company_currency_id, self.company_id, self.date)
                    write_off_amount = writeoff_line.write_off_amount
                    wo_debit = wo_credit = amount_currency = 0
                    if rec.move_type == 'in_invoice':
                        if write_off_amount < 0:
                            wo_debit = abs(write_off_amount)
                        else:
                            wo_credit = write_off_amount
                        writeoff_amount_total += wo_credit - wo_debit
                        amount_currency = -writeoff_line.write_off_amount
                    else:
                        if write_off_amount > 0:
                            wo_debit = write_off_amount
                        else:
                            wo_credit = abs(write_off_amount)
                        writeoff_amount_total += wo_credit - wo_debit
                        amount_currency = writeoff_line.write_off_amount
                    
                    write_off_vals = {
                        'account_id': writeoff_line.write_off_account_id.id,
                        'debit': wo_debit,
                        'credit': wo_credit,
                        # 'price_unit': write_off_amount,
                        # 'quantity': 1,
                        'name': "Write-off: "+writeoff_line.reason,
                        'tax_ids': False,
                        'amount_currency': amount_currency,
                        'partner_id': rec.partner_id.id,
                    }
                    writeoff_move_lines.append((0, 0, write_off_vals))
                else:
                    writeoff_line.unlink()

            debit_tot = credit_tot = 0
            if writeoff_amount_total > 0:
                debit_tot = writeoff_amount_total
            else:
                credit_tot = abs(writeoff_amount_total)
                
            write_off_counterpart_vals = {
                'partner_id': rec.partner_id.id,
                'account_id': account_counterpart.id,
                'debit': debit_tot,
                'name': "Write-off",
                'credit': credit_tot,
            }

            writeoff_move_lines.append((0, 0, write_off_counterpart_vals))

            # for l in writeoff_move_lines:
            #     print(".>>>>>", l)

            if not writeoff_move_lines:
                continue

            if not rec.move_id:
                new_move = self.env['account.move'].create({
                    'move_type': 'entry',
                    'journal_id': rec.write_off_default_journal_id.id,
                    'date': rec.date,
                    'line_ids': writeoff_move_lines,
                    'partner_id': rec.partner_id.id,
                    'ref': rec.name,
                })
            else:
                new_move = rec.move_id
                new_move.button_draft()
                new_move.write({
                    'date': rec.date,
                    'partner_id': rec.partner_id.id,
                    'line_ids': [(2, x.id) for x in rec.move_id.line_ids] + writeoff_move_lines,
                })
            new_move._post(soft=False)

            for src_move, writeoff_move_lines in zip(rec.line_ids.move_id, new_move.line_ids.filtered(lambda x: x.account_id.account_type in ('asset_receivable','liability_payable'))):
                src_move_lines = src_move.line_ids.filtered(lambda x: x.account_id.account_type in ('asset_receivable','liability_payable'))
                (src_move_lines + writeoff_move_lines).reconcile()
            
            rec.state = 'posted'
            rec.move_id = new_move.id
            rec.name = new_move.name

    def button_draft(self):
        for rec in self:
            rec.move_id.line_ids.remove_move_reconcile()
            rec.move_id.button_cancel()
            rec.state = 'draft'

    # def action_view_journal_entry(self):
    #     self.ensure_one()
    #     action = self.env.ref('account.action_move_journal_line').read()[0]
    #     if self.journal_entry_id:
    #         action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
    #         action['res_id'] = self.journal_entry_id.id
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action

    # @api.model
    # def create(self, vals):
    #     if not vals.get('name'):
    #         current_year = datetime.now().year
    #         sequence_code = f"WO/{current_year}/"
    #         vals['name'] = self.env['ir.sequence'].next_by_code('account.write.off') or f"{sequence_code}001"

    #     record = super(AccountWriteOff, self).create(vals)
    #     record._remove_unchecked_lines()
    #     return record

    # def write(self, vals):
    #     result = super(AccountWriteOff, self).write(vals)
    #     self._remove_unchecked_lines()
    #     return result

    def unlink(self):
        for rec in self:
            if rec.move_id:
                raise UserError(_('You cannot delete a write-off that has already had a Journal Entry.'))
        return super(AccountWriteOff, self).unlink()

class AccountWriteOffLine(models.Model):
    _name           = 'account.write.off.line'
    _description    = 'Account Write Off Line'
    
    account_write_off_id = fields.Many2one('account.write.off', ondelete="cascade")
    move_id = fields.Many2one('account.move', string='Invoice/Bill')
    move_line_id = fields.Many2one('account.move.line', string='Invoice/Bill Line')
    date = fields.Date('Date', related='move_id.invoice_date')
    due_date = fields.Date('Due Date', related='move_id.invoice_date_due')
    amount_residual = fields.Float(string='Residual Amount')
    write_off = fields.Boolean('Write Off', default=False)
    write_off_amount = fields.Float('Write Off Amount')
    write_off_account_id = fields.Many2one('account.account', string='Write off Account')
    reason = fields.Text('Notes', required=False)

    @api.onchange('write_off')
    def _onchange_(self):
        if self.write_off:
            self.write_off_amount = self.amount_residual
        else:            
            self.write_off_amount = 0