from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

class PlantBlock(models.Model):
    _inherit = 'lhm.plant.block'

    type_of_plant = fields.Selection([
        ('longterm_tbm_tm', "Tanaman Jangka Panjang dengan konsep Panen Bulanan"),
        ('longterm_seasonal', "Tanaman Jangka Panjang dengan Masa Panen Seasonal"),
        ('shorterm', "Tanaman dengan Waktu Panen yang Singkat")
    ])
    # Untuk tanaman yang ditanam diawal, kemudian panen bulanan
    # Pada saat fase Tanaman Belum Menghasilkan (TBM), semua COST akan dilempar ke akun TBM
    # Pada saat fase Tanaman Menghasilkan (TM), semua COST akan dilempar ke akun BIAYA di MASING-MASING AKTIFITAS
    tbm_account_id = fields.Many2one('account.account', string='TBM Inti Account', help='Akun Harga Penyerahan TBM saat fase Tanaman Belum Menghasilkan')
    plasma_account_id = fields.Many2one('account.account', string='Plasma Account', help='Akun Piutang Asosiasi saat fase Tanaman Menghasilkan')
    # Untuk tanaman yang ditanam diawal, kemudian panen seasonal
    # Pada saat fase Tanaman Belum Menghasilkan (TBM), semua COST akan dilempar ke akun TBM
    # Pada saat fase Tanaman Menghasilkan (TM) tetapi BELUM Season Panen, COST akan disimpan di DEFERED ACCOUNT
    #                   Kemudian saat MASUK Season Panen semua COST akan dilempar ke akun BIAYA di MASING-MASING AKTIFITAS
    # Untuk tanaman jangka pendek
    deferred_account_id = fields.Many2one('account.account', string='Deferred Account', help='Usually used for TBM')