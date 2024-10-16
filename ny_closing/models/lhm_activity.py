from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

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
    cost_account_id = fields.Many2one('account.account', string='Plantation Cost Account', help='Akun Biaya Perkebunan yang digunakan saat proses Alokasi Biaya di Akhir (Closing)')
    