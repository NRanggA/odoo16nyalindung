from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardSeedMutationReport(models.TransientModel):
    _name           = 'wizard.seed.mutation.report'
    _description    = 'Wizard Mutasi Bibit Report'

    product_id      = fields.Many2one('product.product', string='Product')
    date_start      = fields.Date('Date Start')
    date_end        = fields.Date('Date End')
    location_id     = fields.Many2one('lhm.nursery', string='location', ondelete="cascade", required=True)

    def create_report(self):
        if not self.date_start or not self.date_end:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Mutasi !"))
        
        return self.env.ref('c10i_plantation_seed.action_seed_mutation_report_xlsx').report_action(self)