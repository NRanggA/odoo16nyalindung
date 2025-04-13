from odoo import models, fields, api, exceptions


class ReportInfomation(models.Model):
    _name = 'report.information'
    _description = 'Report Information'

    dibuat_oleh = fields.Char('Dibuat Oleh')
    jabatan_pembuat = fields.Char('Jabatan Pembuat')
    disetujui = fields.Char('Disetujui Oleh')
    jabatan_penyetuju = fields.Char('Jabatan Penyetuju')

    @api.model
    def create(self, vals):
        if self.search_count([]) >= 1:
            raise exceptions.UserError("Hanya boleh ada satu data Report Information.")
        return super().create(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    marketing = fields.Char('Marketing')
    phone = fields.Char('Phone')


    @api.depends('marketing')
    def get_marketing(self):
        for record in self:
            if not record.marketing:
                marketing_record = self.search([('marketing', '!=', False)], limit=1)
                return marketing_record.marketing if marketing_record else False
            else:
                return record.marketing
    
    @api.depends('phone')
    def get_phone(self):
        for record in self:
            if not record.phone:
                phone_record = self.search([('phone', '!=', False)], limit=1)
                return phone_record.phone if phone_record else False
            else:
                return record.phone
    
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    dibuat_oleh = fields.Char('Dibuat Oleh', default=lambda self: self._get_default_dibuat_oleh())
    jabatan_pembuat = fields.Char('Jabatan Pembuat', default=lambda self: self._get_default_jabatan_pembuat())
    disetujui = fields.Char('Disetujui Oleh', default=lambda self: self._get_default_disetujui())
    jabatan_penyetuju = fields.Char('Jabatan Penyetuju', default=lambda self: self._get_default_jabatan_penyetuju())

    @api.model
    def _get_default_dibuat_oleh(self):
        info = self.env['report.information'].search([], limit=1, order='id desc')
        return info.dibuat_oleh if info else ''

    @api.model
    def _get_default_jabatan_pembuat(self):
        info = self.env['report.information'].search([], limit=1, order='id desc')
        return info.jabatan_pembuat if info else ''

    @api.model
    def _get_default_disetujui(self):
        info = self.env['report.information'].search([], limit=1, order='id desc')
        return info.disetujui if info else ''

    @api.model
    def _get_default_jabatan_penyetuju(self):
        info = self.env['report.information'].search([], limit=1, order='id desc')
        return info.jabatan_penyetuju if info else ''

    # def get_grouped_taxes(self):
    #     grouped_taxes = {}
    #     for line in self.order_line:
    #         for tax in line.taxes_id:
    #             tax_id = tax.id
    #             tax_amount = line.price_subtotal * (tax.amount / 100)
    #             if tax_id in grouped_taxes:
    #                 grouped_taxes[tax_id]['amount'] += tax_amount
    #             else:
    #                 grouped_taxes[tax_id] = {
    #                     'name': tax.name,
    #                     'amount': tax_amount,
    #                 }
    #     return grouped_taxes

    def get_grouped_taxes(self):
        grouped_taxes = {}
        for line in self.order_line:
            for tax in line.taxes_id:
                tax_id = tax.id
                tax_amount = line.price_subtotal * (tax.amount / 100)
                
                # diubah ke float dan Pembulatan 2 desimal
                tax_amount = round(tax_amount, 2)

                if tax_id in grouped_taxes:
                    grouped_taxes[tax_id]['amount'] += tax_amount
                else:
                    grouped_taxes[tax_id] = {
                        'name': tax.name,
                        'amount': tax_amount,
                    }

        # Bersihkan nilai pajak dari karakter encoding yang tidak diinginkan
        for tax in grouped_taxes.values():
            tax['amount'] = float(tax['amount'])

        return grouped_taxes
