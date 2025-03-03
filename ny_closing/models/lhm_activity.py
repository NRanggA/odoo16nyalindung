from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class Activity(models.Model):
    _name = 'lhm.activity.closing.account'
    _description = 'Closing Account dari Aktifitas'

    activity_id = fields.Many2one('lhm.activity', 'Aktivitas', ondelete='restrict')
    src_journal_id = fields.Many2one('account.journal', 'Source Journal', required=True)
    account_id = fields.Many2one('account.account', 'Cost Account', required=True)

class Activity(models.Model):
    _inherit = 'lhm.activity'

    # Hanya digunakan saat proses Closing Akhir Plantation
    # Untuk tanaman yang ditanam diawal, kemudian panen bulanan
    # Pada saat fase Tanaman Belum Menghasilkan (TBM), semua COST akan dilempar ke akun TBM yg ada di lhm.plant.block
    # Pada saat fase Tanaman Menghasilkan (TM), semua COST akan dilempar ke akun BIAYA di MASING-MASING AKTIFITAS (tm_cost_account_id)
    # Untuk tanaman yang ditanam diawal, kemudian panen seasonal
    # Pada saat fase Tanaman Belum Menghasilkan (TBM), semua COST akan dilempar ke akun TBM yg ada di lhm.plant.block
    # Pada saat fase Tanaman Menghasilkan (TM) tetapi BELUM Season Panen, COST akan disimpan di DEFERED ACCOUNT yg ada di lhm.plant.block
    #                   Kemudian saat MASUK Season Panen semua COST akan dilempar ke akun BIAYA di MASING-MASING AKTIFITAS
    # Untuk tanaman jangka pendek
    cost_account_id = fields.Many2one('account.account', string='Default Plantation Cost Account', help='Akun Biaya Perkebunan yang digunakan saat proses Alokasi Biaya di Akhir (Closing)')
    cost_account_ids = fields.One2many('lhm.activity.closing.account', 'activity_id', string='Mapping Plantation Cost Account')

    def get_plantation_cost_account(self, src_journal):
        self.ensure_one()
        accounts = self.env['lhm.activity.closing.account'].search_read(domain=[('activity_id','=',self.id),
                                                                ('src_journal_id','=',src_journal.id)], 
                                                                fields=['account_id'],
                                                                limit=1)
        if accounts:
            return accounts[0]['account_id'][0]
        elif self.cost_account_id:
            return self.cost_account_id.id
        else:
            raise ValidationError(f"Belum ada default Plantation Cost Account pada aktifitas ({self.code}) {self.name}.")