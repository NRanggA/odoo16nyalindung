from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError

class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution')
    filter_gae_location_ids = fields.Many2many('lhm.location', 'filter_hr_employee_gae_location_rel', compute='_filter_location_gae_ids', string='Filter GAE ke Lokasi')
    gae_to_location_ids = fields.Many2many('lhm.location', 'hr_employee_gae_location_rel', string='GAE ke Lokasi', help='Mendistribusikan biaya lainnya ke Lokasi langsung jika TBM')
    def _filter_location_gae_ids(self):
        for employee in self:
            employee.filter_gae_location_ids = self.env['lhm.plant.block'].search([]).mapped('location_id')
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution')
    gae_to_location_ids = fields.Many2many('lhm.location', 'hr_employee_gae_location_rel', string='GAE ke Lokasi', help='Mendistribusikan biaya lainnya ke Lokasi langsung jika TBM')
    
    