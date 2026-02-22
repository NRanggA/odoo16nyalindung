from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class GaePlan(models.Model):
    _name = 'gae.plan'
    _description = 'GAE Plan'
    _order = 'id desc'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    total_distribution_percentage = fields.Float('Total Distribution Percentage', compute='_compute_total_distribution_percentage')
    line_ids = fields.One2many('gae.plan.line', 'plan_id', string='GAE Plan Lines')

    def _compute_total_distribution_percentage(self):
        for record in self:
            record.total_distribution_percentage = sum(record.line_ids.mapped('distribution_percentage'))

    def _check_total_distribution_percentage(self):
        for record in self:
            if record.total_distribution_percentage != 100:
                raise ValidationError(_('Total Distribution Percentage must be 100%.'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super(GaePlan, self).create(vals_list)
        records._check_total_distribution_percentage()
        return records

    def write(self, vals):
        res = super(GaePlan, self).write(vals)
        self._check_total_distribution_percentage()
        return res

class GaePlanLine(models.Model):
    _name = 'gae.plan.line'
    _description = 'GAE Plan Line'

    plan_id = fields.Many2one('gae.plan', string='GAE Plan', ondelete='cascade')
    varieties_id = fields.Many2one('plant.varieties', string='Varieties', required=True)
    distribution_percentage = fields.Float('Distribution Percentage', required=True)