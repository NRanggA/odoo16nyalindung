from odoo import models, fields, api

class AccountMoveCustomReport(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_customer_invoice_data(self):
        invoices = self.search([
            ('move_type', '=', 'out_invoice'),
            ('l10n_id_tax_number', '!=', False)
        ], ['l10n_id_tax_number', 'name', 'partner_id'])

        invoice_data = []
        for invoice in invoices:
            invoice_data.append({
                'l10n_id_tax_number': invoice.l10n_id_tax_number,
                'invoice_name': invoice.name,
                'partner_name': invoice.partner_id.name,
            })

        return invoice_data


class EFakturList(models.TransientModel):
    _name = 'e.faktur.list'
    _description = 'e-Faktur List'

    l10n_id_tax_number = fields.Char(string="Tax Number")
    invoice_name = fields.Char(string="Invoice Name")
    partner_name = fields.Char(string="Customer Name")

    @api.model
    def default_get(self, fields):
        res = super(EFakturList, self).default_get(fields)
        invoices = self.env['account.move'].get_customer_invoice_data()

        faktur_list = []
        for invoice in invoices:
            faktur_list.append((0, 0, {
                'l10n_id_tax_number': invoice['l10n_id_tax_number'],
                'invoice_name': invoice['invoice_name'],
                'partner_name': invoice['partner_name'],
            }))

        res.update({'faktur_list_ids': faktur_list})
        return res
