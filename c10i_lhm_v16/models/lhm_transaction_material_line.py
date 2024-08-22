from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

class lhm_transaction_material_line(models.Model):
    _name           = 'lhm.transaction.material.line'
    _description    = 'LHM Transaction Material Line'

    name            = fields.Char(string="BPB", readonly=True)
    date            = fields.Date("Tanggal", )
    product_id      = fields.Many2one("product.product", string="Product", ondelete="restrict")
    activity_id     = fields.Many2one("lhm.activity", string="Aktivitas", ondelete="restrict")
    activity_name   = fields.Char(related="activity_id.name", string="Name")
    location_id     = fields.Many2one("lhm.location", string="Lokasi", ondelete="restrict")
    real_stock_qty  = fields.Float('SKB Qty', digits=dp.get_precision('Product Unit of Measure'),)
    product_uom_id  = fields.Many2one("uom.uom", string="UoM", ondelete="restrict")
    stock_qty       = fields.Float('Consumed Qty', digits=dp.get_precision('Product Unit of Measure'),)
    realization     = fields.Float('LHM Qty', digits=dp.get_precision('Product Unit of Measure'),)
    residual_qty    = fields.Float(compute='_get_residual', string='Residual', digits=dp.get_precision('Product Unit of Measure'),)
    # residual_qty    = fields.Float('Residual', digits=dp.get_precision('Product Unit of Measure'),)
    move_id         = fields.Many2one("stock.move", string="Stock Move", ondelete="restrict")
    picking_id      = fields.Many2one("stock.picking", string="Stock Picking", ondelete="restrict")
    progress_id     = fields.Many2one("lhm.transaction.process.line", string="Progress", ondelete="restrict")
    lhm_id          = fields.Many2one("lhm.transaction", string="LHM", ondelete="cascade")

    @api.depends('realization')
    def _get_residual(self):
        for line in self:
            residual = line.real_stock_qty - line.stock_qty - line.realization
            if residual < 0:
                raise UserError(_('Realisasi Salah.\n'
                                'Realisasi tidak dapat melebihi Jumlah yg di SKB'))
            line.residual_qty = residual
