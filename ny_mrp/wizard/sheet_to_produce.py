from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SheetToProduce(models.TransientModel):
    _name = 'wizard.mrp.sheet.to.produce'
    _description = 'Helper : Sheet to Product'

    mrp_id = fields.Many2one('mrp.production', 'Production Order')
    product_latex_id = fields.Many2one('product.product', string='Product')
    product_satuan_id = fields.Many2one('uom.uom', related='product_latex_id.uom_id', string='Satuan', readonly=True, store=True)
    # latex_onhand_qty = fields.Float(related='product_latex_id.qty_available')
    latex_onhand_qty = fields.Float('Onhand Qty Lateks')

    bom_id = fields.Many2one('mrp.bom', string='Bill of Material')

    sheet_to_produce = fields.Float(compute='_compute_qty', readonly=False, store=True, string='Qty To Produce')
    mrp_product_satuan_id = fields.Many2one('uom.uom', related='mrp_id.product_id.uom_id', string='Satuan To Produce', readonly=True, store=True)

    drc = fields.Float(string='DRC (%)', compute='_compute_qty', store=True)

    @api.depends('latex_onhand_qty', 'bom_id')
    def _compute_qty(self):
        for rec in self:
            if rec.bom_id.bom_line_ids.filtered(lambda x: x.product_id.id==rec.product_latex_id.id):
                bom_qty = rec.bom_id.bom_line_ids.filtered(lambda x: x.product_id.id==rec.product_latex_id.id).product_qty
                rec.sheet_to_produce = ((rec.bom_id.product_qty / bom_qty) if bom_qty else 0.0)*rec.latex_onhand_qty
                rec.drc = ((rec.bom_id.product_qty / bom_qty) if bom_qty else 0.0) * 100
            else:
                rec.sheet_to_produce = 0.0
                rec.drc = 0.0
    
    @api.onchange('product_latex_id')
    def onchange_product(self):
        # self.latex_onhand_qty = self.product_latex_id.qty_available
        self.latex_onhand_qty = self.product_latex_id.virtual_available
    
    def action_apply(self):
        self.mrp_id.write({'product_qty': self.sheet_to_produce})