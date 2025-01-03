from odoo import models, fields, api


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


    dibuat_oleh = fields.Char('Dibuat Oleh', default="Wahyu Widianto")
    jabatan_pembuat = fields.Char('Jabatan Pembuat', default="Manager Plantation")
    disetujui = fields.Char('Disetujui Oleh', default="Irwan G Subrata")
    jabatan_penyetuju = fields.Char('Jabatan Penyetuju', default="Direktur")

    @api.depends('dibuat_oleh')
    def get_dibuat_oleh(self):
        for record in self:
            if not record.dibuat_oleh:
                dibuat_oleh_record = self.search([('dibuat_oleh', '!=', False)], limit=1)
                return dibuat_oleh_record.dibuat_oleh if dibuat_oleh_record else False
            else:
                return record.dibuat_oleh
    
    @api.depends('jabatan_pembuat')
    def get_jabatan_pembuat(self):
        for record in self:
            if not record.jabatan_pembuat:
                jabatan_pembuat_record = self.search([('jabatan_pembuat', '!=', False)], limit=1)
                return jabatan_pembuat_record.jabatan_pembuat if jabatan_pembuat_record else False
            else:
                return record.jabatan_pembuat
            
    @api.depends('disetujui')
    def get_disetujui(self):
        for record in self:
            if not record.disetujui:
                disetujui_record = self.search([('disetujui', '!=', False)], limit=1)
                return disetujui_record.disetujui if disetujui_record else False
            else:
                return record.disetujui
    
    @api.depends('jabatan_penyetuju')
    def get_jabatan_penyetuju(self):
        for record in self:
            if not record.jabatan_penyetuju:
                jabatan_penyetuju_record = self.search([('jabatan_penyetuju', '!=', False)], limit=1)
                return jabatan_penyetuju_record.jabatan_penyetuju if jabatan_penyetuju_record else False
            else:
                return record.jabatan_penyetuju

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
