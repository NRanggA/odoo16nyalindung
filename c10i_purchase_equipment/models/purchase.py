# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    equipment_register_count = fields.Integer(compute='_equipment_register_count', string='# Equipment', compute_sudo=True)
    equipment_registered_status = fields.Selection([('no','Nothing to Register'),
        ('to_register', 'Need Equipment Register'),
        ('equipment_registered', 'Equipment Registered')], compute='_compute_equip_register_status', compute_sudo=True)

    def _equipment_register_count(self):
        for order in self:
            registers =  self.env['equipment.register.line'].search([('purchase_line_id.order_id','=',order.id)])
            order.equipment_register_count = len(registers.mapped('register_id').ids)

    def _compute_equip_register_status(self):
        for order in self:
            if any(l.equipment_registered_status=='to_register' for l in order.order_line):
                order.equipment_registered_status = 'to_register'
            elif all(l.equipment_registered_status=='equipment_registered' for l in order.order_line):
                order.equipment_registered_status = 'equipment_registered'
            else:
                order.equipment_registered_status = 'no'

    def _prepare_equipment_register(self):
        self.ensure_one()
        lastest_date = False
        for picking in self.picking_ids.filtered(lambda p: p.state=='done'):
            date_done = picking.date_done.strftime('%Y-%m-%d')
            if not lastest_date:
                lastest_date = date_done
            if lastest_date < date_done:
                lastest_date = date_done
        result = {
            'date': lastest_date,
            'origin': self.name,
            'company_id': self.company_id.id,
        }
        return result

    def action_create_equipment_register(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        receipt_vals_list = []
        for order in self:
            order = order.with_company(order.company_id)
            register_lines_list = []
            for line in order.order_line.filtered(lambda l: l.product_id and l.product_id.product_asset):
                if not float_is_zero(line.qty_to_equip_register, precision_digits=precision):
                    register_lines_list.append((0, 0, line._prepare_equipment_register_line()))
            
            if not register_lines_list:
                continue
            
            register_vals = order._prepare_equipment_register()
            register_vals['register_line_ids'] = register_lines_list

            receipt_vals_list.append(register_vals)

        if not receipt_vals_list:
            raise UserError(_('There is not receiveable lines. You must received the product before register it into Equipment'))

        EquipmentRegister =  self.env['equipment.register']
        registers =  self.env['equipment.register']
        for vals in receipt_vals_list:
            registers |= EquipmentRegister.with_company(vals['company_id']).create(vals)
        return self.action_view_equipment_register(registers)

    def action_view_equipment_register(self, registers=False):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_purchase_equipment.action_equipment_register_purchase')
        if not registers:
            register_lines =  self.env['equipment.register.line'].search([('purchase_line_id.order_id','=',self.id)])
            registers = register_lines.mapped('register_id')
        
        if not registers or len(registers) > 1:
            result['domain'] = "[('id','in',%s)]" % (registers.ids)
        elif len(registers) == 1:
            res = self.env.ref('c10i_purchase_equipment.equipment_register_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = registers.id
        return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_to_equip_register = fields.Float(compute='_compute_qty_received_eq', string='To Invoice Quantity', store=True, readonly=True,
                                            digits='Product Unit of Measure', compute_sudo=True)
    qty_registered = fields.Float(compute='_compute_qty_received_eq', string='Qty Registered', store=True, readonly=True,
                                            digits='Product Unit of Measure', compute_sudo=True)
    equipment_registered_status = fields.Selection([('no','Nothing to Register'),
        ('to_register', 'Need Equipment Register'),
        ('equipment_registered','Equipment Registered')], compute='_compute_equipment_register_status', store=True, compute_sudo=True)
    equipment_register_line_ids = fields.One2many('equipment.register.line', 'purchase_line_id', 'Equipment Register Lines')

    @api.depends('qty_received', 'equipment_register_line_ids.product_qty', 'equipment_register_line_ids.state')
    def _compute_qty_received_eq(self):
        for line in self:
            total_registered = 0.0
            if line.product_id.product_asset:
                for lregis in line.equipment_register_line_ids.filtered(lambda l: l.product_id==line.product_id):
                    if lregis.state == 'done':
                        # total_registered = lregis.product_uom._compute_quantity(lregis.product_qty, line.product_uom, rounding_method='HALF-UP')
                        total_registered += lregis.product_uom._compute_quantity(lregis.product_qty, line.product_uom)
                line.qty_registered = total_registered
                line.qty_to_equip_register = line.qty_received - total_registered
            else:
                line.qty_registered = 0.0
                line.qty_to_equip_register = 0.0

    @api.depends('qty_to_equip_register')
    def _compute_equipment_register_status(self):
        for line in self:
            if line.qty_to_equip_register > 0.0:
                line.equipment_registered_status = 'to_register'
            elif line.qty_registered and line.qty_registered==line.qty_to_equip_register:
                line.equipment_registered_status = 'equipment_registered'
            else:
                line.equipment_registered_status = 'no'

    def _prepare_equipment_register_line(self):
        self.ensure_one()
        quantity = self.product_uom._compute_quantity(self.qty_to_equip_register, self.product_id.uom_id)
        result = {
            'product_id': self.product_id.id,
            'product_qty': quantity,
            'name': self.name,
            'product_uom': self.product_id.uom_id.id,
            'purchase_line_id': self.id,
        }
        return result