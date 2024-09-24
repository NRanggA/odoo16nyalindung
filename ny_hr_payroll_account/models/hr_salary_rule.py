# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    config_account_ids = fields.One2many('hr.salary.rule.account', 'rule_id', string='Config Accounting')