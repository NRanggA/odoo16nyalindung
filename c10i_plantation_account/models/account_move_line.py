from odoo import api, fields, models, _, tools

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    operating_unit_id = fields.Many2one('operating.unit', string='Operation Unit', check_company=True)
    cost_allocation_mark = fields.Selection(related='cost_allocation_id.mark', string='Allocation Mark', store=True)
    cost_allocation_id = fields.Many2one('plantation.cost.type', string='Cost Allocation')
    cost_center_id = fields.Many2one('plantation.cost.center', string='Cost Center', 
        domain="[('type_id','=',cost_allocation_id)]")
    cost_activity_id = fields.Many2one('plantation.cost.activity', string='Activity')
    filtered_cost_activity_ids = fields.Many2many('plantation.cost.activity', string='Filter Activity', compute='_filtered_cost_activity_ids')
    cost_activity_id = fields.Many2one('plantation.cost.activity', string='Activity')

    @api.depends('cost_allocation_id','cost_center_id')
    def _filtered_cost_activity_ids(self):
        for line in self:
            if line.move_id.state!='draft' or not line.cost_allocation_id:
                line.filtered_cost_activity_ids = []
                continue
            activity_ids = []
            if line.cost_allocation_id.code=='PJ' and line.cost_center_id:
                current_project = self.env['plantation.project'].search([('cost_center_id','=',line.cost_center_id.id)])
                activity_ids = current_project.project_activity_ids.mapped('cost_activity_id').ids if current_project else []
            else:
                activity_ids = self.env['plantation.cost.activity'].search([('type_id','=',line.cost_allocation_id.id)]).ids
            
            line.filtered_cost_activity_ids = [(6, 0, activity_ids)]