from odoo import models, fields, api, _

class CropTask(models.Model):
    _name = 'planning.crop.task'
    _description = 'Crop Task Planning'
    _order = 'id desc'
    _rec_name = 'activity_id'
    _check_company_auto = True

    planning_id = fields.Many2one('planning.crop', string='Planning', ondelete='cascade', copy=False)
    parent_state = fields.Selection(related='planning_id.state', string='Planning State', store=True, copy=False)
    filtered_activities = fields.Many2many('lhm.activity', 'planning_crop_task_activities_rel', compute='_filter_activities', string='Filter Activities')
    @api.depends('planning_id.state','planning_id.plant_block_id')
    def _filter_activities(self):
        query_parents = """SELECT parent_id FROM lhm_activity"""
        self.env.cr.execute(query_parents)
        parent_activity_ids = [x[0] for x in self.env.cr.fetchall()]
        for task in self:
            if task.planning_id.state!='draft':
                task.filtered_activities = []
            else:
                if task.planning_id.plant_block_id.is_project:
                    projects = self.env['lhm.project'].search([('plant_block_id','=',task.planning_id.plant_block_id.id)])
                    project_activity_ids = []
                    for project in projects:
                        project_activity_ids += [x.activity_id.id for x in project.line_ids if x.activity_id.id not in parent_activity_ids]
                    if project_activity_ids:
                        task.filtered_activities = [(6, 0, project_activity_ids)]
                    else:
                        task.filtered_activities = []
                else:
                    # activities = task.planning_id.plant_block_id.varieties_id.general_charges_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
                    # activities = task.planning_id.plant_block_id.varieties_id.indirect_cost_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
                    activities = task.planning_id.plant_block_id.varieties_id.harvest_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
                    activities |= task.planning_id.plant_block_id.varieties_id.upkeep_activity_ids.filtered(lambda x: x.id not in parent_activity_ids)
                    task.filtered_activities = [(6, 0, activities.ids)] if activities else []

    activity_id = fields.Many2one('lhm.activity', required=True, 
                        string='Activity', tracking=True, ondelete='restrict')
    
    plan_work_day = fields.Integer("Plan HK")
    product_id = fields.Many2one('product.product', string='Product Hasil', ondelete='restrict')
    plan_result = fields.Float("Plan Hasil")
    product_id_2 = fields.Many2one('product.product', string='Product Hasil 2', ondelete='restrict')
    plan_result_2 = fields.Float("Plan Hasil 2")
    
    plan_material_ids = fields.One2many('planning.crop.task.material', 'planning_task_id', string='Plan Material')
    plan_manpower_ids = fields.One2many('planning.crop.task.manpower', 'planning_task_id', string='Plan Manpower')
    
    act_emp_work_day = fields.Integer(compute='_compute_actual', string="Actual HK")
    act_emp_result = fields.Float(compute='_compute_actual', string="Actual Hasil (Karyawan)")
    act_emp_result_2 = fields.Float(compute='_compute_actual', string="Actual Hasil 2 (Karyawan)")
    
    act_partner_result = fields.Float(compute='_compute_actual', string="Hasil Aktual (Borong)")
    act_partner_result_2 = fields.Float(compute='_compute_actual', string="Hasil 2 Aktual (Borong)")
    
    act_result = fields.Float(compute='_compute_actual', string="Hasil Aktual")
    act_result_2 = fields.Float(compute='_compute_actual', string="Hasil 2 Aktual")

    def _compute_actual(self):
        for task in self:
            query = """SELECT 
                sum(work_day) as act_emp_work_day,
                sum(hasil_1) as act_emp_result,
                sum(hasil_2) as act_emp_result_2
            FROM 
                lhm_transaction_line ltl 
                INNER JOIN lhm_transaction lt ON lt.id=ltl.lhm_id
            WHERE 
                lt.state in ('done','process') AND ltl.date between %s and  %s
                AND ltl.location_id=%s AND ltl.activity_id=%s
            GROUP BY ltl.activity_id
            """
            self.env.cr.execute(query, (task.planning_id.date_from, task.planning_id.date_to,
                    task.planning_id.plant_block_id.location_id.id, task.activity_id.id))
            actual_res = self.env.cr.dictfetchone()
            if actual_res:
                actual_res = actual_res
            else:
                actual_res = {}

            task.act_emp_work_day = actual_res.get('act_emp_work_day')
            task.act_emp_result = actual_res.get('act_emp_result')
            task.act_emp_result_2 = actual_res.get('act_emp_result_2')
            task.act_partner_result = 0
            task.act_partner_result_2 = 0
            task.act_result = task.act_emp_result + task.act_partner_result
            task.act_result_2 = task.act_emp_result_2 + task.act_partner_result_2

    # def copy_data(self, default=None):
    #     res = super(CropTask, self).copy_data(default=default)
    #     for mpp in self.plan_manpower_ids:
    #         mpp.copy_data()
    #     return res

    def action_view_lhm_transaction(self):
        action = self.env["ir.actions.actions"]._for_xml_id("c10i_lhm_v16.action_lhm_transaction")
        action['domain'] = [('activity_id', '=', self.activity_id.id),
                            ('location_id', '=',self.plant_block_id.location_id.id),
                            ('lhm_id.state', 'in', ['done', 'process'])]
        return action

    def action_view_stock_move(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_picking_action")
        action['domain'] = [('activity_id', '=', self.activity_id.id),
                            ('location_id', '=',self.plant_block_id.location_id.id),
                            ('state', '=', 'done')]
        return action