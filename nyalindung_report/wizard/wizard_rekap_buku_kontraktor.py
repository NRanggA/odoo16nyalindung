from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class WizardRekapBukuKontraktor(models.TransientModel):
    _name = 'wizard.rekap.buku.kontraktor'
    _description = 'Wizard Rekap Buku Kontraktor'
    
    from_date = fields.Date('From Date', required=True,
            default=lambda self: fields.Date.today().replace(day=1))
    to_date = fields.Date('To Date', required=True,
            default=lambda self: fields.Date.today())
    partner_ids = fields.Many2many("res.partner", string="Kontraktor")

    def print_excel(self):
        return self.env.ref('nyalindung_report.action_report_rekap_buku_kontraktor_xlsx').report_action(self)