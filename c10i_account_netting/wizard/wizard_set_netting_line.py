from odoo import api, fields, models

class WizardSetNettingLine(models.TransientModel):
    _name = 'wizard.set.netting.line'
    _description = 'Add Netting Line'

    netting_id = fields.Many2one('account.netting', string='Netting', required=True)
    # type = fields.Selection([('src', 'Source'), ('dest', 'Destination')], string='Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer/Vendor', readonly=True)
    move_line_ids = fields.Many2many(
        'account.move.line',
        string='Unreconciled Move Lines',
        domain="[('partner_id', '=', partner_id), ('reconciled', '=', False), ('account_id.reconcile', '=', True)]"
    )

    def action_add_lines(self):
        self.ensure_one()
        line_to_add = []
        for move_line in self.move_line_ids:
            line_to_add.append((0, 0, {
                'move_line_id': move_line.id,
                'amount_residual': move_line.amount_residual,
            }))
        self.netting_id.line_ids = line_to_add
        # if self.type=='src':
        #     self.netting_id.src_line_ids = line_to_add
        # else:
        #     self.netting_id.dest_line_ids = line_to_add
        return {'type': 'ir.actions.act_window_close'}