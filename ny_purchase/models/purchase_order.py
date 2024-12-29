from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    non_credit = fields.Boolean('Non Credit')

    def button_confirm(self):
        if any(line.price_unit == 0.0 for line in self.order_line):
            return {
                'name': 'Peringatan!',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.confirm.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_purchase_order_id': self.id},
            }
        return super(PurchaseOrder, self).button_confirm()
    

    revision_number = fields.Integer(string="Revision Number", default=0, readonly=True)

    @api.model
    def create(self, vals):
        if 'name' not in vals or not vals['name']:
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or 'New'
        vals['name'] = f"{vals['name']}/Rev/0"
        return super(PurchaseOrder, self).create(vals)

    def write(self, vals):
        if 'revision_number' in vals:
            for record in self:
                vals['name'] = f"{record.name.split('/Rev/')[0]}/Rev/{vals['revision_number']}"
        return super(PurchaseOrder, self).write(vals)

    def increment_revision(self):
        for record in self:
            record.revision_number += 1
            record.name = f"{record.name.split('/Rev/')[0]}/Rev/{record.revision_number}"

    def button_cancel(self):
        super(PurchaseOrder, self).button_cancel()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Revision Number'),
            'res_model': 'purchase.revision.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_id': self.id,
                'default_current_revision': self.revision_number,
            },
        }
