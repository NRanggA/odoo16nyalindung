# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrSalaryRuleAccount(models.Model):
    _name = 'hr.salary.rule.account'
    _description = 'Account Configuration on Salary Rule'
    _order = 'id desc'

    rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule', ondelete='restrict')
    is_map_from_lhm = fields.Boolean('Based on LHM Activity')
    is_general_charge = fields.Boolean('Is General Charge')
    is_bpjs_tk = fields.Boolean('BPJS TK')
    is_bpjs_kes = fields.Boolean('BPJS KES')
    default_debit_account_id = fields.Many2one('account.account', string='Debit Account', ondelete='restrict')
    default_credit_account_id = fields.Many2one('account.account', string='Credit Account', ondelete='restrict')
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', required=True)
