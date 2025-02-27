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
        if '/Rev.' not in vals['name']:
            vals['name'] = f"{vals['name']}/Rev.0"
        return super(PurchaseOrder, self).create(vals)

    def write(self, vals):
        if 'revision_number' in vals:
            for record in self:
                vals['name'] = f"{record.name.split('/Rev.')[0]}/Rev.{vals['revision_number']}"
        return super(PurchaseOrder, self).write(vals)

    def increment_revision(self):
        for record in self:
            record.revision_number += 1
            record.name = f"{record.name.split('/Rev.')[0]}/Rev.{record.revision_number}"

    # def button_cancel(self):
    #     super(PurchaseOrder, self).button_cancel()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Purchase Revision Number'),
    #         'res_model': 'purchase.revision.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_purchase_id': self.id,
    #             'default_current_revision': self.revision_number,
    #         },
    #     }

    def open_revision_wizard(self):
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

    # def create_revision(self, new_revision_number):
    #     for record in self:
    #         record.button_cancel()
    #         new_name = f"{record.name.split('/Rev.')[0]}/Rev.{new_revision_number}"
    #         new_vals = record.copy_data()[0]
    #         new_vals.update({
    #             'name': new_name,
    #             'revision_number': new_revision_number,
    #             'state': 'draft',
    #         })
    #         new_po = self.create(new_vals)
    #         # record.write({'state': 'cancel'})
    #     return new_po

    def create_revision(self):
        for record in self:
            new_revision_number = record.revision_number + 1
            new_name = f"{record.name.split('/Rev.')[0]}/Rev.{new_revision_number}"
            new_vals = record.copy_data()[0]
            new_vals.update({
                'name': new_name,
                'revision_number': new_revision_number,
                'state': 'draft',
            })
            new_po = self.create(new_vals)
            record.button_cancel()
            return new_po

    def action_create_invoice(self):
        res = super().action_create_invoice()
        for order in self:
            if order.non_credit:
                move = self.env['account.move'].search([('invoice_origin', '=', order.name)], order='id desc', limit=1)
                if move:
                    total_ppn_value = 0.0
                    account_id = False

                    for line in order.order_line:
                        ppn_taxes = line.taxes_id.filtered(lambda tax: 'PPN' in tax.name)

                        if ppn_taxes:
                            ppn_amount = sum(ppn_taxes.mapped('amount')) / 100
                            qty = line.qty_to_invoice if line.qty_to_invoice > 0 else line.product_qty
                            ppn_value = line.price_unit * ppn_amount * qty

                            if not account_id:
                                move_line = move.line_ids.filtered(lambda l: l.purchase_line_id == line)
                                account_id = move_line.account_id.id if move_line else False

                            total_ppn_value += ppn_value

                    if total_ppn_value > 0 and account_id:
                        ppn_line_vals = {
                            'display_type': 'product',
                            'name': 'PPN Tidak di kreditkan',
                            'product_id': False,
                            'product_uom_id': False,
                            'quantity': 1,
                            'price_unit': total_ppn_value,
                            'account_id': account_id,
                            'tax_ids': [],
                            'move_id': move.id,
                        }
                        self.env['account.move.line'].create(ppn_line_vals)

        return res