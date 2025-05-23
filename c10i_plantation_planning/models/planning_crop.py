from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import ValidationError

from datetime import timedelta
from dateutil.relativedelta import relativedelta

class PlanningCrop(models.Model):
    _name = 'planning.crop'
    _description = 'Planning Crop'
    _order = 'date_from desc, id desc'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True
    _rec_names_search = ['plant_block_id.name']

    plant_block_id = fields.Many2one('lhm.plant.block', required=True, 
                        string='Blok Tanam', tracking=True, ondelete='restrict', copy=True)
    date_from = fields.Date('From', required=True, 
                        tracking=True, copy=False)
    date_to = fields.Date('To', required=True, 
                        tracking=True, copy=False)
    type = fields.Selection([('weekly', 'Weekly Plan'),('monthly', 'Monthly Plan')],
                        string='Type', copy=True)
    task_ids = fields.One2many('planning.crop.task', 'planning_id', string='Task')
    company_id = fields.Many2one('res.company', required=True,
                        default=lambda self: self.env.company.id, 
                        string='Company')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True, copy=False)
    active = fields.Boolean(default=True)

    @api.constrains('date_from', 'date_to', 'plant_block_id', 'type')
    def _check_date(self):
        for plan in self:
            if plan.date_from > plan.date_to:
                raise ValidationError(_("The start date must be less than the end date."))
            existing_plans = self.search([
                ('id', '!=', plan.id),
                ('plant_block_id', '=', plan.plant_block_id.id),
                ('date_from', '<=', plan.date_to),
                ('date_to', '>=', plan.date_from),
                ('type', '=', plan.type),
            ])
            if existing_plans:
                raise ValidationError(_("The selected block already has a plan in the same date range."))

    def default_get(self, fields_list):
        res = super(PlanningCrop, self).default_get(fields_list)
        if res.get('type') == 'weekly':
            if 'date_from' in fields_list and 'date_to' in fields_list:
                today = fields.Date.context_today(self)
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                res.update({
                    'date_from': start_of_week,
                    'date_to': end_of_week,
                })
        elif res.get('type') == 'monthly':
            if 'date_from' in fields_list and 'date_to' in fields_list:
                today = fields.Date.context_today(self)
                start_of_month = today.replace(day=1)
                end_of_month = (start_of_month + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
                res.update({
                    'date_from': start_of_month,
                    'date_to': end_of_month,
                })
        return res

    def copy_data(self, default=None):
        res = super(PlanningCrop, self).copy_data(default=default)
        
        add_default_vals = {}
        if self.type == 'weekly':
            today = fields.Date.context_today(self)
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            add_default_vals.update({
                'date_from': start_of_week,
                'date_to': end_of_week,
            })
        elif self.type == 'monthly':
            today = fields.Date.context_today(self)
            start_of_month = today.replace(day=1)
            end_of_month = (start_of_month + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
            add_default_vals.update({
                'date_from': start_of_month,
                'date_to': end_of_month,
            })
        copy_task_lines = []
        for task in self.task_ids:
            copy_task_vals = task.copy_data()[0]
            copy_task_lines.append((0, 0, copy_task_vals))
        
        res[0].update({
            **add_default_vals,
            'task_ids': copy_task_lines,
        })
        return res
    
    def name_get(self):
        res = []
        for plan in self:
            name = f"{plan.plant_block_id.code} ({plan.date_from.strftime('%d-%m')} - {plan.date_to.strftime('%d-%m')})"
            res.append((plan.id, name,))
        return res

    def write(self, update_vals):
        for plan in self:
            if 'date_from' in update_vals or 'date_to' in update_vals:
                plan._check_date()
        return super(PlanningCrop, self).write(update_vals)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|','|','|', 
                ('plant_block_id.name', '=ilike', name.split(' ')[0] + '%'), 
                ('plant_block_id.name', operator, name), 
                ('plant_block_id.code', '=ilike', name + '%')
                ('plant_block_id.code', operator, name)
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def action_confirm(self):
        self.state = 'confirm'
        return True
    
    def action_done(self):
        self.state = 'done'
        return True
    
    def action_set_draft(self):
        self.state = 'draft'
        return True