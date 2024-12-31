from odoo import models, fields, api, _
from datetime import datetime



class AccountJournal(models.Model):
    _inherit = 'account.journal'


    sequence_id = fields.Many2one('ir.sequence', string='Reference Sequence IN')   
    sequence_out_id = fields.Many2one('ir.sequence', string='Reference Sequence OUT')

    def create_sequence(self):
        for journal in self:
            if journal.type == 'bank':
                if journal.code and not journal.sequence_id:
                    sequence_in = self.env['ir.sequence'].create({
                        'name': f"Sequence Bank Masuk {journal.code}",
                        'code': f"account.journal.in.{journal.code}",
                        'prefix': f"BM {journal.code} ",
                        'padding': 4, 
                        'suffix': "/%(month)s/%(year)s",
                        # 'use_date_range': True,
                        'company_id': journal.company_id.id
                    })
                    sequence_out = self.env['ir.sequence'].create({
                        'name': f"Sequence Bank Keluar {journal.code}",
                        'code': f"account.journal.out.{journal.code}",
                        'prefix': f"BK {journal.code} ",
                        'padding': 4,
                        'suffix': "/%(month)s/%(year)s",
                        # 'use_date_range': True,
                        'company_id': journal.company_id.id
                    })
            if journal.type == 'cash':
                if journal.code and not journal.sequence_id:
                    sequence_in = self.env['ir.sequence'].create({
                        'name': f"Sequence Kas Masuk {journal.code}",
                        'code': f"account.journal.in.{journal.code}",
                        'prefix': f"KM {journal.code} ",
                        'suffix': "/%(month)s/%(year)s",
                        'padding': 4, 
                        'company_id': journal.company_id.id
                    })
                    sequence_out = self.env['ir.sequence'].create({
                        'name': f"Sequence Kas Keluar {journal.code}",
                        'code': f"account.journal.out.{journal.code}",
                        'prefix': f"KK {journal.code} ",
                        'suffix': "/%(month)s/%(year)s",
                        'padding': 4,
                        'company_id': journal.company_id.id
                    })


            journal.sequence_id = sequence_in.id
            journal.sequence_out_id = sequence_out.id

    @api.model
    def create(self, vals_list):
        journals = super(AccountJournal, self).create(vals_list)
        for journal in journals:
            journal.create_sequence()
        return journals
    
    def write(self, vals):
        res = super(AccountJournal, self).write(vals)
        if vals.get('code'):
            self.create_sequence()
        return res