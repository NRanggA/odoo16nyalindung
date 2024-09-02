from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_state = fields.Selection(
        selection_add=[
            ('written_off', 'Dihapus'), 
        ]
    )

class AccountWriteOff(models.Model):
    _name        = 'account.write.off'
    _description = 'Account Write Off'

    name                    = fields.Char('Name')
    date                    = fields.Date('Document Date', required=True)
    customer_id             = fields.Many2one('res.partner', string='Customer', required=True, ondelete="restrict")
    company_id              = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    state                   = fields.Selection([
                                ('draft', 'Draft'),
                                ('approve', 'Approve'),
                            ], string='Status', default='draft')

    line_ids                = fields.One2many('account.write.off.line', 'account_write_off_id', string="Detail Write Off")
    account_write_off       = fields.Many2one(
                                comodel_name='account.account',
                                related='company_id.account_write_off', readonly=False,
                                string="Account Write Off")
    
    write_off_default_journal_id = fields.Many2one(
                                comodel_name='account.journal',
                                related='company_id.write_off_default_journal_id', readonly=False,
                                string="Journal")
    
    # Field to store journal entry
    journal_entry_id        = fields.Many2one('account.move', string='Journal Entry', readonly=True)

    def button_approve(self):
        self._account_move_entry()
    
    def _account_move_entry(self):
        AccountMove = self.env['account.move']
        
        for record in self:
            # Memastikan akun write-off sudah terisi
            acc_src = record.account_write_off
            if not acc_src:
                raise ValidationError(_('Akun pada Setting Account Write Off Belum diisi.\n'
                                        'Silahkan isi akun tersebut terlebih dahulu'))

            journal_id = record.write_off_default_journal_id
            if not journal_id:
                raise ValidationError(_('Journal pada Setting Account Write Off Belum diisi.\n'
                                        'Silahkan isi Journal tersebut terlebih dahulu'))
            # Inisialisasi total untuk entri jurnal
            total_lines = 0.0
            
            # Persiapkan baris-baris entri jurnal
            move_lines = []

            for line in record.line_ids:
                # Dapatkan akun piutang customer untuk sisi kredit
                credit_account = line.invoice_id.partner_id.property_account_receivable_id
                if not credit_account:
                    raise ValidationError(_('Akun piutang untuk customer belum diisi.\n'
                                            'Silahkan isi akun tersebut terlebih dahulu'))
                
                line_name = f"{line.invoice_id.name or 'Invoice'} - {line.invoice_id.invoice_date or 'Tanggal'} - {line.invoice_id.partner_id.name or 'Customer'}"
                # debit
                move_lines.append((0, 0, {
                    'account_id': acc_src.id,
                    'name'      : line_name,
                    'debit'     : line.total_value,
                    'credit'    : 0.0,
                    'partner_id': record.customer_id.id,
                }))
                # Hitung total baris untuk validasi
                total_lines += line.total_value

                # mengubah payment_state pada invoice 
                line.invoice_id.payment_state = 'written_off'

            # kredit
            move_lines.append((0, 0, {
                'account_id': credit_account.id,
                'name'      : line_name,
                'debit'     : 0.0,
                'credit'    : total_lines,
                'partner_id': record.customer_id.id,
            }))

            # header jurnal (account.move)
            move_vals = {
                'date'      : record.date,
                'journal_id': journal_id.id, # diambil dari setting accounting->write off
                # 'journal_id': record.line_ids[0].invoice_id.journal_id.id,
                'line_ids'  : move_lines,
            }
            
            move = AccountMove.create(move_vals)
            self.state = 'approve'
            
            # Hubungkan entri jurnal dengan catatan write-off
            record.journal_entry_id = move.id

            # # Posting entri jurnal untuk mengonfirmasi
            move.action_post()


    def button_draft(self):
        self.state = 'draft'
        for line in self.line_ids:
            line.invoice_id.payment_state = 'not_paid'


    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        # Cari invoice yang statusnya not_paid dan partial
        invoices = self.env['account.move'].search([
            ('partner_id', '=', self.customer_id.id),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ])

        line_data = []

        for inv in invoices:
            line_data.append((0, 0, {
                'date': inv.invoice_date,  
                'invoice_id': inv.id,
                'invoice_no': inv.name,
                'total_value': inv.amount_total,
                'write_off': False,  
                'reason': '',
            }))
        self.line_ids = line_data

    # Fungsi untuk menghapus data write off line yang nilai boolean nya bernilai false
    def _remove_unchecked_lines(self):
        lines_to_remove = self.line_ids.filtered(lambda line: not line.write_off)
        if lines_to_remove:
            lines_to_remove.unlink()

    def action_view_journal_entry(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if self.journal_entry_id:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.journal_entry_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            current_year = datetime.now().year
            sequence_code = f"WO/{current_year}/"
            vals['name'] = self.env['ir.sequence'].next_by_code('account.write.off') or f"{sequence_code}001"

        record = super(AccountWriteOff, self).create(vals)
        record._remove_unchecked_lines()
        return record

    def write(self, vals):
        result = super(AccountWriteOff, self).write(vals)
        self._remove_unchecked_lines()
        return result

class AccountWriteOffLine(models.Model):
    _name           = 'account.write.off.line'
    _description    = 'Account Write Off Line'
    
    date                 = fields.Date('Tanggal')
    invoice_id           = fields.Many2one('account.move', string='Invoice')
    account_write_off_id = fields.Many2one('account.write.off', ondelete="cascade")
    invoice_no           = fields.Char('Nomor Invoice')
    total_value          = fields.Float('Total Value')
    write_off            = fields.Boolean('Write Off', default=False)
    reason               = fields.Text('Keterangan')