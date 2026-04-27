# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrSalaryRuleAccount(models.Model):
    _inherit = 'hr.salary.rule.account'
    
    is_gea_rule = fields.Boolean('Is GAE Account')
    # allocate_to_project = fields.Boolean('Allocate to Project')