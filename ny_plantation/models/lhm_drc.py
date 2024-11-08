from odoo import models, fields, api

class lhm_drc(models.Model):
    _name = 'lhm.drc'
    _description = 'Ini Header DRC'

    drc_line_ids = fields.One2many('lhm.drc.line', 'drc_id', string="Lines")
    nap_id = fields.Many2one('lhm.nap', ondelete="cascade")
    name = fields.Char(string="No. Dok", required=True)
    date = fields.Date(string="Tanggal", default=fields.Date.context_today)
    confirmed = fields.Boolean(string="Confirmed", default=False)
    cancel = fields.Boolean(string="Cancelled", default=False)
    state = fields.Selection([
        ('draft', 'New'), 
        ('cancel', 'Cancelled'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft', index=True, readonly=True,
    help="* New: Dokumen Baru.\n"
         "* Cancelled: Dokumen Telah Dibatalkan.\n"
         "* Confirmed: Dokumen Sedang Di Proses.\n")
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'
    def action_cancel(self):
        for record in self:
            record.state = 'cancel'
    def action_confirm(self):
        NapLine = self.env['lhm.nap.line']
        for record in self:
            for line in record.drc_line_ids:
                nap_line_records = NapLine.search([
                    ('block_id', '=', line.block_id.id),
                    ('tgl_panen', '=', line.date),
                    ('product_id', '=', line.product.id)
                ])
                
                for nap_line in nap_line_records:
                    nap_line.write({'drc': line.drc})
                    
            record.state = 'confirmed'




class lhm_drc_line(models.Model):
    _name = 'lhm.drc.line'
    _description = 'Ini Line DRC'

    drc_id = fields.Many2one('lhm.drc', string="Dokumen Utama", ondelete='cascade')
    block_id = fields.Many2one("lhm.plant.block", string="Lokasi")
    date = fields.Date(string="Tanggal")
    product = fields.Many2one('product.product', string="Product", required=True)
    uom = fields.Many2one('uom.uom', string="Unit of Measure", required=True)
    drc = fields.Float(string="DRC", required=True)
    nap_line_id = fields.Many2one('lhm.nap.line', string="NAP Line", ondelete="cascade")

