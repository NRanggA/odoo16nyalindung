from odoo import fields, models, api, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import UserError, ValidationError


class PurcahaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_received = fields.Char(compute='_compute_product_is_received', string='Is Received')

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_product_is_received(self):
        for record in self:
            has_received = any(record.picking_ids and record.picking_ids.filtered(lambda xx:xx.state == 'done'))
            record.is_received = bool(has_received)

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
            'partner_id': self.partner_id.id,
            'partner_ref': self.partner_ref,
        }
        return result

    def action_create_equipment_register(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        EquipmentRegister = self.env['equipment.register']
        registers = self.env['equipment.register']
        
        for order in self:
            order = order.with_company(order.company_id)
            
            for line in order.order_line.filtered(lambda l: l.product_id and l.product_id.product_asset):
                for qty in range(int(order.order_line.product_qty)):
                    if not float_is_zero(line.qty_to_equip_register, precision_digits=precision):
                        register_vals = order._prepare_equipment_register()
                        register_vals['register_line_ids'] = [(0, 0, line._prepare_equipment_register_line())]
                        
                        registers |= EquipmentRegister.with_company(register_vals['company_id']).create(register_vals)
        
        if not registers:
            raise UserError(_('There is not receiveable lines. You must receive the product before registering it into Equipment'))
        
        return self.action_view_equipment_register(registers)
    
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_equipment_register_line(self):
        self.ensure_one()
        result = {
            'product_id': self.product_id.id,
            'product_qty': 1,
            'name': self.name,
            'product_uom': self.product_id.uom_id.id,
            'purchase_line_id': self.id
        }
        return result
        
