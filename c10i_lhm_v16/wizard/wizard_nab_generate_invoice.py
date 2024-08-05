from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import calendar


class LhmGenNapWizard(models.TransientModel):
    _name           = "lhm.gen.nap.wizard"
    _description    = "Generate NAP Wizard"

    period_id       = fields.Many2one(comodel_name='account.period', string='Account Period', required=True, ondelete="restrict", copy=True)
    date_invoice    = fields.Date(string='Invoice Date', required=True)
    date_from       = fields.Date(string='Dari Tanggal', required=True)
    date_to         = fields.Date(string='SD Tanggal', required=True)
    pks_id          = fields.Many2one(comodel_name="res.partner", string="Nama PKS", ondelete="restrict", required=True)
    product_id      = fields.Many2one('product.template', string='Product', change_default=True, ondelete='restrict', required=True, domain="[('is_nap','=',True)]")
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    
    header_nap_ids  = fields.One2many(comodel_name='lhm.gen.nap.header.wizard', inverse_name='nap_id', string='Header NAP', copy=False)
    line_nap_ids    = fields.One2many(comodel_name='lhm.gen.nap.line.wizard', inverse_name='nap_id', string='Line NAP', copy=False)

    # @api.multi
    def _get_display_price(self, product):
        if not self.pks_id.property_product_pricelist:
            return 0.0
        final_price, rule_id = self.pks_id.property_product_pricelist.get_product_price_rule(self.product_id, 1.0, self.pks_id, date=self._context.get('date_pks'))
        return final_price

    # @api.multi
    def generate_nap(self):
        if self.header_nap_ids:
            for delete in self.header_nap_ids:
                delete.unlink()
        if self.line_nap_ids:
            for delete in self.line_nap_ids:
                delete.unlink()

        date_from   = self.date_from
        date_to     = self.date_to
        pks         = self.pks_id.id
        
        data_nap_draft = self.env['lhm.nap'].search([('pks_id', '=', pks),
                                                  ('date_pks', '>=', date_from),
                                                  ('date_pks', '<=', date_to),
                                                  ('state', '=', 'draft')],  order='name', )
        if data_nap_draft:
            raise UserError(_('Ada beberapa Nota Angkut Buah (NAP) yang berstatus draft diantara tanggal tersebut. \nSilahkan di periksa terlebih dahulu.'))

        data_nap    = self.env['lhm.nap'].search([('pks_id', '=', pks),
                                                  ('date_pks', '>=', date_from),
                                                  ('date_pks', '<=', date_to),
                                                  ('state', '=', 'confirmed')],  order='name', )

        if data_nap:
            # NAP Group By Price
            grouped_lines = {}
            for nap in data_nap:
                nap_price = self.with_context({'date_pks': nap.date_pks})._get_display_price(self.product_id)
                if nap_price not in grouped_lines.keys():
                    grouped_lines.update({nap_price: []})
                grouped_lines[nap_price].append(nap)
            # NAP Header and Detail Creation
            for nap_price, grouped_nap in grouped_lines.items():
                #Insert lhm.gen.nap.header.wizard
                tot_qty = 0
                first_date = min([x.date_pks for x in grouped_nap])
                last_date = max([x.date_pks for x in grouped_nap])
                for nap in grouped_nap:
                    # tot_qty += nap.janjang_jml
                    tot_qty += nap.netto
                values_nap_header = {
                    'date_from': first_date,
                    'date_to': last_date,
                    'qty': tot_qty,
                    'uom_id': self.product_id.uom_id.id,
                    'price': nap_price,
                    'total': tot_qty*nap_price,
                    'nap_id': self.id or False
                }
                new_values_nap_header = self.env['lhm.gen.nap.header.wizard'].create(values_nap_header)

                # Insert lhm.gen.nap.line.wizard
                header_id=new_values_nap_header.id
                
                for nap in grouped_nap:
                    values_nap_line = {
                        'name': nap.name,
                        'date_nap': nap.date_pks,
                        'no_nap': nap.no_nap,
                        'afdeling_id': nap.afdeling_id.id,
                        'vehicle_id': nap.vehicle_id.id,
                        'reg_number': nap.reg_number,
                        'timbang_ksg_kbn': nap.timbang_ksg_kbn,
                        'timbang_isi_kbn': nap.timbang_isi_kbn,
                        'timbang_tara_kbn': nap.timbang_tara_kbn,
                        'janjang_jml': nap.janjang_jml,
                        'pks_id': nap.pks_id.id,
                        'date_pks': nap.date_pks,
                        'timbang_isi_pks': nap.timbang_isi_pks,
                        'timbang_ksg_pks': nap.timbang_ksg_pks,
                        'timbang_tara_pks': nap.timbang_tara_pks,
                        'grading': nap.grading,
                        'netto': nap.netto,
                        'nap_id': self.id or False,
                        'header_id': header_id,
                        'src_nap_id': nap.id,
                    }
                    new_values_nap_line = self.env['lhm.gen.nap.line.wizard'].create(values_nap_line)
        return False

    # @api.multi
    def process_nap(self):
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']

        journal_id = Invoice.default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': '',
            'type': 'out_invoice',
            'date_invoice': self.date_invoice,
            # 'force_period_id': self.period_id.id,
            'reference': 'NAP %s'%(datetime.strptime(self.date_invoice, '%Y-%m-%d').strftime('%d/%m/%Y')),
            'account_id': self.pks_id.property_account_receivable_id.id,
            'partner_id': self.pks_id.id,
            'partner_shipping_id': self.pks_id.id,
            'journal_id': journal_id,
            'currency_id': self.pks_id.property_product_pricelist and \
                self.pks_id.property_product_pricelist.currency_id.id or self.company_id.currency_id.id,
            'company_id': self.company_id.id,
        }
        invoice = Invoice.create(invoice_vals)
        for line in self.header_nap_ids:
            account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
            if not account:
                raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                    (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))
            date_start = datetime.strptime(line.date_from, '%Y-%m-%d').strftime('%d %B %Y')
            date_end = datetime.strptime(line.date_to, '%Y-%m-%d').strftime('%d %B %Y')
            invoice_line_vals = {
                'invoice_id': invoice.id,
                'name': "Penjualan %s %s - %s"%(self.product_id.name, date_start, date_end),
                'product_id': self.product_id.id,
                'price_unit': line.price,
                'uom_id': line.uom_id.id,
                'quantity': line.qty,
                'account_id': account.id,
            }
            invoice_line_id = InvoiceLine.create(invoice_line_vals)
        

        if not invoice.invoice_line_ids:
            raise UserError(_('There is no invoicable line.'))
        # If invoice is negative, do a refund invoice instead
        if invoice.amount_untaxed < 0:
            invoice.type = 'out_refund'
            for line in invoice.invoice_line_ids:
                line.quantity = -line.quantity
        # Use additional field helper function (for account extensions)
        for line in invoice.invoice_line_ids:
            line._set_additional_fields(invoice)
        # Necessary to force computation of taxes. In account_invoice, they are triggered
        # by onchanges, which are not triggered when doing a create.
        invoice.compute_taxes()
        invoice.message_post('This invoice has been created from \
            Generate Invoice NAP and consist of NAP : %s'%",".join([x.src_nap_id.name for x in self.line_nap_ids]))

        # Update all related NAP
        for nap in self.line_nap_ids:
            nap.src_nap_id.sudo().write({'invoice_id': invoice.id})
        
        # Redirect to show Invoice
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['res_id'] = invoice.id
        return action


class LhmGenNapHeaderWizard(models.TransientModel):
    _name           = "lhm.gen.nap.header.wizard"
    _description    = "Generate NAP Header Wizard"

    date_from       = fields.Date(string='Dari Tanggal', required=True)
    date_to         = fields.Date(string='SD Tanggal', required=True)
    qty             = fields.Float('Jumlah Barang', required=True)
    uom_id          = fields.Many2one(comodel_name="uom.uom", string="Satuan", ondelete="restrict", required=False)
    price           = fields.Float('Harga Satuan', required=False)
    total           = fields.Float('Jumlah Harga', required=False)
    
    nap_id          = fields.Many2one(comodel_name='lhm.gen.nap.wizard', string='Main NAP', required=True, ondelete="cascade", copy=False)
    line_nap_ids2   = fields.One2many(comodel_name='lhm.gen.nap.line.wizard', inverse_name='header_id', string='Line NAP', copy=False)


class LhmGenNapLineWizard(models.TransientModel):
    _name            = 'lhm.gen.nap.line.wizard'
    _description     = 'Generate NAP Line'

    name             = fields.Char('No. Register', required=False)
    date_nap         = fields.Date("Tanggal PKS")
    no_nap           = fields.Char('No. NAP')
    afdeling_id      = fields.Many2one(comodel_name="res.afdeling", string="Afdeling", ondelete="restrict")
    vehicle_id       = fields.Many2one(comodel_name="lhm.utility", string="Kendaraan", ondelete="restrict", domain="[('type','=', 'vh')]")
    reg_number       = fields.Char('Nomor Polisi', readonly=True, related="vehicle_id.reg_number", store=True)

    timbang_ksg_kbn  = fields.Float('Timb. Kosong-KBN ')
    timbang_isi_kbn  = fields.Float('Timb. Isi-KBN ')
    timbang_tara_kbn = fields.Float('Timb. Tara-KBN ', readonly=True,)
    janjang_jml      = fields.Float('Jml Janjang', readonly=True,)

    pks_id           = fields.Many2one(comodel_name="res.partner", string="Nama PKS", ondelete="restrict")
    date_pks         = fields.Date("Tanggal PKS")
    timbang_isi_pks  = fields.Float('Timb. Isi-PKS')
    timbang_ksg_pks  = fields.Float('Timb. Kosong-PKS')
    timbang_tara_pks = fields.Float('Timb. Tara-PKS', readonly=True,)
    grading          = fields.Float('Grading')
    netto            = fields.Float('Netto', readonly=True,)

    nap_id          = fields.Many2one(comodel_name='lhm.gen.nap.wizard', string='Main NAP', required=True, ondelete="cascade", copy=False)
    header_id       = fields.Many2one(comodel_name='lhm.gen.nap.header.wizard', string='Header NAP', required=True, ondelete="cascade", copy=False)
    src_nap_id      = fields.Many2one(comodel_name='lhm.nap', string='Source NAP', required=True, ondelete="cascade", copy=False)




