# from odoo import models, fields, api, _

# class CostCenter(models.Model):
#     _inherit = 'account.cost.center'

#     payroll_distribution_ids = fields.One2many('cost.center.payroll.distribution', 'cost_center_id', string='Payroll Cost Distribution')

# class CostCenterPayrollAllocation(models.Model):
#     _name = 'cost.center.payroll.distribution'
#     _description = 'Cost Center Payroll Cost Distribution'

#     cost_center_id = fields.Many2one('account.cost.center', string='Cost Center')
#     varieties_id = fields.Many2one('plant.varieties', string='ORG')

#     dest_location_type_id = fields.Many2one('lhm.location.type', string='Dest. Type')
#     dest_location_id = fields.Many2one('lhm.location', string='Dest. Location')
#     dest_activity_id = fields.Many2one('lhm.activity', string='Dest. Activity')
#     pct_cost = fields.Float('% Cost')