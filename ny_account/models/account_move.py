from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer/Vendor",
        store=True, readonly=False, ondelete='restrict',
        compute='_compute_partner_id',
        tracking=True,
        check_company=True)

    @api.onchange('partner_id')
    def _compute_partner_id(self):
        for rec in self:
            if rec.move_type == 'out_invoice':
                return {'domain': {'partner_id': [('customer_category', '=', True)]}}

            if rec.move_type == 'in_invoice':
                return {'domain': {'partner_id': [('vendor_category', '=', True)]}}

    def _must_check_constrains_date_sequence(self):
        
        if self.journal_id.type in ['bank', 'cash']:
            return False
        
        return super(AccountMove, self)._must_check_constrains_date_sequence()
    
    def action_post(self):
        for rec in self:
            if rec.move_type == 'out_invoice':
                if not rec.env.context.get('from_wizard'):
                    confirmation_message = "Apakah anda ingin mengenerate : %s?" % rec.journal_id.name
                    return {
                        'type'      : 'ir.actions.act_window',
                        'res_model' : 'wizard.action.confirm.invoice',
                        'view_mode' : 'form',
                        'view_id'   : self.env.ref('ny_account.view_wizard_action_confirm_invoice').id,
                        'target'    : 'new',
                        'context': {
                            'active_id'             : rec.id, 
                            'active_model'          : rec._name,
                            'confirmation_message'  : confirmation_message  
                        },
                    }
                
                if self.journal_id.is_org:    
                    if not self.journal_id.varieties_id:
                        raise ValidationError(f"Journal yang anda pilih [{self.journal_id.name}] tidak memiliki ORG, silahkan isi terlebih dahulu!.")
                    
                    for line in rec.invoice_line_ids:
                        line.plantation_varieties_id = self.journal_id.varieties_id.id

        return super(AccountMove, self).action_post()