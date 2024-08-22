from odoo import models, fields, api
from odoo.exceptions import ValidationError
import binascii


class PrepopulatedData(models.Model):
    _name = 'prepopulated.data'
    _description = 'Prepopulated Data'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Name')
    npwp = fields.Char('NPWP')
    jenis_transaksi = fields.Integer('Jenis Transaksi')
    status_pengganti = fields.Integer('Status Pengganti')    
    nomor_faktur = fields.Char('Nomor Faktur')
    tanggal_faktur = fields.Date('Tanggal Faktur')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda s: s.env.company.currency_id.id, required=True, ondelete='restrict')
    dpp = fields.Monetary('DPP')
    ppn = fields.Monetary('PPN')
    ppnbm = fields.Monetary('PPnBM')
    is_dikreditkan = fields.Selection([
        ('Ya', 'Ya'),
        ('Tidak', 'Tidak'),
    ], string='Dikreditkan', default='ya')

    def import_data(self):
        action = self.env["ir.actions.actions"]._for_xml_id('nyalindung_prepopulated_data.action_wizard_import_prepopulated_data')
        return action