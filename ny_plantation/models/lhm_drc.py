from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

class lhm_drc(models.Model):
    _name = 'lhm.drc'
    _description = 'Ini Header DRC'

    drc_line_ids = fields.One2many('lhm.drc.line', 'drc_id', string="Lines")
    nap_id       = fields.Many2one('lhm.nap', ondelete="cascade")
    name         = fields.Char(string="No. Dok", default='New')
    date         = fields.Date(string="Tanggal", required=True, default=fields.Date.context_today)
    tgl_panen    = fields.Date("Tgl. Panen")
    confirmed    = fields.Boolean(string="Confirmed", default=False)
    cancel       = fields.Boolean(string="Cancelled", default=False)
    state        = fields.Selection([
        ('draft', 'New'), 
        ('cancel', 'Cancelled'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft', index=True, readonly=True,
    help="* New: Dokumen Baru.\n"
         "* Cancelled: Dokumen Telah Dibatalkan.\n"
         "* Confirmed: Dokumen Sedang Di Proses.\n")

    @api.model
    def create(self, values):
        date = values.get('date', fields.Date.context_today(self))
        date_obj = fields.Date.from_string(date)
        existing_records = self.search_count([('date', '=', date)])
        sequence = str(existing_records + 1).zfill(2)
        values['name'] = f"DRC/{date_obj.strftime('%Y-%m-%d')}/{sequence}"
        return super(lhm_drc, self).create(values)
    
    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise exceptions.UserError(_("Dokumen dengan status 'Confirmed' tidak dapat dihapus!"))
        return super(lhm_drc, self).unlink()
    
    @api.onchange('tgl_panen')
    def _onchange_tgl_panen(self):
        if not self.tgl_panen:
            self.drc_line_ids = [(5, 0, 0)]
            return
        nap_lines = self.env['lhm.nap.line'].search([
            ('tgl_panen', '=', self.tgl_panen),
            ('lhm_nap_id.state', '=', 'confirmed')
        ])
        if not nap_lines:
            raise ValidationError("Tidak ditemukan Dokumen NAP yang status 'Confirmed'. Silahkan cek Dokumen NAP yang terkait.")
        grouped_data = {}
        for nap_line in nap_lines:
            key = (nap_line.block_id.id, nap_line.product_id.id)
            if key not in grouped_data:
                grouped_data[key] = {
                    'block_id': nap_line.block_id.id,
                    'date': nap_line.tgl_panen,
                    'product': nap_line.product_id.id,
                    'uom': nap_line.uom_id.id,
                }
        drc_lines = [(0, 0, data) for data in grouped_data.values()]
        self.drc_line_ids = [(5, 0, 0)] + drc_lines
    
    @api.constrains('tgl_panen', 'drc_line_ids')
    def _existing_tgl_panen(self):
        for record in self:
            if record.tgl_panen and record.drc_line_ids:
                for line in record.drc_line_ids:
                    if line.block_id:
                        existing_drc = self.search([
                            ('tgl_panen', '=', record.tgl_panen),
                            ('drc_line_ids.block_id', '=', line.block_id.id),
                            ('id', '!=', record.id)
                        ])
                        if existing_drc:
                            raise ValidationError(
                                f"Tanggal Panen {record.tgl_panen} dengan Lokasi {line.block_id.name} "
                                f"sudah digunakan di dokumen lain. Harap pilih Tanggal atau Lokasi yang berbeda."
                            )
    
    def action_draft(self):
        napline = self.env['lhm.nap.line']
        for record in self:
            affected_nap_ids = set()
            for line in record.drc_line_ids:
                nap_line_records = napline.search([
                    ('block_id', '=', line.block_id.id),
                    ('tgl_panen', '=', line.date),
                    ('product_id', '=', line.product.id),
                    ('lhm_nap_id.state', '=', 'done'),
                ])
                for nap_line in nap_line_records:
                    nap_line.write({'drc': 0})
                    affected_nap_ids.add(nap_line.lhm_nap_id.id)
            if affected_nap_ids:
                nap_ids = self.env['lhm.nap'].browse(list(affected_nap_ids))
                nap_ids.write({'state': 'confirmed'})
            record.state = 'draft'

    def action_cancel(self):
        # for record in self:
            # for line in record.drc_line_ids:
            #     nap_lines = self.env['lhm.nap.line'].search([
            #         ('block_id', '=', line.block_id.id),
            #         ('tgl_panen', '=', line.date),
            #         ('product_id', '=', line.product.id)
            #     ])

                # for nap_line in nap_lines:
                #     if nap_line.lhm_nap_id.state != 'draft':
                #         raise ValidationError("Anda tidak bisa membatalkan dokumen ini karena terdapat NAP yang lokasi dan tanggalnya sama tetapi Status nya belum 'draft'.")
        self.state = 'cancel'

    def action_confirm(self):
        napline = self.env['lhm.nap.line']
        for record in self:
            for line in record.drc_line_ids:
                if not line.drc or line.drc == 0:
                    raise ValidationError(f"DRC pada baris dengan Lokasi '{line.block_id.name}' dan Produk '{line.product.name}' tidak boleh kosong atau nol.")
                nap_line_records = napline.search([
                    ('block_id', '=', line.block_id.id),
                    ('tgl_panen', '=', line.date),
                    ('product_id', '=', line.product.id),
                    ('lhm_nap_id.state', '=', 'confirmed'),
                ])
                if not nap_line_records:
                    raise ValidationError(f"Tidak ditemukan dokumen NAP untuk Lokasi '{line.block_id.name}', Tanggal Panen '{line.date}' yang statusnya Confirmed")
                for nap_line in nap_line_records:
                    nap_line.write({'drc': line.drc})
                    
            record.state = 'confirmed'


class lhm_drc_line(models.Model):
    _name = 'lhm.drc.line'
    _description = 'Ini Line DRC'

    drc_id = fields.Many2one('lhm.drc', string="Dokumen Utama", ondelete='cascade')
    block_id = fields.Many2one("lhm.plant.block", string="Lokasi")
    date = fields.Date(string="Tanggal")
    product = fields.Many2one('product.product', string="Product")
    uom = fields.Many2one('uom.uom', string="Unit of Measure")
    drc = fields.Float(string="DRC", required=True)
    nap_line_id = fields.Many2one('lhm.nap.line', string="NAP Line", ondelete="cascade")

    # @api.onchange('product')
    # def _onchange_product(self):
    #     if self.product:
    #         self.uom_id = self.product.uom_id
    #     else:
    #         self.uom_id = False

