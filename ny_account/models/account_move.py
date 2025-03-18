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

                if skip_efaktur_validation:
                    rec.l10n_id_tax_number = '%s0%013d' % (str(rec.l10n_id_kode_transaksi), 0)
                    # continue

        return super(AccountMove, self).action_post()

    # gabisa super, karena private kali :(
    # @api.constrains('l10n_id_tax_number')
    # def _constrains_l10n_id_tax_number(self):
    #     super()._constrains_l10n_id_tax_number()

    #     for record in self.filtered('l10n_id_tax_number'):
    #         if len(record.l10n_id_tax_number) < 16:
    #             raise UserError(_('A tax number should have at least 16 digits'))

    @api.constrains('l10n_id_tax_number')
    def _constrains_l10n_id_tax_number(self):
        for record in self.filtered('l10n_id_tax_number'):
            if record.l10n_id_tax_number != re.sub(r'\D', '', record.l10n_id_tax_number):
                record.l10n_id_tax_number = re.sub(r'\D', '', record.l10n_id_tax_number)
            if len(record.l10n_id_tax_number) < 16:
                raise UserError(_('A tax number should have at least 16 digits'))
            elif record.l10n_id_tax_number[:2] not in dict(self._fields['l10n_id_kode_transaksi'].selection).keys():
                raise UserError(_('A tax number must begin by a valid Kode Transaksi'))
            elif record.l10n_id_tax_number[2] not in ('0', '1'):
                raise UserError(_('The third digit of a tax number must be 0 or 1'))

    # def _post(self, soft=True):
    #     """Custom override untuk menonaktifkan validasi e-Faktur berdasarkan sistem parameter."""
    #     param_obj = self.env['ir.config_parameter'].sudo()

    #     # Pastikan kita membaca parameter terbaru
    #     self.env.cr.commit()
    #     skip_efaktur_validation = param_obj.get_param('custom.skip_efaktur_validation', default='False') == 'True'

    #     print("=== PARAMETER SKIP E-FAKTUR:", skip_efaktur_validation)

    #     for move in self:
    #         if move.l10n_id_need_kode_transaksi:
    #             if not move.l10n_id_kode_transaksi:
    #                 raise ValidationError(_('You need to put a Kode Transaksi for this partner.'))
    #             if move.l10n_id_replace_invoice_id.l10n_id_tax_number:
    #                 if not move.l10n_id_replace_invoice_id.l10n_id_attachment_id:
    #                     raise ValidationError(_('Replacement invoice only for invoices on which the e-Faktur is generated. '))
    #                 rep_efaktur_str = move.l10n_id_replace_invoice_id.l10n_id_tax_number
    #                 move.l10n_id_tax_number = '%s1%s' % (move.l10n_id_kode_transaksi, rep_efaktur_str[3:])
    #             else:
    #                 # Jika parameter skip_efaktur_validation = True, langsung lanjut tanpa validasi
    #                 if skip_efaktur_validation:
    #                     print("=== VALIDASI E-FAKTUR DILEWATI ===")
    #                     move.l10n_id_tax_number = '%s0%013d' % (str(move.l10n_id_kode_transaksi), 0)
    #                     continue  # Lanjut ke move berikutnya tanpa validasi

    #                 # Jika parameter False, tetap lakukan validasi seperti biasa
    #                 efaktur = self.env['l10n_id_efaktur.efaktur.range'].pop_number(move.company_id.id)
    #                 if not efaktur:
    #                     raise ValidationError(_('There is no Efaktur number available.  Please configure the range you get from the government in the e-Faktur menu. '))
    #                 move.l10n_id_tax_number = '%s0%013d' % (str(move.l10n_id_kode_transaksi), efaktur)

    #     return super()._post(soft)
