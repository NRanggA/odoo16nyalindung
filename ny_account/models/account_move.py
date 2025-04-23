from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re

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
    
    # Komen dulu punya boleanweng
    # def action_post(self):
    #     for rec in self:
    #         if rec.move_type == 'out_invoice':
    #             if not rec.env.context.get('from_wizard'):
    #                 confirmation_message = "Apakah anda ingin mengenerate : %s?" % rec.journal_id.name
    #                 return {
    #                     'type'      : 'ir.actions.act_window',
    #                     'res_model' : 'wizard.action.confirm.invoice',
    #                     'view_mode' : 'form',
    #                     'view_id'   : self.env.ref('ny_account.view_wizard_action_confirm_invoice').id,
    #                     'target'    : 'new',
    #                     'context': {
    #                         'active_id'             : rec.id, 
    #                         'active_model'          : rec._name,
    #                         'confirmation_message'  : confirmation_message  
    #                     },
    #                 }
                
    #             if self.journal_id.is_org:    
    #                 if not self.journal_id.varieties_id:
    #                     raise ValidationError(f"Journal yang anda pilih [{self.journal_id.name}] tidak memiliki ORG, silahkan isi terlebih dahulu!.")
                    
    #                 for line in rec.invoice_line_ids:
    #                     line.plantation_varieties_id = self.journal_id.varieties_id.id

    #     return super(AccountMove, self).action_post()

    @api.depends('partner_id', 'line_ids.tax_ids')
    def _compute_need_kode_transaksi(self):
        for move in self:
            # Modify efaktur l10in_id_faktur
            # hilangin persyaratan nomor faktur ini. 
            # Karena ada perubahan Coretax, jd blum tau 
            # mekanismenya masih bisa upload dari Odoo atau tidak
            move.l10n_id_need_kode_transaksi = False
    
    def action_post(self):
        """Override action_post untuk menambahkan logika skip validasi e-Faktur."""
        param_obj = self.env['ir.config_parameter'].sudo()
        self.env.cr.commit()
        skip_efaktur_validation = param_obj.get_param('custom.skip_efaktur_validation', default='False') == 'True'

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

    # @api.onchange('l10n_id_tax_number')  
    # def _onchange_l10n_id_tax_number(self):  
    #     param_obj = self.env['ir.config_parameter'].sudo()  
    #     skip_efaktur_validation = param_obj.get_param('custom.skip_efaktur_validation', default='False') == 'True'  

    #     for record in self:  
    #         if skip_efaktur_validation:
    #             continue
    #         if record.l10n_id_tax_number and record.move_type not in self.get_purchase_types():  
    #             raise UserError(_("You can only change the number manually for a Vendor Bills and Credit Notes"))

    # def write(self, vals):
    #     """Memaksa update nomor e-Faktur jika skip e-Faktur aktif"""
    #     param_obj = self.env['ir.config_parameter'].sudo()
    #     skip_efaktur_validation = param_obj.get_param('custom.skip_efaktur_validation', default='False') == 'True'

    #     if skip_efaktur_validation and 'l10n_id_tax_number' in vals:
    #         return super(AccountMove, self.sudo()).write(vals)  # Gunakan sudo agar bisa bypass restriksi

    #     return super(AccountMove, self).write(vals)

    # @api.model
    # def create(self, vals):
    #     """Pastikan saat create, nomor e-Faktur tetap bisa di-set jika skip e-Faktur aktif."""
    #     param_obj = self.env['ir.config_parameter'].sudo()
    #     skip_efaktur_validation = param_obj.get_param('custom.skip_efaktur_validation', default='False') == 'True'

    #     if skip_efaktur_validation and 'l10n_id_tax_number' in vals:
    #         return super(AccountMove, self.sudo()).create(vals)

    #     return super(AccountMove, self).create(vals)

    # gabisa super, karena private kali :(
    # @api.constrains('l10n_id_tax_number')
    # def _constrains_l10n_id_tax_number(self):
    #     super()._constrains_l10n_id_tax_number()

    #     for record in self.filtered('l10n_id_tax_number'):
    #         if len(record.l10n_id_tax_number) < 16:
    #             raise UserError(_('A tax number should have at least 16 digits'))

    # @api.constrains('l10n_id_tax_number')
    # def _constrains_l10n_id_tax_number(self):
    #     for record in self.filtered('l10n_id_tax_number'):
    #         if record.l10n_id_tax_number != re.sub(r'\D', '', record.l10n_id_tax_number):
    #             record.l10n_id_tax_number = re.sub(r'\D', '', record.l10n_id_tax_number)
    #         if len(record.l10n_id_tax_number) < 16:
    #             raise UserError(_('A tax number should have at least 16 digits'))
    #         elif record.l10n_id_tax_number[:2] not in dict(self._fields['l10n_id_kode_transaksi'].selection).keys():
    #             raise UserError(_('A tax number must begin by a valid Kode Transaksi'))
    #         elif record.l10n_id_tax_number[2] not in ('0', '1'):
    #             raise UserError(_('The third digit of a tax number must be 0 or 1'))