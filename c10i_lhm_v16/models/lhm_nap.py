from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from datetime import datetime


class lhm_nap(models.Model):
    _name           = 'lhm.nap'
    _description    = 'Nota Angkut Panen'

    @api.depends('timbang_ksg_kbn', 'timbang_isi_kbn', 'timbang_isi_pks', 'timbang_ksg_pks', 'grading')
    def _compute_timbang(self):
        self.timbang_tara_kbn = self.timbang_isi_kbn - self.timbang_ksg_kbn
        self.timbang_tara_pks = self.timbang_isi_pks - self.timbang_ksg_pks
        self.netto = self.timbang_isi_pks - self.timbang_ksg_pks - self.grading

    @api.depends('line_ids')
    def _compute_janjang(self):
        if self.line_ids:
            total_janjang = 0
            for line_nap in self.line_ids:
                total_janjang = total_janjang + line_nap.qty_nap
            self.janjang_jml = total_janjang

    @api.depends('date_nap', 'state')
    def _compute_account_period_id(self):
        for plantation_nap in self:
            if plantation_nap.date_nap:
                period_id = self.env['account.period'].search([('date_start', '<=', plantation_nap.date_nap), ('date_stop', '>=', plantation_nap.date_nap), ('special', '=', False)])
                if period_id:
                    plantation_nap.account_period_id = period_id

    name                = fields.Char('No. Register', required=False)
    date_nap            = fields.Date("Tanggal", readonly=True, states={'draft': [('readonly',False)]})
    account_period_id   = fields.Many2one("account.period", string="Accounting Periode", ondelete="restrict", compute='_compute_account_period_id', store=True)
    date_start          = fields.Date(related="account_period_id.date_start", string="Range Start Date", readonly=1)
    date_stop           = fields.Date(related="account_period_id.date_stop", string="Range End Date", readonly=1)
    no_nap              = fields.Char('No. NAP Manual', readonly=True, states={'draft': [('readonly',False)]})
    afdeling_id         = fields.Many2one("res.afdeling", string="Afdeling", ondelete="restrict", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    driver              = fields.Char('Nama Supir', readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    vehicle_id          = fields.Many2one("lhm.utility", string="Kendaraan", ondelete="restrict", domain="[('type','=', 'vh')]", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    vehicle_subtitute_id= fields.Many2one("lhm.utility", "Kendaraan Pengganti", ondelete="restrict", domain="[('type','=', 'vh')]", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    reg_number          = fields.Char('Nomor Polisi', readonly=True, related="vehicle_id.reg_number", store=True)
    reg_number_subtitue = fields.Char('Nomor Polisi', readonly=True, related="vehicle_subtitute_id.reg_number", store=True)
    ownership           = fields.Selection('Kepemilikan', readonly=True, related="vehicle_id.ownership", store=True)
    ownership_subtitute = fields.Selection('Kepemilikan', readonly=True, related="vehicle_subtitute_id.ownership", store=True)
    timbang_ksg_kbn     = fields.Float('Timbangan Kosong Kebun', readonly=True, states={'draft': [('readonly',False)]})
    timbang_isi_kbn     = fields.Float('Timbangan Isi Kebun', readonly=True, states={'draft': [('readonly',False)]})
    timbang_tara_kbn    = fields.Float('Timbangan Tara', compute='_compute_timbang', store=True)
    janjang_jml         = fields.Float('Jumlah Janjang', compute='_compute_janjang', store=True)
    pks_id              = fields.Many2one("res.partner", string="Nama PKS", ondelete="restrict", readonly=True, states={'draft': [('readonly',False)]})
    date_pks            = fields.Date("Tanggal PKS", readonly=True, states={'draft': [('readonly',False)]})
    timbang_isi_pks     = fields.Float('Timbangan Isi PKS', readonly=True, states={'draft': [('readonly',False)]})
    timbang_ksg_pks     = fields.Float('Timbangan Kosong PKS', readonly=True, states={'draft': [('readonly',False)]})
    timbang_tara_pks    = fields.Float('Timbangan Tara', compute='_compute_timbang', store=True)
    afkir               = fields.Float('Afkir', readonly=True, states={'draft': [('readonly',False)]})
    grading             = fields.Float('Grading', readonly=True, states={'draft': [('readonly',False)]})
    netto               = fields.Float('Netto', compute='_compute_timbang', store=True)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    line_ids            = fields.One2many('lhm.nap.line', inverse_name='lhm_nap_id', string="Detail Nota Angkut Panen", readonly=True, states={'draft': [('readonly',False)], 'revision': [('readonly',False)]})
    confirmed           = fields.Boolean('Confirmed', copy=False)
    cancelled           = fields.Boolean('Cancelled', copy=False)
    force_edit          = fields.Boolean('Revisi', copy=False)
    process             = fields.Boolean('Process', copy=False)
    state               = fields.Selection(compute='_get_state', store=True, selection=[
                                ('draft', 'New'), ('cancel', 'Cancelled'), ('process', 'Process'),
                                ('confirmed', 'Confirmed'), ('done', 'Done'), ('revision','Revisi')], string='Status',
                                copy=False, default='draft', index=True, readonly=True,
                                help="* New: Dokumen Baru.\n"
                                     "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                     "* Process: Menyimpan Data Timbangan Pabrik ke Detail Nota Angkut Panen.\n"
                                     "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                     "* Done: Dokumen Sudah Selesai Diproses. \n")
    invoice_id          = fields.Many2one('account.move', 'NAP Invoice')
    plasma_invoice_id   = fields.Many2one('account.move', 'NAP Invoice Plasma')
    contractor_id       = fields.Many2one('res.partner', 'Kontraktor', readonly=True, states={'draft': [('readonly',False)], 'confirmed': [('readonly',False)], 'revision': [('readonly',False)]})
    lhm_contractor_id   = fields.Many2one('lhm.contractor', 'Contractor Book', readonly=True)
    product_id          = fields.Many2one('product.product', string="Product")
    product_qty         = fields.Float(string="Quantity")
    uom_id              = fields.Many2one('uom.uom', string="Unit of Measure")
    quality             = fields.Integer(string="Quality")
    kebun_line_ids      = fields.One2many('timbangan.kebun', inverse_name='lhm_nap_id', string="Penamaan")
    pabrik_line_ids     = fields.One2many('timbangan.pabrik', inverse_name='lhm_nap_id', string="Penamaan")
    partner_id          = fields.Many2one('res.partner', string="Partner")
    drc                 = fields.Float(string='DRC')
    # drc_id             = fields.One2many('lhm.drc', 'nap_id', string="DRC Lines")
    _order = "date_nap desc"

    @api.depends('confirmed', 'invoice_id', 'invoice_id.state', 'cancelled', 'process', 'force_edit')
    def _get_state(self):
        for record in self:
            if record.confirmed:
                record.state = 'done'
            elif record.process:
                record.state = 'process'
            elif record.cancelled:
                record.state = 'cancel'
            elif record.force_edit:
                record.state = 'revision'
            else:
                record.state = 'draft'

    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'vdata_panen_nap_naf')
    #     self.env.cr.execute("""
    #         CREATE OR REPLACE VIEW vdata_panen_nap_naf AS (
    #         SELECT 'panen' AS grp,
    #             lrb.tgl_panen,
    #             lpb.afdeling_id,
    #             lpb.id AS block_id,
    #             lrb.tgl_panen AS tgl_trans,
    #             sum(lrb.value) AS jjg_qty
    #         FROM lhm_restan_balance lrb
    #         LEFT JOIN lhm_plant_block lpb ON lpb.id = lrb.block_id
    #         GROUP BY lrb.tgl_panen, lpb.afdeling_id, lpb.id
    #         UNION ALL
    #         SELECT 'panen' AS grp,
    #             ltpl.date AS tgl_panen,
    #             lpb.afdeling_id,
    #             lpb.id AS block_id,
    #             ltpl.date AS tgl_trans,
    #             sum(ltpl.nilai) AS jjg_qty
    #         FROM lhm_transaction lt
    #         LEFT JOIN lhm_transaction_process_line ltpl ON lt.id = ltpl.lhm_id
    #         LEFT JOIN lhm_activity la ON la.id = ltpl.activity_id
    #         LEFT JOIN lhm_plant_block lpb ON lpb.location_id = ltpl.location_id
    #         WHERE la.is_panen = TRUE AND lt.state IN ('done', 'close')
    #         GROUP BY ltpl.date, lpb.afdeling_id, lpb.id
    #         UNION ALL
    #         SELECT 'nap' AS grp,
    #             lnl.tgl_panen,
    #             lpb.afdeling_id,
    #             lnl.block_id,
    #             ln.date_pks AS tgl_trans,
    #             - sum(lnl.qty_nap) AS jjg_qty
    #         FROM lhm_nap ln
    #         LEFT JOIN lhm_nap_line lnl ON lnl.lhm_nap_id = ln.id
    #         LEFT JOIN lhm_plant_block lpb ON lpb.id = lnl.block_id
    #         WHERE ln.state IN ('confirmed', 'done') AND lnl.block_id IS NOT NULL
    #         GROUP BY lnl.tgl_panen, lpb.afdeling_id, lnl.block_id, ln.date_pks
    #         UNION ALL
    #         SELECT 'naf' AS grp,
    #             lnal.tgl_panen,
    #             lpb.afdeling_id,
    #             lnal.block_id,
    #             lna.date_naf AS tgl_trans,
    #             - sum(lnal.qty) AS jjg_qty
    #         FROM lhm_nap_afkir lna
    #         LEFT JOIN lhm_nap_afkir_line lnal ON lnal.lhm_nap_afkir_id = lna.id
    #         LEFT JOIN lhm_plant_block lpb ON lpb.id = lnal.block_id
    #         WHERE lna.state IN ('confirmed', 'done') AND lnal.block_id IS NOT NULL
    #         GROUP BY lnal.tgl_panen, lpb.afdeling_id, lnal.block_id, lna.date_naf
    #         )
    #     """)

    @api.onchange('vehicle_id' ,'vehicle_subtitute_id')
    def onchange_vehicle(self):
        if self.vehicle_id:
            self.contractor_id = self.vehicle_id and self.vehicle_id.partner_id and self.vehicle_id.partner_id.id or False
        elif self.vehicle_subtitute_id:
            self.contractor_id = self.vehicle_subtitute_id and self.vehicle_subtitute_id.partner_id and self.vehicle_subtitute_id.partner_id.id or False

    @api.depends('confirmed', 'invoice_id', 'invoice_id.state', 'cancelled', 'process','force_edit')
    def _get_state(self):
        if self.confirmed:
            self.state = 'done'
        elif self.process:
            self.state = 'process'
        elif self.cancelled:
            self.state = 'cancel'
        elif self.force_edit:
            self.state = 'revision'
        else:
            self.state = 'draft'

    def unlink(self):
        for nap in self:
            if nap.state not in ['draft']:
                raise UserError(_('Status Nota Angkut Panen dengan nomor %s adalah %s.\n'
                                  'Nota Angkut Panen hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (nap.name, nap.state.title()))
        nap = super(lhm_nap, self).unlink()
        return nap
    
    @api.model
    def create(self, values):
        if values.get('no_nap'):
            values['name'] = values['no_nap']
        else:
            afdeling = self.env['res.afdeling'].browse(values.get('afdeling_id'))
            date_nap = values.get('date_nap')
            if date_nap:
                date_nap = fields.Date.from_string(date_nap)
            if afdeling and date_nap:
                values['name'] = f"{afdeling.name}/{date_nap.strftime('%Y-%m-%d')}"
            else:
                values['name'] = _('New')
        return super(lhm_nap, self).create(values)
    
    def create_material_receipt(self):
        self.state = 'confirmed'
        for record in self:
            for line in record.pabrik_line_ids:
                line._create_or_update_stock_picking()

    def button_confirm(self):
        for record in self:
            for nap_line in record.line_ids:
                if nap_line.employee_id:
                    if nap_line.product_id.name in ["Latex", "Lump"] and nap_line.drc == 0:
                        raise ValidationError(
                            _("Tidak dapat mengkonfirmasi dokumen ini karena DRC untuk produk '%s' bernilai 0. Harap periksa dan masukkan nilai DRC di form DRC.")
                            % nap_line.product_id.name
                        )
                    if nap_line.lhm_transaction_nap_id.lhm_id.state == 'draft':
                        raise ValidationError(
                            _("Tidak dapat mengkonfirmasi dokumen ini karena terdapat dokumen LHM dengan tanggal yang sama dalam status 'draft'. Periksa dan selesaikan terlebih dahulu dokumen LHM tersebut.")
                        )
                    if nap_line.product_id.name == "Latex":
                        nap_line.lhm_transaction_nap_id.write({
                            'product_id': nap_line.product_id.id,
                            'hasil_1_nap': nap_line.qty_nap,
                            'satuan_1_nap': nap_line.uom_id.id,
                            'drc_latex_nap': nap_line.drc,
                        })
                    elif nap_line.product_id.name == "Lump":
                        nap_line.lhm_transaction_nap_id.write({
                            'product_id_2': nap_line.product_id.id,
                            'hasil_2_nap': nap_line.qty_nap,
                            'satuan_2_nap': nap_line.uom_id.id,
                            'drc_lump_nap': nap_line.drc,
                        })
                    else:
                        nap_line.lhm_transaction_nap_id.write({
                            'product_id': nap_line.product_id.id,
                            'hasil_1_nap': nap_line.qty_nap,
                            'satuan_1_nap': nap_line.uom_id.id,
                        })
                if nap_line.supplier_id:
                    if nap_line.product_id.name == "Latex":
                        nap_line.lhm_contractor_nap_id.write({
                            'product_id': nap_line.product_id.id,
                            'nilai': nap_line.qty_nap,
                            'uom_id': nap_line.uom_id.id,
                            'drc_latex_nap': nap_line.drc,
                        })
                    elif nap_line.product_id.name == "Lump":
                        nap_line.lhm_contractor_nap_id.write({
                            'product_id_2': nap_line.product_id.id,
                            'nilai2': nap_line.qty_nap,
                            'uom2_id': nap_line.uom_id.id,
                            'drc_lump_nap': nap_line.drc,
                        })
                    else:
                        nap_line.lhm_contractor_nap_id.write({
                            'product_id': nap_line.product_id.id,
                            'nilai': nap_line.qty_nap,
                            'uom_id': nap_line.uom_id.id,
                        })
                nap_line.lhm_transaction_nap_id.lhm_transaction_line_id.get_wage_borong_panen()
                nap_line.lhm_contractor_nap_id.convert_karet_contractor()
            self.state = 'done'

    def button_draft(self):
        for nap in self:
            if nap.sudo().invoice_id and nap.sudo().invoice_id.state not in ('draft','cancel'):
                raise UserError(_('Anda tidak dapat meng-Cancel Nota Angkut Panen \n'
                                  'yang telah memiliki Invoice.\n'
                                  'Silahkan Cancel Invoice tersebut terlebih dahulu. Invoice : %s')%nap.invoice_id.internal_number)
            for link_lhm in nap.line_ids.mapped('lhm_line_ids'):
                link_lhm.unlink()
        self.state = 'draft'
        self.confirmed = False
        self.cancelled = False
        self.process = False
        self.line_ids.write({'lhm_progress_ids': [(5,False,False)]})

    def button_cancel(self):
        self.state = 'cancel'
        self.confirmed = False
        self.cancelled = True
        self.process = False

    def button_revise(self):
        for nap in self:
            for link_lhm in nap.line_ids.mapped('lhm_line_ids'):
                link_lhm.unlink()
        self.confirmed = False
        self.force_edit = True
        self.line_ids.write({'lhm_progress_ids': [(5,False,False)]})

    def button_approve_revision(self):
        self.confirmed = True
        self.force_edit = False
        self.line_ids.link_to_lhm_progress()
        self.line_ids.allocate_nap_line_to_lhm_line()
                        
    def button_save_to_nap_line(self):
        self.state = 'process'
        self.process = True
        for record in self:
            record.line_ids.unlink()
            employee_data = {}
            supplier_data = {}

            for pabrik_line in record.pabrik_line_ids:
                kebun_line = self.env['timbangan.kebun'].search([
                    ('lhm_nap_id', '=', self.id),
                    ('block_id', '=', pabrik_line.block_id.id),
                    ('product_id', '=', pabrik_line.product_id.id),
                    ('tgl_panen', '=', pabrik_line.tgl_panen),
                ], limit=1)

                if kebun_line:
                    nap_lines = self.env['lhm.transaction.nap.line'].search([
                        ('lhm_transaction_line_id.location_id', '=', pabrik_line.block_id.location_id.id),
                        ('lhm_transaction_line_id.date', '=', pabrik_line.tgl_panen),
                        ('lhm_transaction_line_id.activity_id.is_nap', '=', True),
                    ])

                    contractor_lines = self.env['lhm.contractor.nap.line'].search([
                        ('contractor_line_id.location_id', '=', pabrik_line.block_id.location_id.id),
                        ('contractor_id.date', '=', pabrik_line.tgl_panen),
                    ])

                    for nap_line in nap_lines:
                        employee_id = nap_line.employee_id.id
                        product_id = pabrik_line.product_id.id

                        if employee_id not in employee_data:
                            employee_data[employee_id] = {
                                'employee_id': employee_id,
                                'product_1': None,
                                'hasil_1_nap': None,
                                'drc_latex': None,
                                'uom_1': None,
                                'product_2': None,
                                'hasil_2_nap': None,
                                'drc_lump': None,
                                'lhm_transaction_nap_id': nap_line.id,
                                'block_id': pabrik_line.block_id.id,
                                'tgl_panen': pabrik_line.tgl_panen
                            }

                        if nap_line.lhm_transaction_line_id.product_id.id == product_id:
                            if employee_data[employee_id]['product_1'] is None:
                                employee_data[employee_id]['product_1'] = nap_line.lhm_transaction_line_id.product_id.id
                                employee_data[employee_id]['hasil_1_nap'] = (
                                    (nap_line.lhm_transaction_line_id.hasil_1 / kebun_line.product_qty) * pabrik_line.product_qty
                                )
                                employee_data[employee_id]['drc_latex'] = pabrik_line.drc
                                employee_data[employee_id]['uom_1'] = pabrik_line.uom_id.id
                        elif nap_line.lhm_transaction_line_id.product_id_2.id == product_id:
                            employee_data[employee_id]['product_2'] = nap_line.lhm_transaction_line_id.product_id_2.id
                            employee_data[employee_id]['hasil_2_nap'] = (
                                (nap_line.lhm_transaction_line_id.hasil_2 / kebun_line.product_qty) * pabrik_line.product_qty
                            )
                            employee_data[employee_id]['drc_lump'] = pabrik_line.drc
                            employee_data[employee_id]['uom_2'] = pabrik_line.uom_id.id

                    for contractor_line in contractor_lines:
                        supplier_id = contractor_line.supplier_id.id
                        product_id = pabrik_line.product_id.id
                        supplier_key = (supplier_id, pabrik_line.block_id.id, pabrik_line.tgl_panen)

                        if supplier_key not in supplier_data:
                            supplier_data[supplier_key] = {
                                'supplier_id': supplier_id,
                                'product_1': None,
                                'hasil_1_nap': None,
                                'drc_latex': None,
                                'uom_1': None,
                                'product_2': None,
                                'hasil_2_nap': None,
                                'drc_lump': None,
                                'lhm_contractor_nap_id': contractor_line.id,
                                'block_id': pabrik_line.block_id.id,
                                'tgl_panen': pabrik_line.tgl_panen
                            }

                        if contractor_line.product_id.id == product_id:  
                            if supplier_data[supplier_key]['product_1'] is None:
                                supplier_data[supplier_key]['product_1'] = contractor_line.product_id.id
                                supplier_data[supplier_key]['hasil_1_nap'] = (
                                    (contractor_line.contractor_line_id.nilai / kebun_line.product_qty) * pabrik_line.product_qty
                                )
                                supplier_data[supplier_key]['drc_latex'] = pabrik_line.drc
                                supplier_data[supplier_key]['uom_1'] = pabrik_line.uom_id.id
                        elif contractor_line.product_id_2.id == product_id:
                            supplier_data[supplier_key]['product_2'] = contractor_line.product_id_2.id
                            supplier_data[supplier_key]['hasil_2_nap'] = (
                                (contractor_line.contractor_line_id.nilai2 / kebun_line.product_qty) * pabrik_line.product_qty
                            )
                            supplier_data[supplier_key]['drc_lump'] = pabrik_line.drc
                            supplier_data[supplier_key]['uom_2'] = pabrik_line.uom_id.id

            for employee_id, data in employee_data.items():
                if data['hasil_1_nap']:
                    transaction_exists = (
                        self.env['lhm.transaction.nap.line'].search_count([('id', '=', data['lhm_transaction_nap_id'])]) > 0
                    )
                    if transaction_exists:
                        self.env['lhm.nap.line'].create({
                            'lhm_nap_id': record.id,
                            'block_id': data['block_id'],
                            'employee_id': data.get('employee_id'),
                            'product_id': data['product_1'],
                            'tgl_panen': data['tgl_panen'],
                            'qty_nap': data['hasil_1_nap'],
                            'drc': data['drc_latex'],
                            'uom_id': data['uom_1'],
                            'lhm_transaction_nap_id': data['lhm_transaction_nap_id'],
                        })

                if data['product_2'] and data['hasil_2_nap']:
                    transaction_exists = (
                        self.env['lhm.transaction.nap.line'].search_count([('id', '=', data['lhm_transaction_nap_id'])]) > 0
                    )
                    if transaction_exists:
                        self.env['lhm.nap.line'].create({
                            'lhm_nap_id': record.id,
                            'block_id': data['block_id'],
                            'employee_id': data.get('employee_id'),
                            'product_id': data['product_2'],
                            'tgl_panen': data['tgl_panen'],
                            'qty_nap': data['hasil_2_nap'],
                            'drc': data['drc_lump'],
                            'uom_id': data['uom_2'],
                            'lhm_transaction_nap_id': data['lhm_transaction_nap_id'],
                        })

            for supplier_key, data in supplier_data.items():
                if data['hasil_1_nap']:
                    transaction_exists = (
                        self.env['lhm.contractor.nap.line'].search_count([('id', '=', data['lhm_contractor_nap_id'])]) > 0
                    )    
                    if transaction_exists:
                        self.env['lhm.nap.line'].create({
                            'lhm_nap_id': record.id,
                            'block_id': data['block_id'],
                            'supplier_id': data.get('supplier_id'),
                            'product_id': data['product_1'],
                            'tgl_panen': data['tgl_panen'],
                            'qty_nap': data['hasil_1_nap'],
                            'drc': data['drc_latex'],
                            'uom_id': data['uom_1'],
                            'lhm_contractor_nap_id': data['lhm_contractor_nap_id'],
                        })

                if data['product_2'] and data['hasil_2_nap']:
                    transaction_exists = (
                        self.env['lhm.contractor.nap.line'].search_count([('id', '=', data['lhm_contractor_nap_id'])]) > 0
                    )
                    if transaction_exists:
                        self.env['lhm.nap.line'].create({
                            'lhm_nap_id': record.id,
                            'block_id': data['block_id'],
                            'supplier_id': data.get('supplier_id'),
                            'product_id': data['product_2'],
                            'tgl_panen': data['tgl_panen'],
                            'qty_nap': data['hasil_2_nap'],
                            'drc': data['drc_lump'],
                            'uom_id': data['uom_2'],
                            'lhm_contractor_nap_id': data['lhm_contractor_nap_id'],
                        })

class lhm_nap_line(models.Model):
    _name               = 'lhm.nap.line'
    _description        = 'LHM Nota Angkut Panen Line'

    @api.depends('block_id', 'tgl_panen')
    def _compute_panen(self):
        for line in self:
            if line.block_id and line.tgl_panen:
                total_lhm       = 0
                total_nap       = 0
                if isinstance(line.id, int):
                    domain = [
                        ('block_id', '=', line.block_id.id),
                        ('tgl_panen', '=', line.tgl_panen),
                        ('id', '!=', line.id)]
                else:
                    domain = [
                        ('block_id', '=', line.block_id.id),
                        ('tgl_panen', '=', line.tgl_panen)]
                other_nap       = self.env['lhm.nap.line'].search(domain)
                progress_ids    = self.env['lhm.transaction.process.line'].search([('date', '=', line.tgl_panen), ('location_id', '=', line.block_id.location_id.id)])
                balance_ids     = self.env['lhm.restan.balance'].search([('tgl_panen', '=', line.tgl_panen), ('block_id', '=', line.block_id.id)])
                if balance_ids:
                    for balance in balance_ids:
                        total_lhm += balance.value
                if progress_ids:
                    for progress in progress_ids:
                        if progress.activity_id.is_panen:
                            total_lhm += progress.nilai
                if other_nap:
                    for nap in other_nap:
                        total_nap += nap.qty_nap
                line.qty_panen_lhm  = total_lhm
                line.qty_akum_nap   = total_nap
                line.qty_sisa_panen = total_lhm - total_nap

    @api.depends('lhm_nap_id.state','lhm_line_ids','lhm_line_ids.lhm_id.state',
        'lhm_line_ids.lhm_line_id.location_id','lhm_line_ids.lhm_line_id.activity_id',
        'lhm_line_ids.lhm_line_id.work_result')
    def _check_allocation_state(self):
        for line in self:
            # total_allocation = sum(line.lhm_line_ids.mapped('nilai'))
            total_panen = sum(line.mapped('lhm_progress_ids').mapped('nilai'))
            total_allocation = 0.0
            for xline in line.lhm_line_ids:
                if xline.lhm_line_id and xline.lhm_line_id.activity_id.is_panen \
                        and xline.lhm_line_id.location_id.id==line.block_id.location_id.id:
                    total_allocation+=(xline.lhm_line_id.work_result/total_panen)*line.qty_nap
            if round(total_allocation,2) < line.qty_nap:
                line.pending_allocation = True
            else:
                line.pending_allocation = False

    name                     = fields.Char('Name', related="lhm_nap_id.name", store=True)
    block_id                 = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    tgl_panen                = fields.Date("Tgl. Panen")
    qty_panen_lhm            = fields.Float("Total Panen", compute="_compute_panen", store=True)
    qty_akum_nap             = fields.Float("Akumulasi NAP", compute="_compute_panen", store=True)
    qty_sisa_panen           = fields.Float("Sisa Panen", compute="_compute_panen", store=True)
    qty_nap                  = fields.Float("Total NAP")
    lhm_nap_id               = fields.Many2one("lhm.nap", string="Nota Buah Angkut", ondelete="cascade")
    transaction_nap_line_ids = fields.One2many('lhm.transaction.nap.line', 'lhm_nap_line_id', string="Transaction NAP Lines")
    lhm_progress_ids         = fields.Many2many('lhm.transaction.process.line', 'lhm_process_nap_line_rel', 'nap_line_id', 'progress_id', 'LHM Progress Ref')
    lhm_line_ids             = fields.One2many('lhm.transaction.line.nap.line', 'nap_line_id', 'LHM Detail')
    pending_allocation       = fields.Boolean('Pending Allocaton', compute='_check_allocation_state', store=True)
    product_id               = fields.Many2one('product.product', string="Product")
    product_qty              = fields.Float(string="Quantity")
    uom_id                   = fields.Many2one('uom.uom', string="UoM")
    pemanen                  = fields.Char(string='Pemanen')
    employee_id              = fields.Many2one("hr.employee", string="Pemanen", ondelete="restrict")
    supplier_id              = fields.Many2one("res.partner", string="Kontraktor", readonly=True)
    drc                      = fields.Float(string='DRC')
    lhm_transaction_nap_id   = fields.Many2one('lhm.transaction.nap.line', string='Nap Line LHM')
    lhm_contractor_nap_id    = fields.Many2one('lhm.contractor.nap.line')

    @api.onchange('block_id', 'tgl_panen')
    def _onchange_block_tgl_panen(self):
        if self.block_id and self.tgl_panen:
            nap_lines = self.env['lhm.transaction.nap.line'].search([
                ('lhm_transaction_line_id.location_id', '=', self.block_id.location_id.id),
                ('lhm_transaction_line_id.lhm_id.date', '=', self.tgl_panen),
                ('lhm_transaction_line_id.activity_id.is_panen', '=', True),
            ])
            employee_ids = nap_lines.mapped('employee_id')
            return {'domain': {'employee_id': [('id', 'in', employee_ids.ids)]}}
            # tambahkan looping

    def compute_weight(self):
        self.ensure_one()
        weight = 0.0
        weight = (self.qty_nap*self.block_id.with_context({'date': self.lhm_nap_id.date_pks})._get_rate_bjr()) * self.lhm_nap_id.netto \
            / sum([x.qty_nap*x.block_id.with_context({'date': self.lhm_nap_id.date_pks})._get_rate_bjr() for x in self.lhm_nap_id.line_ids])
        return weight

    def link_to_lhm_progress(self):
        for line in self:
            lhm_lines = self.env['lhm.transaction.process.line'].search([ \
                ('location_id','=',line.block_id.location_id.id), 
                ('lhm_id.state','!=','draft'), 
                ('lhm_id.date','=',line.tgl_panen), 
                ('activity_id.is_panen','=',True)
                ])
            if not lhm_lines:
                continue
            else:
                line.write({'lhm_progress_ids': [(6,0,lhm_lines.ids)]})
                #Trigger Function
                lhm_lines.write({'nap_line_ids': []})

    def allocate_nap_line_to_lhm_line(self):
        for nap_line in self.filtered(lambda x: x.pending_allocation):
            vals = []
            total_panen = sum(nap_line.mapped('lhm_progress_ids').mapped('nilai'))
            if not nap_line.mapped('lhm_progress_ids'):
                raise ValidationError(_("Tidak dapat menemukan LHM.\nSilahkan \
                        input LHM dan Progress LHMnya sebelum membuat NAP"))
            if total_panen < nap_line.qty_nap:
                raise ValidationError(_("Total Progress Panen dari LHM untuk Blok %s lebih \n \
                        sedikit dibandingkan dengan NAP yg dikeluarkan"))
                # continue
            for progress in nap_line.lhm_progress_ids:
                lhm_lines = progress.lhm_id.mapped('lhm_line_ids').filtered(lambda x: x.location_id==progress.location_id and x.activity_id==progress.activity_id and x.activity_id.is_panen)
                # total_panen = sum(lhm_lines.mapped('work_result'))
                for line in lhm_lines:
                    janjang = total_panen and (line.work_result/total_panen)*nap_line.qty_nap or 0.0
                    berat = total_panen and (line.work_result/total_panen)*nap_line.compute_weight() or 0.0
                    vals.append((0,0,{
                        'lhm_line_id': line.id,
                        'nap_line_id': nap_line.id,
                        'nilai': janjang,
                        'uom_id': line.satuan_id and line.satuan_id.id or False,
                        'nilai2': berat,
                    }))
                    # self.env['lhm.transaction.line.nap.line'].create(vals)
            if vals:
                nap_line.write({'lhm_line_ids': vals})

    @api.model
    def _cron_linked_to_nap(self):
        pending_line = self.search([('lhm_progress_ids','=',False), ('lhm_nap_id.state','not in',['draft','revision'])])
        pending_line.link_to_lhm_progress()
        pending_line = self.search([('pending_allocation','=',True), ('lhm_nap_id.state','not in',['draft','revision'])])
        pending_line.allocate_nap_line_to_lhm_line()

    def update_from_timbangan_kebun(self, block_id, tgl_panen, product_id, employee_id, qty_nap):
        for record in self:
            record.write({
                'block_id': block_id,
                'tgl_panen': tgl_panen,
                'product_id': product_id,
                'employee_id': employee_id,
                'qty_nap': qty_nap,
            })
    
    @api.model
    def create(self, vals):
        record = super(lhm_nap_line, self).create(vals)
        return record

    def write(self, vals):
        res = super(lhm_nap_line, self).write(vals)
        return res
    
    # @api.constrains('tgl_panen', 'block_id', 'lhm_nap_id')
    # def _check_attendance_id(self):
    #     for record in self:
    #         record._check_parent_one()
	#
    # def _check_parent_one(self):
    #     if self.tgl_panen and self.block_id and self.lhm_nap_id:
    #         if isinstance(self.lhm_nap_id.id, int):
    #             domain = [
    #                 ('tgl_panen', '=', self.tgl_panen),
    #                 ('block_id', '=', self.block_id.id),
    #                 ('lhm_nap_id', '=', self.lhm_nap_id.id),
    #                 ('id','!=',self.id)]
    #             nap_line = self.search(domain)
    #             if nap_line:
    #                 raise UserError(_(
    #                     'Anda tidak dapat membuat nota angkut panen dengan nama blok %s dan tanggal %s karena terjadi duplikasi data!') % (
    #                                 self.block_id.name, self.tgl_panen))
    #     return True

    # @api.onchange('qty_sisa_panen', 'qty_nap')
    # def onchange_qty_nap(self):
    #     if self.qty_sisa_panen and self.qty_nap:
    #         if self.qty_sisa_panen < self.qty_nap:
    #             self.qty_nap = 0.00
    #             return {
    #                 'warning': {'title': _('Kesalahan Input Data'),
    #                             'message': _("Total Tidak boleh lebih besar daripada sisa")},
    #             }
########################################### End Of Transaction Nota Angkut Panen #############################################
class TimbanganKebun(models.Model):
    _name = 'timbangan.kebun'
    _description = 'Timbangan Kebun'

    lhm_nab_id  = fields.Many2one('lhm.nab', string='LHM NAB')
    lhm_nap_id  = fields.Many2one('lhm.nap', string='LHM NAP')
    product_id  = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Product Quantity')
    uom_id      = fields.Many2one('uom.uom', string='UoM')
    block_id    = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict")
    tgl_panen   = fields.Date(string='Tanggal Panen')

    @api.model
    def create(self, vals):
        record = super(TimbanganKebun, self).create(vals)
        record._create_or_update_timbangan_pabrik()
        record._create_or_update_nota_angkut_panen()
        return record

    def write(self, vals):
        res = super(TimbanganKebun, self).write(vals)
        self._create_or_update_timbangan_pabrik()
        self._create_or_update_nota_angkut_panen()
        return res

    def _create_or_update_timbangan_pabrik(self):
        for record in self:
            pabrik_vals = {
                'lhm_nab_id': record.lhm_nab_id.id,
                'lhm_nap_id': record.lhm_nap_id.id,
                'product_id': record.product_id.id,
                'uom_id': record.uom_id.id,
                'block_id': record.block_id.id,
                'tgl_panen': record.tgl_panen,
            }
            existing_pabrik = self.env['timbangan.pabrik'].search([
                ('lhm_nab_id', '=', record.lhm_nab_id.id),
                ('lhm_nap_id', '=', record.lhm_nap_id.id),
                ('product_id', '=', record.product_id.id),
                ('block_id', '=', record.block_id.id)
            ])
            if existing_pabrik:
                existing_pabrik.write(pabrik_vals)
            else:
                self.env['timbangan.pabrik'].create(pabrik_vals)

    def _create_or_update_nota_angkut_panen(self):
        for record in self:
            if record.lhm_nap_id:
                nap_lines = record.lhm_nap_id.line_ids.filtered(
                    lambda l: l.block_id == record.block_id and l.tgl_panen == record.tgl_panen
                )
                for nap_line in nap_lines:
                    detail_vals = {
                        'block_id': record.block_id.id,
                        'employee_id': nap_line.employee_id.id,
                        'product_id': record.product_id.id,
                        'tgl_panen': record.tgl_panen,
                        'qty_nap': nap_line.qty_nap,
                    }
                    existing_details = self.env['lhm.nap.line'].search([
                        ('block_id', '=', record.block_id.id),
                        ('employee_id', '=', nap_line.employee_id.id),
                        ('tgl_panen', '=', record.tgl_panen),
                        ('product_id', '=', record.product_id.id),
                    ])
                    
                    if existing_details:
                        for detail in existing_details:
                            detail.update_from_timbangan_kebun(
                                record.block_id.id, record.tgl_panen, record.product_id.id, nap_line.employee_id.id, nap_line.qty_nap)
                    else:
                        self.env['lhm.nap.line'].create(detail_vals)

class TimbanganPabrik(models.Model):
    _name = 'timbangan.pabrik'
    _description = 'Timbangan Pabrik'

    lhm_nab_id         = fields.Many2one('lhm.nab', string='LHM NAB')
    lhm_nap_id         = fields.Many2one('lhm.nap', string='LHM NAP')
    product_id         = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty        = fields.Float(string='Product Quantity')
    uom_id             = fields.Many2one('uom.uom', string='UoM')
    drc                = fields.Float(string='DRC')
    quality_pabrik     = fields.Many2one('lhm.quality.pabrik', string='Quality')
    tgl_panen          = fields.Date(string='Tanggal Panen')
    tgl_terima         = fields.Date(string='Tanggal Terima')
    block_id           = fields.Many2one("lhm.plant.block", string="Lokasi", ondelete="restrict", readonly=True)
    stock_picking_id   = fields.Many2one('stock.picking', string='Stock Picking', ondelete='cascade')
    # drc_line_ids       = fields.One2many('lhm.drc.line', 'timbangan_pabrik_id', string="DRC Lines", ondelete="cascade")


    @api.model
    def create(self, vals):
        return super(TimbanganPabrik, self).create(vals)

    def write(self, vals):
        return super(TimbanganPabrik, self).write(vals)

    def _create_or_update_stock_picking(self):
        if not self.uom_id:
            raise UserError("Unit of Measure (UoM) harus diisi sebelum menyimpan data.")

        if not self.stock_picking_id:
            picking_vals = {
                # 'partner_id': self.lhm_nap_id.partner_id.id if self.lhm_nap_id else False,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                'move_ids_without_package': [(0, 0, {
                    'product_id': self.product_id.id,
                    'name': self.product_id.name,
                    'product_uom_qty': self.product_qty,
                    'product_uom': self.uom_id.id,
                    'location_id': self.env.ref('stock.stock_location_suppliers').id,
                    'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                })],
                'picking_type_id': self.env.ref('stock.picking_type_in').id,
            }
            picking = self.env['stock.picking'].create(picking_vals)
            self.stock_picking_id = picking.id
            # print(">>>>>>>>>>>>>>>>", self.block_id.location_id)
            # print(">>>>>>>>>>>>>>>>", stop)
        else:
            self.stock_picking_id.move_ids_without_package[0].write({
                'product_uom_qty': self.product_qty,
                'product_uom': self.uom_id.id,
            })
