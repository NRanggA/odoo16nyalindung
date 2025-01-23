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
    # picking_ids = fields.Many2many('stock.picking', 'ripening_picking_rel', string='Internal Transfers')
    # scrap_ids = fields.Many2many('stock.scrap', 'ripening_scrap_rel', string='Scraps')

    state = fields.Selection([('draft','New'), ('cancel','Cancel'),('confirm','Confirm'),('done','Done')], string='Status', default='draft')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    stock_picking_repening_count = fields.Integer("Stock Picking Repeing Count", compute='_compute_stock_picking_repening_count')
    stock_picking_return_scrap_count = fields.Integer("Stock Picking Return Scrap Count", compute='_compute_stock_picking_return_scrap_count')
    stock_scrap_count = fields.Integer("Stock Scrap Count", compute='_compute_stock_scrap_count')

    has_qty_scrap = fields.Boolean(
        string="Has Scrap Quantity", 
        compute="_compute_has_qty_scrap", 
        store=True,
    )

    @api.depends('line_ids.qty_scrap')
    def _compute_has_qty_scrap(self):
        for record in self:
            record.has_qty_scrap = any(line.qty_scrap > 0 for line in record.line_ids)


    @api.depends('line_ids.stock_move_ids')
    def _compute_stock_picking_repening_count(self):
        for rec in self:
            rec.stock_picking_repening_count = len(rec.line_ids.stock_move_ids.picking_id.ids)
    
    @api.depends('line_ids.return_scarp_ids')
    def _compute_stock_picking_return_scrap_count(self):
        for rec in self:
            rec.stock_picking_return_scrap_count = len(rec.line_ids.return_scarp_ids.picking_id.ids)
    
    @api.depends('line_ids.scrap_ids')
    def _compute_stock_scrap_count(self):
        for rec in self:
            rec.stock_scrap_count = len(rec.line_ids.scrap_ids.ids)

    # def action_cancel(self):
    #     for record in self:
    #         if any(line.qty_received > 0 for line in record.line_ids) or any(line.qty_scrap > 0 for line in record.line_ids):
    #             error_message = (
    #                 "Anda tidak bisa membatalkan dokumen ini karena terdapat {} yang sudah diproses / status dokumen tidak Draft. "
    #                 "Silahkan return {} terlebih dahulu."
    #             )
    #             if any(line.qty_received > 0 for line in record.line_ids):
    #                 raise ValidationError(error_message.format('Receipt', 'receipt'))
    #             if any(line.qty_scrap > 0 for line in record.line_ids):
    #                 raise ValidationError(error_message.format('Scrap', 'scrap'))
            
    #         record.state = 'cancel'

    def _validate_cancel(self):
        for record in self:
            processed_lines = [
                line for line in record.line_ids if line.qty_received > 0 or line.qty_scrap > 0
            ]
            if processed_lines:
                products = ", ".join([line.product_id.name for line in processed_lines])
                raise ValidationError((
                    "Dokumen tidak dapat dibatalkan karena produk berikut sudah diproses:\n{}.\n"
                    "Silakan selesaikan atau return proses terkait sebelum membatalkan."
                ).format(products))

    def action_cancel(self):
        self._validate_cancel()
        self.write({'state': 'cancel'})

    def action_draft(self):
        for rec in self:
            rec.state = 'draft' 

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockRipeningPisang, self).create(vals_list)
        return res
    
    def unlink(self):
        for rec in self:
            if rec.state!='draft':
                raise UserError("Tidak dapat menghapus Transaksi yang tidak berstatus New")
        return super(StockRipeningPisang, self).unlink()
    
    # Repening
    def _prepare_move_lines(self):
        self.ensure_one()
        res = []
        for line in self.line_ids:
            res.append((0,0,line._prepare_move_line_vals()))
        return res
    
    # Scrap
    def _prepare_move_line_scraps(self):
        self.ensure_one()
        res = []
        for line in self.line_ids:
            res.append((0,0,line._prepare_move_line_scrap_vals()))
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
                ##
                'repening_line_id': line.id,
            })
        
        return res

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def create_return_scrap(self):
        for rec in self:
            move_line_vals = rec._prepare_move_line_scraps()
            
            picking_vals = {
                'picking_type_id': self.env.ref('ny_plantation.picking_type_scrap_1').id,
                'move_ids': move_line_vals,
            }
            picking = self.env['stock.picking'].create(picking_vals)
            
            if picking.state == 'assigned':
                picking.action_set_quantities_to_reservation()

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
            # picking.action_confirm()
            # picking.action_assign()
            if picking.state=='assigned':
                # picking.move_ids.action_done()
                picking.action_set_quantities_to_reservation()
                # picking.button_validate()
            # rec.picking_ids = [(6,0,picking.ids)]
            # Create Scrap
            scrap_to_create = rec._prepare_scrap_lines(picking)
            scrap_datas = self.env['stock.scrap'].create(scrap_to_create)
            # for scrap_data in scrap_datas:
                # scrap_data.action_validate()
            # rec.scrap_ids = [(6,0,scrap_datas.ids)]
            rec.state = 'done'
            rec.date_done = picking.date_done
            rec.name = picking.name
    
    def action_view_pickings(self):
        # stock_picking_action_picking_type
        # action_picking_form
        for rec in self:
            for line in rec.line_ids:
                action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_picking_action_picking_type")
                if len(line.stock_move_ids.picking_id.ids)>1:
                    domain = [('id','in',line.stock_move_ids.picking_id.ids)]
                elif len(line.stock_move_ids.ids)==1:
                    domain = [('id','=',line.stock_move_ids.picking_id.id)]
                    action['views'] = [(self.env.ref("stock.view_picking_form").id, "form")]
                    action['res_id'] = line.stock_move_ids.picking_id.id
                else:
                    domain = [('id','=',0)]
                action['domain'] = domain
                return action
            
    def action_view_return_scrap(self):
        # stock_picking_action_picking_type
        # action_picking_form
        for rec in self:
            for line in rec.line_ids:
                action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_picking_action_picking_type")
                if len(line.return_scarp_ids.picking_id.ids)>1:
                    domain = [('id','in',line.return_scarp_ids.picking_id.ids)]
                elif len(line.return_scarp_ids.ids)==1:
                    domain = [('id','=',line.return_scarp_ids.picking_id.id)]
                    action['views'] = [(self.env.ref("stock.view_picking_form").id, "form")]
                    action['res_id'] = line.return_scarp_ids.picking_id.id
                else:
                    domain = [('id','=',0)]
                action['domain'] = domain
                return action

    def action_view_scraps(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        domain = []
        for rec in self:
            if len(rec.line_ids.scrap_ids.ids) > 1:
                domain.append(('id', 'in', rec.line_ids.scrap_ids.ids))
            elif len(rec.line_ids.scrap_ids.ids) == 1:
                action['views'] = [(self.env.ref("stock.stock_scrap_form_view").id, "form")]
                action['res_id'] = rec.line_ids.scrap_ids.id
                domain = [('id', '=', rec.line_ids.scrap_ids.id)]
            else:
                domain = [('id', '=', 0)]

        action['domain'] = domain
        return action
            

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
    
    stock_move_ids = fields.One2many('stock.move', 'repening_line_id',string='Stock Move')
    qty_received = fields.Float('Qty Repening Received', compute='_compute_qty_received', store=True)

    # Scrap Return
    return_scarp_ids = fields.One2many('stock.move', 'return_scrap_repening_line_id',string='Stock Move Scrap')

    # Scrap Received
    scrap_ids = fields.One2many('stock.scrap', 'repening_line_id',string='Stock Scrap')
    qty_scrap = fields.Float('Qty Scrap Received', compute='_compute_qty_scrap', store=True)


    @api.depends('return_scarp_ids', 'return_scarp_ids.state', 'return_scarp_ids.product_qty', 'scrap_ids', 'scrap_ids.state', 'scrap_ids.scrap_qty')
    def _compute_qty_scrap(self):
        for record in self:
            qty_scrap = 0
            for scrap in record.scrap_ids.filtered(lambda m: m.state == 'done'):
                qty_scrap += scrap.scrap_qty
            
            for move in record.return_scarp_ids.filtered(lambda m: m.state == 'done'):
                if move.location_id.id == self.env['stock.location'].search([('scrap_location','=',True)], limit=1).id and move.location_dest_id.id == self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id:
                    qty_scrap -= move.product_qty
            
            record.qty_scrap = qty_scrap

    @api.depends('stock_move_ids', 'stock_move_ids.state', 'stock_move_ids.product_qty')
    def _compute_qty_received(self):
        for record in self:
            qty_received = 0
            for move in record.stock_move_ids.filtered(lambda m: m.state == 'done'):
                if move.location_id.id == self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id and move.location_dest_id.id == self.env.ref('ny_plantation.loc_ripening_loc_1').id:
                    qty_received += move.product_qty
                elif move.location_id.id == self.env.ref('ny_plantation.loc_ripening_loc_1').id and move.location_dest_id.id == self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id:
                    qty_received -= move.product_qty
            
            record.qty_received = qty_received


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
    
    # Repening
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
            'repening_line_id':self.id,
        }

    # Scraps
    # def _prepare_move_line_scrap_vals(self):
    #     self.ensure_one()
    #     return {
    #         'name': self.product_id.name,
    #         'product_id': self.product_id.id,
    #         'product_uom': self.product_uom.id,
    #         'product_uom_qty': self.out_product_scrap_qty,
    #         # 'location_id': self.env.ref('stock.stock_location_stock').id,
    #         'location_id': self.env['stock.location'].search([('scrap_location','=',True)], limit=1).id,
    #         'location_dest_id': self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id,
    #         'return_scrap_repening_line_id':self.id,
    #     }

    def _prepare_move_line_scrap_vals(self):
        self.ensure_one()
        scrap_location = self.env['stock.location'].search([('scrap_location', '=', True)], limit=1)
        if not scrap_location:
            raise ValueError("Lokasi scrap tidak ditemukan. Tolong periksa lokasi scrap terlebih dahulu.")
        return {
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.out_product_scrap_qty,
            'location_id': scrap_location.id,
            'location_dest_id': self.env.ref('c10i_lhm_v16.loc_stock_kebun_loc_1').id,
            'return_scrap_repening_line_id': self.id,
        }


class StockMove(models.Model):
    _inherit = 'stock.move'

    repening_line_id = fields.Many2one('stock.ripening.pisang.line', string='Ripening')
    return_scrap_repening_line_id = fields.Many2one('stock.ripening.pisang.line', string='Ripening Scrap')


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    repening_line_id = fields.Many2one('stock.ripening.pisang.line', string='Rapening Line')
