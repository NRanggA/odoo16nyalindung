from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

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
        return super(AccountMove, self).action_post()