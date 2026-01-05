from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.tools.misc import OrderedSet
from odoo.tools.float_utils import float_is_zero

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    non_credit = fields.Boolean('Non Credit')
    termin_pembayaran = fields.Char('Termin Pembayaran')

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

    pr_names = fields.Char(
        string="Purchase Request",
        compute="_compute_pr_names",
        store=True)

    @api.depends('order_line.purchase_request_lines.request_id')
    def _compute_pr_names(self):
        for po in self:
            pr_names = set()
            for line in po.order_line:
                for pr_line in line.purchase_request_lines:
                    if pr_line.request_id:
                        pr_names.add(pr_line.request_id.name)
            po.pr_names = ', '.join(sorted(pr_names))

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
    

    # Override button cancel jika sudah di return bisa di cancel / qty_recived sudah 0 maka akan bisa di cancel
    def button_cancel(self):
        order_lines_ids = OrderedSet()
        pickings_to_cancel_ids = OrderedSet()
        for order in self:
            # Bawaan Odoo
            # for move in order.order_line.mapped('move_ids'):
            #     if move.state == 'done':
            #         raise UserError(_('Unable to cancel purchase order %s as some receptions have already been done.') % (order.name))

            #Cek Received Qty == 0
            for line in order.order_line:
                if any(move.state == 'done' for move in line.move_ids):
                    if not float_is_zero(line.qty_received, precision_rounding=line.product_uom.rounding):
                        raise UserError(_('Cannot cancel PO %s: Items already received.') % order.name)

            #Cek Vendor Bill harus cancelled
            bills = order.invoice_ids.filtered(lambda x: x.move_type in ['in_invoice', 'in_refund'])
            if any(bill.state not in ['cancel', 'draft'] for bill in bills):
                raise UserError(_('Cannot cancel PO %s: Vendor bill is still active or posted.') % order.name)

            # Cek Advance harus cancelled
            advances = order.advanced_vendor_move_ids.filtered(lambda move: move.is_advanced)
            if any(move.state != 'cancel' for move in advances):
                raise UserError(_('Cannot cancel PO %s: There are advance payments that are not cancelled.') % order.name)

            # If the product is MTO, change the procure_method of the closest move to purchase to MTS.
            # The purpose is to link the po that the user will manually generate to the existing moves's chain.
            if order.state in ('draft', 'sent', 'to approve', 'purchase'):
                order_lines_ids.update(order.order_line.ids)

            pickings_to_cancel_ids.update(order.picking_ids.filtered(lambda r: r.state not in  ['done', 'cancel']).ids)

        order_lines = self.env['purchase.order.line'].browse(order_lines_ids)

        moves_to_cancel_ids = OrderedSet()
        moves_to_recompute_ids = OrderedSet()
        for order_line in order_lines:
            # moves_to_cancel_ids.update(order_line.move_ids.ids)

            # Override dari fungsi odoo agar tidak memasukkan semua move_ids nya
            valid_moves = order_line.move_ids.filtered(lambda move: move.state not in ['done', 'cancel'])
            moves_to_cancel_ids.update(valid_moves.ids)
            if order_line.move_dest_ids:
                move_dest_ids = order_line.move_dest_ids.filtered(lambda move: move.state != 'done' and not move.scrapped)
                if order_line.propagate_cancel:
                    moves_to_cancel_ids.update(move_dest_ids.ids)
                else:
                    moves_to_recompute_ids.update(move_dest_ids.ids)


        if moves_to_cancel_ids:
            moves_to_cancel = self.env['stock.move'].browse(moves_to_cancel_ids)
            moves_to_cancel._action_cancel()

        if moves_to_recompute_ids:
            moves_to_recompute = self.env['stock.move'].browse(moves_to_recompute_ids)
            moves_to_recompute.write({'procure_method': 'make_to_stock'})
            moves_to_recompute._recompute_state()

        if pickings_to_cancel_ids:
            pikings_to_cancel = self.env['stock.picking'].browse(pickings_to_cancel_ids)
            pikings_to_cancel.action_cancel()

        if order_lines:
            order_lines.write({'move_dest_ids': [(5, 0, 0)]})

        self.write({'state': 'cancel', 'mail_reminder_confirmed': False})
        # return super(PurchaseOrder, self).button_cancel()