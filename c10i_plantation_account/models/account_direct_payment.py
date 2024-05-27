from odoo import api, fields, models, _, tools

class AccountDirectPayment(models.Model):
    _inherit = "account.direct.payment"
    
    operating_unit_id = fields.Many2one('operating.unit', string='Operation Unit', check_company=True, default=lambda s: s.env.operating_unit)

    def _prepare_move(self):
        res = super()._prepare_move()
        res.update({
                'operating_unit_id': self.operating_unit_id.id if self.operating_unit_id else False,
            })
        return res

class AccountDirectPaymentLine(models.Model):
    _inherit = "account.direct.payment.line"

    cost_allocation_id = fields.Many2one('plantation.cost.type', string='Cost Allocation')
    cost_allocation_mark = fields.Selection(related='cost_allocation_id.mark', string='Allocation Mark', store=True)
    cost_center_id = fields.Many2one('plantation.cost.center', string='Cost Center', 
        domain="[('type_id','=',cost_allocation_id)]")
    filtered_cost_activity_ids = fields.Many2many('plantation.cost.activity', string='Filter Activity', compute='_filtered_cost_activity_ids')
    cost_activity_id = fields.Many2one('plantation.cost.activity', string='Activity')

    @api.depends('cost_allocation_id','cost_center_id')
    def _filtered_cost_activity_ids(self):
        for line in self:
            if line.payment_id.state!='draft' or not line.cost_allocation_id:
                line.filtered_cost_activity_ids = []
                continue
            activity_ids = []
            if line.cost_allocation_id.code=='PJ' and line.cost_center_id:
                current_project = self.env['plantation.project'].search([('cost_center_id','=',line.cost_center_id.id)])
                activity_ids = current_project.project_activity_ids.mapped('cost_activity_id').ids if current_project else []
            else:
                activity_ids = self.env['plantation.cost.activity'].search([('type_id','=',line.cost_allocation_id.id)]).ids
            
            line.filtered_cost_activity_ids = [(6, 0, activity_ids)]

    def _prepare_move_line(self):
        res = super()._prepare_move_line()
        res.update({
                'cost_allocation_id': self.cost_allocation_id.id if self.cost_allocation_id else False,
                'cost_center_id': self.cost_center_id.id if self.cost_center_id else False,
                'cost_activity_id': self.cost_activity_id.id if self.cost_activity_id else False,
            })
        return res

    @api.onchange('cost_activity_id')
    def onchange_activity(self):
        if self.cost_activity_id and self.cost_activity_id.account_allocation_id:
            self.account_id = self.cost_activity_id.account_allocation_id.id