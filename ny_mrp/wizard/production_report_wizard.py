# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductionReportWizard(models.TransientModel):
    _name = 'production.report.wizard'
    _description = 'Wizard Laporan Produksi'

    report_type = fields.Selection([
        ('raw_material', 'Laporan Olah Bahan Baku'),
        ('finished_product', 'Laporan Barang Jadi'),
    ], string='Jenis Laporan', required=True, default='raw_material')
    
    date_from = fields.Date(string='Tanggal Mulai', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Tanggal Akhir', required=True, default=fields.Date.today)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_('Tanggal Mulai harus lebih kecil atau sama dengan Tanggal Akhir!'))

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref('ny_mrp.action_report_production_order_xlsx').report_action(self)
