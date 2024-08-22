# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import ValidationError, UserError

class MaterialRequest(models.Model):
    _name = "material.request"
    _description = "Material Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_request desc, id desc"

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "issue"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "issue"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    name = fields.Char(string="Number")
    date_request = fields.Date(string="Date of Request", default=fields.Date.context_today)
    requested_by = fields.Many2one("res.users", string="Requested by", 
        default=lambda s: s.env.uid, tracking=True, index=True,
    )
    description = fields.Text(string="Description")
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False)
    picking_type_id = fields.Many2one("stock.picking.type", string="Picking Type",
        default=_default_picking_type, domain=[('code','=','issue')])
    location_id = fields.Many2one('stock.location', related='picking_type_id.default_location_src_id', string='Location')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'), 
        ('approved', 'Approved'), 
        ('done', 'Closed'), 
        ('reject', 'Rejected'), 
        ('cancel', 'Cancel')], default="draft", tracking=True)
    issue_state = fields.Selection([('no', 'Nothing To Issue'), 
        ('to_issue', 'To Issue'),
        ('partial', 'Partially Issued'),
        ('issued', 'Fully Issued')], compute='_issue_status', compute_sudo=True, 
        string='Issue Status', store=True)
    allow_force_close = fields.Boolean(compute='_issue_status', compute_sudo=True, 
        string='Allow Force Close', store=True)
    line_ids = fields.One2many("material.request.line", "mr_id", string="Lines")
    company_id = fields.Many2one("res.company", string="Company", 
        default=lambda s: s.env.company.id, tracking=True,
    )
    picking_count = fields.Integer(compute='_picking_count', compute_sudo=True, 
        string="# Pickings")

    def _picking_count(self):
        for request in self:
            request.picking_count = len(request.line_ids.mapped('move_ids.picking_id').ids)

    @api.depends('state', 'line_ids.qty_done', 'line_ids.qty_to_issue')
    def _issue_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for request in self:
            if request.state not in ('approved','done'):
                request.issue_state = 'no'
                continue

            if any(not float_is_zero(line.qty_to_issue, precision_digits=precision)
                    for line in request.line_ids):
                if any(not float_is_zero(line.qty_done, precision_digits=precision)
                        for line in request.line_ids):
                    request.allow_force_close = True
                    request.issue_state = 'partial'
                else:
                    request.issue_state = 'to_issue'
            elif all(float_is_zero(line.qty_to_issue, precision_digits=precision)
                    for line in request.line_ids):
                if any(line.qty_done<line.product_qty for line in request.line_ids):
                    request.issue_state = 'partial'
                else:
                    request.issue_state = 'issued'
                request.allow_force_close = False
            else:
                request.issue_state = 'no'

    ##########################
    #      HELPER METHOD     #
    ##########################
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.requested_by.partner_id.id
            })
        if not self.picking_type_id.default_location_dest_id.id:
            raise UserError(_("You must set an Internal Issue Location for this Operation Type %s", self.picking_type_id.name))
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': False,
            'user_id': False,
            'date': self.date_request,
            'origin': self.name,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'company_id': self.company_id.id,
            'skb' : True
        }

    def unlink(self):
        for request in self:
            if not request.state == 'cancel':
                raise UserError(_('In order to delete a material request, you must cancel it first.'))
        return super(MaterialRequest, self).unlink()

    ##########################
    #     BUSINESS METHOD    #
    ##########################
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for request in self.filtered(lambda mr: mr.state=='approved'):
            if any(product.type=='product' for product in request.line_ids.product_id):
                request = request.with_company(request.company_id)
                res = request._prepare_picking()
                picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                moves = request.line_ids._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                # print("----------------", moves)
                # print("---------------", stop) stoper nya pun gk berfungsi, bukan fungsi ini yg berjalan (note from cimol)
                # moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': request},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True


    def action_submit(self):
        for request in self:
            if request.state!='draft':
                raise ValidationError(_('You cannot Submit request that is not in Draft state'))
            request.name = self.env['ir.sequence'].next_by_code(self._name)
            request.state="submit"

    def action_approved(self):
        for request in self:
            if request.state!='submit':
                raise ValidationError(_('You cannot Approve request that is not in Submitted state'))
            request.state="approved"
            request._create_picking()

    def action_done(self):
        for request in self:
            if request.state!='approved':
                raise ValidationError(_('You cannot set Done request that is not in Approved State'))
            request.state="done"

    def force_close(self):
        for request in self:
            open_pickings = request.line_ids.mapped('move_ids.picking_id').filtered(lambda p: p.state not in ('done','cancel'))
            if open_pickings:
                open_pickings.action_cancel()
            force_close_msg = """ Hello """ + request.requested_by.name + """,""" + """
                          <br/>
                          <br/>
                          Your material request number """ + request.name + """ 
                          has been forcebly closed by """ + self.env.user.name
            request.message_post(body=force_close_msg)
        self.action_done()

    def action_reject(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for request in self:
            if any(not float_is_zero(line.qty_done, precision_digits=precision)
                    for line in request.line_ids):
                raise ValidationError(_('You cannot reject Material Request which have been Issued. Please Close it instead or Force it to be Closed'))
            request.state="reject"

    def action_cancel(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for request in self:
            if any(not float_is_zero(line.qty_done, precision_digits=precision)
                    for line in request.line_ids):
                raise ValidationError(_('You cannot cancel Material Request which have been Issued. Please Close it instead or Force it to be Closed'))
            open_pickings = request.line_ids.mapped('move_ids.picking_id').filtered(lambda p: p.state not in ('done','cancel'))
            if open_pickings:
                open_pickings.action_cancel()
            request.state="cancel"

    def action_draft(self):
        self.state="draft"

    def action_open_picking(self):
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        pickings = self.line_ids.mapped('move_ids.picking_id')
        if len(pickings) > 1:
            result['domain'] = "[('id','in',%s)]" % (pickings.ids)
        elif len(pickings)==1:
            result['domain'] = "[('id','=',%s)]" % (pickings.id)
        return result

class MaterialRequestLine(models.Model):
    _name = "material.request.line"
    _description = "Material Request Line"

    mr_id = fields.Many2one("material.request", string="Material Request", ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product", ondelete="restrict")
    name = fields.Char(string="Description")
    product_qty = fields.Float(string="Qty Demand")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    qty_available = fields.Float(compute='_compute_available', compute_sudo=True, 
        string='Availability')
    qty_issued_method = fields.Selection([('manual', 'Manual')], compute='_compute_qty_issued_method', 
        compute_sudo=True, string='Issue Method', store=True)
    qty_done = fields.Float(compute='_compute_qty_issued', inverse='_inverse_qty_issued', string="Qty Done", 
        digits='Product Unit of Measure', compute_sudo=True, store=True)
    qty_done_manual = fields.Float("Manual Issued Qty", digits='Product Unit of Measure', copy=False)
    qty_to_issue = fields.Float(compute='_compute_qty_to_issue', string="Qty to Issue", 
        compute_sudo=True, store=True)
    move_ids = fields.One2many('stock.move', 'mr_line_id', string='Stock Moves')

    @api.depends('product_id')
    def _compute_qty_issued_method(self):
        for line in self:
            if line.product_id and line.product_id.type!='product':
                line.qty_issued_method = 'manual'
            else:
                line.qty_issued_method = False

    def _compute_available(self):
        for line in self:
            if not line.mr_id.location_id or not line.product_id:
                line.qty_available = 0.0
            else:
                line.qty_available = line.product_id.with_context(location_id=line.mr_id.location_id).qty_available


    
    @api.depends(
        'product_id', 
        'product_qty', 
        'uom_id',
        'mr_id.state', 
        'move_ids.state')
    def _compute_qty_issued(self):
        for line in self:
            qty_done = qty_to_issue = 0.0
            if line.mr_id.state not in ('approved','done'):
                line.qty_done = qty_done
                line.qty_to_issue = qty_to_issue
                continue
            if line.product_id.type=='product':
                for move in line.move_ids.filtered(lambda m:m.state=='done'):
                    if move.location_id.usage=='internal' and move.location_dest_id.usage!='internal':
                        qty_done += move.product_uom._compute_quantity(move.product_uom_qty, line.uom_id)
                    elif move.location_id.usage!='internal' and move.location_dest_id.usage=='internal':
                        qty_done -= move.product_uom._compute_quantity(move.product_uom_qty, line.uom_id)
            else:
                qty_done = line.qty_done_manual or 0.0
            line.qty_done = qty_done
    
    @api.depends('qty_done', 'mr_id.state', 'move_ids.state')
    def _compute_qty_to_issue(self):
        for line in self:
            if line.mr_id.state!='approved':
                line.qty_to_issue = 0.0
                continue
            qty_to_issue = line.product_qty - line.qty_done
            line.qty_to_issue = qty_to_issue if qty_to_issue > 0.0 else 0.0

    @api.onchange('qty_done')
    def _inverse_qty_issued(self):
        """ When writing on qty_received, if the value should be modify manually (`qty_received_method` = 'manual' only),
            then we put the value in `qty_received_manual`. Otherwise, `qty_received_manual` should be False since the
            received qty is automatically compute by other mecanisms.
        """
        for line in self:
            if line.product_id.type != 'product':
                line.qty_done_manual = line.qty_done
            else:
                line.qty_done_manual = 0.0

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.name = self.product_id.name
            self.uom_id = self.product_id.uom_id.id
        else:
            self.name = False
            self.uom_id = False
        self._compute_available()

    def _prepare_stock_move_vals(self, picking, product_uom_qty, product_uom):
        self.ensure_one()
        # print("----------------", self)
        # print("----------------", disinidatanya)
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            # 'requested_by' : self.mr_id.requested_by,
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': self.mr_id.date_request,
            # 'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
            'location_id': self.mr_id.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.mr_id.picking_type_id.default_location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': False,
            'state': 'draft',
            'mr_line_id': self.id,
            'company_id': self.mr_id.company_id.id,
            'price_unit': False,
            'picking_type_id': self.mr_id.picking_type_id.id,
            'group_id': self.mr_id.group_id.id,
            'origin': self.mr_id.name,
            'description_picking': self.name,
            # 'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.mr_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
        }

    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            if line.product_id.type!='product':
                continue
            if float_compare(line.product_qty, 0.0, precision_rounding=self.uom_id.rounding) > 0:
                product_uom_qty, product_uom = line.uom_id._adjust_uom_quantities(self.product_qty, self.product_id.uom_id)
                values.append(self._prepare_stock_move_vals(picking, product_uom_qty, product_uom))
                # print("----------------", values)
                # print("----------------", disinidatanya)
        return self.env['stock.move'].create(values)

    def unlink(self):
        for line in self:
            if line.mr_id.state!='cancel':
                raise UserError(_('Cannot delete a material request line which is in state \'%s\'.') % (line.mr_id.state,))
        return super(MaterialRequestLine, self).unlink()