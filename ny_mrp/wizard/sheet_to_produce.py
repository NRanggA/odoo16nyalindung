from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SheetToProduct(models.TransientModel):
    _name = 'wizard.sheet.to.product'
    _description = 'Helper : Sheet to Product'

    product_latex_id = fields.Many2one('product.product', string='Latex')
    latex_onhand_qty = fields.Float(related='product_latex_id.qty_available')

    bom_id = fields.Many2one('mrp.bom', string='Bill of Material')

    sheet_to_produce = fields.Float(compute='_compute_qty', readonly=False, store=True, precompute=True, string='Qty To Produce')

    @api.depends('latex_onhand_qty', 'bom_id')
    def _compute_qty(self):
        for rec in self:
            if rec.bom_id.bom_line_ids.filtered(lambda x: x.product_id.id==rec.latex_product_id.id):
                bom_qty = rec.bom_id.bom_line_ids.filtered(lambda x: x.product_id.id==rec.latex_product_id.id).product_qty
                rec.sheet_to_produce = ((rec.bom_id.product_qty / bom_qty) if bom_qty else 0.0)*rec.latex_onhand_qty
            else:
                rec.sheet_to_produce = 0.0