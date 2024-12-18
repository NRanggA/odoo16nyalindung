from odoo import models, fields, api, Command, _
from odoo.exceptions import ValidationError, UserError

from odoo.tools import float_compare, float_round

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    is_pisang = fields.Boolean()
    scrap_qty = fields.Float('Scrap Quantity', default=0, digits='Product Unit of Measure', help="Quantity of products that will scrapped automatically from when packaging process.")
    
    def _check_qty(self, product_qty, uom_id, rounding_method="HALF-UP"):
        self.ensure_one()
        if not self.is_pisang or not self.env.context.get('ripening',False):
            return super(ProductPackaging, self)._check_qty(product_qty, uom_id, rounding_method=rounding_method)
        default_uom = self.product_id.uom_id
        packaging_qty = default_uom._compute_quantity(self.qty + self.scrap_qty, uom_id)
        # We do not use the modulo operator to check if qty is a mltiple of q. Indeed the quantity
        # per package might be a float, leading to incorrect results. For example:
        # 8 % 1.6 = 1.5999999999999996
        # 5.4 % 1.8 = 2.220446049250313e-16
        if product_qty and packaging_qty:
            rounded_qty = float_round(product_qty / packaging_qty, precision_rounding=1.0,
                                  rounding_method=rounding_method) * packaging_qty
            return rounded_qty if float_compare(rounded_qty, product_qty, precision_rounding=default_uom.rounding) else product_qty
        return product_qty

class StockRipeningPisangLine(models.Model):
    _name = 'stock.ripening.pisang.line'
    _description = 'Detail Ripening Pisang'

    ripening_id = fields.Many2one('stock.ripening.pisang', string='Reference')
    company_id = fields.Many2one(related='ripening_id.company_id', store=True)
    product_id = fields.Many2one('product.product', string='Product', 
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", 
        index=True, required=True, check_company=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom = fields.Many2one(
        'uom.uom', "UoM", required=True, domain="[('category_id', '=', product_uom_category_id)]",
        compute="_compute_product_uom", store=True, readonly=False, precompute=True,
    )
    product_qty = fields.Float('Source Quantity')
    
    product_packaging_id = fields.Many2one('product.packaging', string="Packaging",
        compute='_compute_product_packaging_id', store=True, readonly=False, precompute=True,
        domain="[('sales', '=', True), ('product_id','=',product_id),('is_pisang','=',True)]",
        check_company=True)
    product_packaging_qty = fields.Float(string="Packaging Quantity"
        # compute='_compute_product_packaging_qty',
        # store=True, readonly=False, precompute=True
        )
    out_product_qty = fields.Float(string='Quantity Output',
        compute='_compute_output_product_qty', store=True, readonly=False, precompute=True)
    out_product_scrap_qty = fields.Float(string='Quantity Scrap',
        compute='_compute_output_product_qty', store=True, readonly=False, precompute=True)
    
    product_tmpl_id = fields.Many2one('product.template', string='Product Template',
        related='product_id.product_tmpl_id')

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            line.product_uom = line.product_id.uom_id.id
    
    @api.depends('product_id', 'product_qty', 'product_uom')
    def _compute_product_packaging_id(self):
        for line in self:
            # remove packaging if not match the product
            if line.product_packaging_id.product_id != line.product_id:
                line.product_packaging_id = False
            # suggest biggest suitable packaging matching the SO's company
            if line.product_id and line.product_qty and line.product_uom:
                suggested_packaging = line.product_id.packaging_ids\
                        .filtered(lambda p: p.sales and p.is_pisang and (p.product_id.company_id <= p.company_id <= line.company_id))\
                        .with_context(ripening=True)._find_suitable_product_packaging(line.product_qty, line.product_uom)
                line.product_packaging_id = suggested_packaging or line.product_packaging_id
    
    @api.depends('product_packaging_id', 'product_uom', 'product_qty', 'product_packaging_qty')
    def _compute_output_product_qty(self):
        for line in self:
            if not line.product_packaging_id or not line.product_packaging_qty:
                line.out_product_qty = 0.0
                line.out_product_scrap_qty = 0.0
            else:
                packaging_uom = line.product_packaging_id.product_uom_id
                # packaging_uom_qty = line.product_uom._compute_quantity(line.product_qty, packaging_uom)
                out_product_qty_with_scrap = float_round(
                    line.product_packaging_qty * (line.product_packaging_id.qty + line.product_packaging_id.scrap_qty),
                    precision_rounding=packaging_uom.rounding)
                line.out_product_qty = out_product_qty_with_scrap - (line.product_packaging_id.scrap_qty * line.product_packaging_qty)
                line.out_product_scrap_qty = out_product_qty_with_scrap - line.out_product_qty

    # @api.depends('product_packaging_id', 'product_uom', 'product_uom_qty')
    # def _compute_product_packaging_qty(self):
    #     for line in self:
    #         if not line.product_packaging_id:
    #             line.product_packaging_qty = False
    #         else:
    #             packaging_uom = line.product_packaging_id.product_uom_id
    #             packaging_uom_qty = line.product_uom._compute_quantity(line.product_uom_qty, packaging_uom)
    #             line.product_packaging_qty = float_round(
    #                 packaging_uom_qty / line.product_packaging_id.qty,
    #                 precision_rounding=packaging_uom.rounding)
    
    def _prepare_move_line_vals(self):
        self.ensure_one()
        return {
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.out_product_qty,
            # 'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_id': self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id,
            'location_dest_id': self.env.ref('ny_plantation.loc_ripening_loc_1').id,
        }

class StockRipeningPisang(models.Model):
    _name = 'stock.ripening.pisang'
    _description = 'Ripening Pisang'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date asc, id desc"

    name = fields.Char('No.', readonly=True)
    date = fields.Date(default=fields.Date.context_today, string="Creation Date")
    date_done = fields.Datetime(string="Date of Transfer")
    partner_id = fields.Many2one('res.partner', string='Transfer To')
    note = fields.Text('Note')

    line_ids = fields.One2many('stock.ripening.pisang.line', 'ripening_id', string='Operations')
    picking_ids = fields.Many2many('stock.picking', 'ripening_picking_rel', string='Internal Transfers')
    scrap_ids = fields.Many2many('stock.scrap', 'ripening_scrap_rel', string='Scraps')

    state = fields.Selection([('draft','New'),('confirm','Confirm'),('done','Done')], string='Status', default='draft')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockRipeningPisang, self).create(vals_list)
        return res
    
    def unlink(self):
        for rec in self:
            if rec.state!='draft':
                raise UserError("Tidak dapat menghapus Transaksi yang tidak berstatus New")
        return super(StockRipeningPisang, self).unlink()
    
    def _prepare_move_lines(self):
        self.ensure_one()
        res = []
        for line in self.line_ids:
            res.append((0,0,line._prepare_move_line_vals()))
        return res
    
    def _prepare_scrap_lines(self, picking):
        self.ensure_one()
        res = []
        for line in self.line_ids:
            res.append({
                'product_id': line.product_id.id,
                'scrap_qty': line.out_product_scrap_qty,
                # 'location_id': picking.location_dest_id.id,
                # 'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_id': self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id,
                'scrap_location_id': self.env['stock.location'].search([('scrap_location','=',True)], limit=1).id,
                'picking_id': picking.id,
            })
        return res

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_validate(self):
        for rec in self:
            # Create Internal Transfer
            picking_type = self.env.ref('ny_plantation.picking_type_ripening_1')
            move_lines = rec._prepare_move_lines()
            int_picking_vals = {
                'picking_type_id': picking_type.id,
                'move_ids': move_lines
            } 
            picking = self.env['stock.picking'].create(int_picking_vals)
            picking.action_confirm()
            picking.action_assign()
            if picking.state=='assigned':
                # picking.move_ids.action_done()
                picking.action_set_quantities_to_reservation()
                picking.button_validate()
            rec.picking_ids = [(6,0,picking.ids)]
            # Create Scrap
            scrap_to_create = rec._prepare_scrap_lines(picking)
            scrap_datas = self.env['stock.scrap'].create(scrap_to_create)
            for scrap_data in scrap_datas:
                scrap_data.action_validate()
            rec.scrap_ids = [(6,0,scrap_datas.ids)]
            rec.state = 'done'
            rec.date_done = picking.date_done
            rec.name = picking.name
    
    def action_view_pickings(self):
        # stock_picking_action_picking_type
        # action_picking_form
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_picking_action_picking_type")
        if len(self.picking_ids.ids)>1:
            domain = [('id','in',self.picking_ids.ids)]
        elif len(self.picking_ids.ids)==1:
            domain = [('id','=',self.picking_ids.id)]
            action['views'] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action['res_id'] = self.picking_ids.id
        else:
            domain = [('id','=',0)]
        action['domain'] = domain
        return action

    def action_view_scraps(self):
        # stock.stock_scrap_form_view
        # stock.action_stock_scrap
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        if len(self.scrap_ids.ids)>1:
            domain = [('id','in',self.scrap_ids.ids)]
        elif len(self.scrap_ids.ids)==1:
            domain = [('id','=',self.scrap_ids.id)]
            action['views'] = [(self.env.ref("stock.stock_scrap_form_view").id, "form")]
            action['res_id'] = self.scrap_ids.id
        else:
            domain = [('id','=',0)]
        action['domain'] = domain
        return action