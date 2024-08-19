from odoo import models, fields, api, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    code = fields.Selection(selection_add=[('issue', 'Issue Product')], 
                ondelete={'issue': 'cascade'})

    @api.onchange('code')
    def _onchange_picking_code(self):
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
        stock_location = warehouse.lot_stock_id
        self.show_operations = self.code != 'incoming' and self.user_has_groups(
            'stock.group_production_lot,'
            'stock.group_stock_multi_locations,'
            'stock.group_tracking_lot'
        )
        if self.code == 'incoming':
            self.default_location_src_id = self.env.ref('stock.stock_location_suppliers').id
            self.default_location_dest_id = stock_location.id
        elif self.code == 'outgoing':
            self.default_location_src_id = stock_location.id
            self.default_location_dest_id = self.env.ref('stock.stock_location_customers').id
        elif self.code == 'issue':
            self.default_location_src_id = stock_location.id
            self.default_location_dest_id = self.env.ref('c10i_material_request.stock_location_internal_consumption').id
        elif self.code == 'internal' and not self.user_has_groups('stock.group_stock_multi_locations'):
            return {
                'warning': {
                    'message': _('You need to activate storage locations to be able to do internal operation types.')
                }
            }