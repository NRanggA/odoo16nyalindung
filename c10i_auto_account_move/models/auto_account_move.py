from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class AutoAccountMove(models.Model):
    _name = 'auto.account.move'
    _description = 'Auto Create Account Move'

    name = fields.Char('Name', required=True, help='Masukkan nama partner untuk dokumen ini')
    generate_interval = fields.Selection([
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string='Generate Interval', required=True)
    interval_number = fields.Integer('Interval Number', default=1, help="Total berapa kali vendor bill akan di-generate", required=True)
    after_generate_interval = fields.Integer('After Generate Interval', default=0, help="Jumlah vendor bill yang sudah digenerate")
    move_id = fields.Many2one('account.move', string='Account Move', required=True)
    last_generated = fields.Date('Last Generated')
    type = fields.Selection([
        ('in_invoice', 'Vendor Bill'),
        ('out_invoice', 'Customer Invoice'),
        ('entry', 'Journal Entry'),
    ], string='Type', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Progress'),
        ('done', 'Done'),
    ], string='state', default='draft')

    @api.onchange('move_id')
    def _onchange_move_id(self):
        if self.move_id:
            self.type = self.move_id.move_type

    @api.model
    def generate_auto_account_move(self):
        # today = fields.Date.today()
        date_string = "2025-02-26"
        today = datetime.strptime(date_string, "%Y-%m-%d").date()
        records = self.search([])

        for record in records:
            move = record.move_id
            generate = False


            if record.after_generate_interval >= record.interval_number:
                record.write({'state': 'done'})
                continue  

            # Untuk mengecek kapan terakhir kali di generate
            # last_date = record.last_generated or today - relativedelta(years=10)

            if record.generate_interval == 'monthly' and record.last_generated:
                generate = today >= (record.last_generated + relativedelta(months=1))
            elif record.generate_interval == 'yearly' and record.last_generated:
                generate = today >= (record.last_generated + relativedelta(years=1))
            elif not record.last_generated:
                generate = True

            if generate and move.state == 'posted':
                default = {
                    'date': today,
                    'invoice_date': today if move.move_type == 'in_invoice' else False,
                    'state': 'draft'
                }
                move.copy(default)


                record.write({
                    'last_generated': today,
                    'after_generate_interval': record.after_generate_interval + 1
                })

        return True

    @api.model
    def create(self, vals):
        """ Saat record dibuat, langsung ubah state menjadi 'progress' """
        vals['state'] = 'process'
        return super(AutoAccountMove, self).create(vals)
