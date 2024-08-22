from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_id_tax_number = fields.Char(string="Tax Number", copy=False)

    @api.constrains('l10n_id_tax_number')
    def validation_check_nomor_faktur(self):
        for record in self:
            if record.partner_id and record.l10n_id_tax_number:
                this_nomor_faktur = record.l10n_id_tax_number[3:]
                partner_nomor_faktur = self.env['prepopulated.data'].search([('npwp','=',record.partner_id.vat),('nomor_faktur', '=', this_nomor_faktur)])
                if not partner_nomor_faktur:
                    raise ValidationError("Please Input This Tax Number for this partner in Master Data Prepopulated Data")