# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrPayslipRunCostMap(models.Model):
    _inherit = 'hr.payslip.cost.map'

    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution', help="Untuk non Gaji")
    gae_to_location_ids = fields.Many2many('lhm.location', 'hr_payslip_cost_map_gae_location_rel', string='GAE ke Lokasi', help='Mendistribusikan biaya lainnya ke Lokasi langsung jika TBM')
    gae_to_location = fields.Boolean(string='GAE ke Lokasi', help='Mendistribusikan biaya lainnya ke Lokasi langsung jika TBM')