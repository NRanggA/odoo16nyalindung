from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardReportProductionKebun(models.TransientModel):
    _name           = 'wizard.report.production.kebun'
    _description    = 'Wizard Report Production Kebun'
    
    from_date           = fields.Date('From Date')
    to_date             = fields.Date('To Date')
    # kemandoran_id       = fields.Many2many("hr.foreman", string="Kemandoran", ondelete="restrict", tracking=True, domain=[("id", "in", [140, 193, 195, 199, 200, 217])],)
    kemandoran_id       = fields.Many2many("hr.foreman", string="Kemandoran", ondelete="restrict", tracking=True, domain=[("is_sadap", "=", True)],)

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Production Kebun!"))

        return self.env.ref('nyalindung_report.action_production_report_kebun_xlsx').report_action(self)