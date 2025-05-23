from odoo import models, fields, api, _

class CropTaskManpower(models.Model):
    _name = 'planning.crop.task.manpower'
    _description = 'Task Manpower Plan'
    _check_company_auto = True
    _rec_names_search = ['name', 'task_id.activity_id', 'employee_id']

    planning_task_id = fields.Many2one('planning.crop.task', required=True, 
                        string='Task', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee', 
                        ondelete='restrict')
    
    # Planning Qty on Days/Hours for the Employee (or General if the Employee are Empty)
    plan_qty = fields.Float("Planned Qty")
    cost_per_uom = fields.Float("Cost per UoM")
    uom = fields.Selection([('hour','Hour'),('day','Day')], required=True, string='UoM')
    plan_cost = fields.Float(compute='_compute_plan_cost', string='Planned Cost', store=True)
    
    # Planning Hectare (This should be same with the plan hectare on the Task)
    plan_hectare = fields.Float("Planned Hectare")
    plan_cost_per_hectare = fields.Float(compute='_compute_plan_cost', string='Planned Cost per Hectare', store=True)

    # Actual Hectare and Cost
    # actual_qty = fields.Float(compute='_compute_actual_cost', string='Actual Qty', store=True)
    # actual_hectare = fields.Float(compute='_compute_actual_cost', string='Actual Hectare', store=True)
    # actual_cost = fields.Float(compute='_compute_actual_cost', string='Actual Cost', store=True)

    @api.depends('plan_qty', 'cost_per_uom', 'plan_hectare')
    def _compute_plan_cost(self):
        for line in self:
            line.plan_cost = line.plan_qty * line.cost_per_uom
            line.plan_cost_per_hectare = line.plan_cost / line.plan_hectare if line.plan_hectare else 0.0

    # @api.depends(
    #     'cost_per_uom',
    #     'task_id', 
    #     'task_id.timesheet_ids',
    #     'task_id.timesheet_ids.work_day',
    #     'task_id.timesheet_ids.result_hectare')
    # def _compute_actual_cost(self):
    #     for line in self:
    #         line.actual_hectare = sum(line.task_id.timesheet_ids.mapped('result_hectare')) if line.task_id.timesheet_ids else 0.0
    #         if line.uom=='day':
    #             line.actual_qty = sum(line.task_id.timesheet_ids.mapped('work_day')) if line.task_id.timesheet_ids else 0.0
    #         else: # hour
    #             line.actual_qty = 8*sum(line.task_id.timesheet_ids.mapped('work_day')) if line.task_id.timesheet_ids else 0.0
    #         line.actual_cost = line.actual_qty * line.cost_per_uom