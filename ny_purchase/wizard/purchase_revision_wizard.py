from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PurchaseRevisionWizard(models.TransientModel):
    _name = 'purchase.revision.wizard'
    _description = 'Wizard to Purchase Revision Number'

    purchase_id = fields.Many2one('purchase.order', string="Purchase Order", required=True, readonly=True)
    current_revision = fields.Integer(string="Revisi Sekarang", readonly=True)
    new_revision = fields.Integer(string="Masukkan Revisi Ke Berapa", required=True)

    def purchase_revision(self):
        if self.new_revision < 0:
            raise UserError(_('Revisi tidak boleh negatif.'))
        self.purchase_id.write({
            'revision_number': self.new_revision,
            'name': f"{self.purchase_id.name.split('/Rev/')[0]}/Rev/{self.new_revision}",
        })

    # def close_wizard(self):
    #     self.purchase_id.write({'state': self.purchase_id.state})
    #     return {'type': 'ir.actions.act_window_close'}