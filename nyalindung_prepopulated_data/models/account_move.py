from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_id_tax_number = fields.Char(string="Tax Number", copy=False, store=True)

    def validation_check_nomor_faktur(self):
        for record in self:
            if record.move_type == 'out_invoice':
                continue
            # print(">>>>>>>>>>>>>>>>>>", record.partner_id)
            # print(">>>>>>>>>>>>>>>>>>", record.l10n_id_tax_number)
            # print(">>>>>>>>>>>>>>>>>>", stop)
            if record.partner_id and record.l10n_id_tax_number:
                this_nomor_faktur = record.l10n_id_tax_number[3:]
                partner_nomor_faktur = self.env['prepopulated.data'].search([('npwp','like',record.partner_id.vat[2:]),('nomor_faktur','=',this_nomor_faktur)])
                print(">>>>>>>>>>>>>>>>>>", partner_nomor_faktur)         
                print(">>>>>>>>>>>>>>>>>>", this_nomor_faktur)         
                if partner_nomor_faktur:
                    jenis_transaksi = record.l10n_id_tax_number[1]
                    status_pengganti = record.l10n_id_tax_number[2]
                    kode_transaksi = self.env['prepopulated.data'].search([('jenis_transaksi','=',jenis_transaksi),('status_pengganti','=',status_pengganti)])
                    if not kode_transaksi:
                        raise ValidationError('Please check Jenis Transaksi and Status Pengganti code')
                else:
                    raise ValidationError("Please Input This Tax Number for this partner in Master Data Prepopulated Data")
                

    @api.model
    def create(self, vals):
        record = super(AccountMove, self).create(vals)
        record.validation_check_nomor_faktur()
        return record

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        self.validation_check_nomor_faktur()
        return res