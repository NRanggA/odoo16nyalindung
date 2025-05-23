from odoo import models, fields, api, _

class CropTaskMaterial(models.Model):
    _name = 'planning.crop.task.material'
    _description = 'Task Material Plan'
    _check_company_auto = True
    _rec_names_search = ['name', 'task_id.activity_id', 'product_id']

    planning_task_id = fields.Many2one('planning.crop.task', required=True, 
                        string='Task', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', 
                        ondelete='restrict', required=True)
    base_uom_id = fields.Many2one(related='product_id.uom_id', string='Base UoM', 
                        compute='_get_base_uom', precompute=True, store=True)
    base_uom_categ_id = fields.Many2one(related='base_uom_id.category_id', string='Base UoM Category', 
                        compute='_get_base_uom', precompute=True, store=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', 
                        compute='_get_base_uom', domain="[('category_id','=',base_uom_categ_id)]",
                        precompute=True, store=True)
    
    # Plan Qty and Cost
    plan_qty = fields.Float('Plannnig Quantity')
    cost_price = fields.Float('Unit Cost')
    plan_cost = fields.Float(compute='_compute_plan_cost', string='Planned Cost', store=True)

    # Actual Qty and Cost
    # actual_qty = fields.Float(compute='_compute_actual_cost', string='Actual Qty', store=True)
    # actual_cost = fields.Float(compute='_compute_actual_cost', string='Actual Cost', store=True)

    @api.depends('product_id')
    def _get_base_uom(self):
        for line in self:
            # line.uom_id = line.product_id.uom_id.id
            line.base_uom_id = line.product_id.uom_id.id
            line.base_uom_categ_id = line.product_id.uom_id.category_id.id
    
    @api.depends('plan_qty', 'cost_price')
    def _compute_plan_cost(self):
        for line in self:
            line.plan_cost = line.plan_qty * line.cost_price
    
    # @api.depends('task_id', 'cost_price', 'uom_id',
    #     'task_id.material_ids',
    #     'task_id.material_ids.uom_id',
    #     'task_id.material_ids.product_qty')
    # def _compute_actual_cost(self):
    #     for line in self:
    #         qty_actual = 0.0
    #         for m in line.task_id.material_ids:
    #             qty_actual += line.uom_id._compute_quantity(m.product_qty, m.uom_id)
    #         line.actual_qty = qty_actual
    #         line.actual_cost = line.actual_qty * line.cost_price