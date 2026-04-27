from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError

class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution', help="Untuk non Gaji")
    filter_gae_location_ids = fields.Many2many('lhm.location', 'filter_hr_employee_gae_location_rel', compute='_filter_location_gae_ids', string='Filter GAE ke Lokasi')
    gae_to_location_ids = fields.Many2many('lhm.location', 'hr_employee_gae_location_rel', string='GAE ke Lokasi', help='Mendistribusikan biaya lainnya ke Lokasi')
    def _filter_location_gae_ids(self):
        for employee in self:
            employee.filter_gae_location_ids = self.env['lhm.plant.block'].search([]).mapped('location_id')
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution', help="Untuk non Gaji")
    gae_to_location_ids = fields.Many2many('lhm.location', 'hr_employee_gae_location_rel', string='GAE ke Lokasi', help='Mendistribusikan biaya lainnya ke Lokasi')
    
    def get_default_location_activity_payroll(self):
        self.ensure_one()
        res = super().get_default_location_activity_payroll()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>")
        if self.gae_to_location_ids and self.plantation_activity_id:
            res.update({
                'plantation_varieties_id': False,
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': self.plantation_activity_id.id,
                'plantation_activity_bpjs_tk_id': self.plantation_activity_bpjs_tk_id.id,
                'plantation_activity_bpjs_kes_id': self.plantation_activity_bpjs_kes_id.id,
                'plantation_account_id': self.plantation_activity_id.account_id.id,
                'plantation_account_bpjs_tk_id': self.plantation_activity_bpjs_tk_id.account_id.id,
                'plantation_account_bpjs_kes_id': self.plantation_activity_bpjs_kes_id.account_id.id,

            })
        print(">>>>>>>>>>>>>>>>>>>>>>>>>", self.gae_to_location_ids)
        return res