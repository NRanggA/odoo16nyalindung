from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import calendar


class LhmContractorBill(models.TransientModel):
    _name           = "lhm.contractor.bill.wizard"
    _description    = "Contractor Bill Wizard"

    contractor_id       = fields.Many2one("res.partner", "Kontraktor", ondelete="restrict", required=True)
    date_invoice        = fields.Date('Invoice Date', required=True)
    # start_period_id     = fields.Many2one('account.period', 'Account Period', required=True, ondelete="restrict", copy=True)
    contractor_vehicle  = fields.Boolean(string="Vehicle")
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)

    lhm_contractor_ids  = fields.Many2many('lhm.contractor', string='LHM Contractor')
    
    invoice_lines       = fields.One2many('lhm.contractor.summary', 'wizard_id', string='Summary', copy=False)
    line_ids            = fields.Many2many('lhm.contractor.line', string='Detail Kontraktor', readonly=True)
    line_vehicle_ids    = fields.Many2many('lhm.contractor.vehicle.line', string='Detail Kontraktor Alat', readonly=True)
    has_npwp            = fields.Boolean(compute='_get_npwp', string='Ada NPWP?')
    taxes_id            = fields.Many2many('account.tax', string='Tax')

    account_payable_contractor_id = fields.Many2one(
                                comodel_name='account.account',
                                related='company_id.account_payable_contractor_id', readonly=False,
                                string="Account Payable Perantara Buku Kontraktor")
    
    # @api.multi
    @api.depends('contractor_id')
    def _get_npwp(self):
        result = []
        for wizard in self:
            self.has_npwp = True
            # self.has_npwp = wizard.contractor_id.has_npwp
            # print("Error field has.npwp tidak ditemukan di model res.partner")

    def generate_line(self):
        if self.contractor_vehicle:
            if self.line_vehicle_ids:
                self.line_vehicle_ids = [(5, None, None)]
        else:
            if self.line_ids:
                self.line_ids = [(5, None, None)]
        if self.invoice_lines:
            for line in self.invoice_lines:
                line.unlink()

        # date_from   = self.start_period_id.date_start
        # date_to     = self.start_period_id.date_stop


        if self.lhm_contractor_ids:
            buku_kontraktor_datas = self.lhm_contractor_ids
        else:
            buku_kontraktor_datas = self.env['lhm.contractor'].search([
                                                # ('date_start', '>=', date_from),
                                                # ('date_end', '<=', date_to), ('invoice_id','=',False),
                                                ('supplier_id', '=', self.contractor_id.id), 
                                                ('invoice_id', '=', False), 
                                                ('state', '=', 'confirmed')],  order='name', )
        to_write = {}
        if buku_kontraktor_datas:
            grouped_lines = {}
            bk_line_ids = []
            bk_line_vehicle_ids = []
            for buku_kontraktor in buku_kontraktor_datas:
                if self.contractor_vehicle:
                    for y in buku_kontraktor.line_vehicle_ids:
                        bk_line_vehicle_ids.append(y.id)

                    for line in buku_kontraktor.line_vehicle_ids:
                        # if line.tidak_ditagihkan:
                        #     continue
                        key = (line.location_type_id, line.location_id, line.activity_id)
                        if key not in grouped_lines.keys():
                            grouped_lines.update({key: {
                                'location_type_id'  : line.location_type_id and line.location_type_id.id or False,
                                'varieties_id'       : line.varieties_id and line.varieties_id.id or False,
                                'location_id'       : line.location_id and line.location_id.id or False,
                                'activity_id'       : line.activity_id and line.activity_id.id or False,
                                'amount'            : 0.0,
                                'wizard_id'         : self.id,
                            }})
                        grouped_lines[key]['amount'] += line.total
                        to_write.update({'line_vehicle_ids': list(map(lambda x: (4, x), bk_line_vehicle_ids))})
                else:
                    for x in buku_kontraktor.line_ids:
                        bk_line_ids.append(x.id)

                    for line in buku_kontraktor.line_ids:
                        key = (line.location_type_id, line.location_id, line.activity_id)
                        if key not in grouped_lines.keys():
                            grouped_lines.update({key: {
                                'location_type_id'  : line.location_type_id and line.location_type_id.id or False,
                                'varieties_id'       : line.varieties_id and line.varieties_id.id or False,
                                'location_id'       : line.location_id and line.location_id.id or False,
                                'activity_id'       : line.activity_id and line.activity_id.id or False,
                                'amount'            : 0.0,
                                'wizard_id'         : self.id,
                                }})
                        grouped_lines[key]['amount'] += line.total
                        to_write.update({'line_ids': list(map(lambda x: (4,x), bk_line_ids))})

            for vals in grouped_lines.values():
                self.env['lhm.contractor.summary'].create(vals)
            self.write(to_write)
        return True

    # @api.multi
    def process(self):
        Invoice = self.env['account.move']
        InvoiceLine = self.env['account.move.line']
        if self.line_vehicle_ids:
            contractor_datas = list(set([x.contractor_id for x in self.line_vehicle_ids]))
        else:
            contractor_datas = list(set([x.contractor_id for x in self.line_ids]))

        for contractor in contractor_datas:
            if contractor.invoice_id:
                raise UserError(_('Buku Kontraktor ini sudah memiliki Vendor Bill'))

        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        if not journal_id:
            raise UserError(_('Please define an accounting purchase journal for this company.'))
        
        line_to_add = []
        # for line in self.invoice_lines:
            # default_loc_type = self.env['lhm.location.type'].search([('name', '=', '-')])
            # PUNYA LAMA 
            # line_to_add.append((0,0,{
            #     'name'                          : "Jasa Kontraktor: %s"%(line.activity_id.name),
            #     'plantation_location_type_id'   : line.location_type_id.id if line.location_type_id else False,
            #     'plantation_varieties_id'       : line.varieties_id.id if line.varieties_id else False,
            #     'plantation_location_id'        : line.location_id.id if line.location_id else False,
            #     'plantation_activity_id'        : line.activity_id.id if line.activity_id else False,
            #     'account_id'                    : self.account_payable_contractor_id.id,
            #     'product_id'                    : False,
            #     'product_uom_id'                : False,
            #     'quantity'                      : 1,
            #     'price_unit'                    : line.amount,
            #     'tax_ids'                       : [(6,0,[x.id for x in self.taxes_id])],
            # }))

        total_amount = sum(line.amount for line in self.invoice_lines)
        tipe_lokasi = self.env['lhm.location.type'].search([('code', '=', '-')], limit=1)

        # TERBARU
        line_to_add.append((0,0,{
            'name'                          : "Jasa Kontraktor: %s"%(self.contractor_id.name),
            'plantation_location_type_id'   : tipe_lokasi.id,
            'plantation_varieties_id'       : '',
            'plantation_location_id'        : '',
            'plantation_activity_id'        : '',
            'account_id'                    : self.account_payable_contractor_id.id,
            'product_id'                    : False,
            'product_uom_id'                : False,
            'quantity'                      : 1,
            'price_unit'                    : total_amount,
            'tax_ids'                       : [(6,0,[x.id for x in self.taxes_id])],
        }))
        
        invoice_vals = {
            'name'                  : '',
            'move_type'             : 'in_invoice',
            'invoice_date'          : self.date_invoice,
            'partner_id'            : self.contractor_id.id,
            'partner_shipping_id'   : self.contractor_id.id,
            'journal_id'            : journal_id.id,
            'currency_id'           : self.company_id.currency_id.id,
            'company_id'            : self.company_id.id,
            'invoice_line_ids'      : line_to_add
        }

        invoice = Invoice.create(invoice_vals)

        if not invoice.invoice_line_ids:
            raise UserError(_('There is no invoicable line.'))
        # If invoice is negative, do a refund invoice instead
        if invoice.amount_untaxed < 0:
            invoice.move_type  = 'in_refund'
            for line in invoice.invoice_line_ids:
                line.quantity = -line.quantity

        invoice.message_post(body=_('This invoice has been created from Buku Kontraktor'))

        # Update all related Buku Kontraktor
        for contractor in contractor_datas:
            contractor.write({'invoice_id': invoice.id})

        # Redirect to show Invoice
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = invoice.id
        return action


class LhmContractorSummary(models.TransientModel):
    _name           = "lhm.contractor.summary"
    _description    = "Rangkuman Buku Kontraktor"

    wizard_id           = fields.Many2one('lhm.contractor.bill.wizard', 'Wizard', required=True, ondelete="cascade", copy=False)
    location_type_id    = fields.Many2one("lhm.location.type", "Tipe", ondelete="restrict")
    varieties_id        = fields.Many2one('plant.varieties', string="ORG", ondelete='restrict')
    location_id         = fields.Many2one("lhm.location", "Lokasi", ondelete="restrict")
    activity_id         = fields.Many2one("lhm.activity", "Aktivitas", ondelete="restrict")
    amount              = fields.Float('Nilai')