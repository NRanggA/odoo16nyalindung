# -*- coding:utf-8 -*-

from odoo import api, fields, models, _

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    pph_mark_type = fields.Selection([('base_amount','[BASEPPH] Dasar Pengenaan Pajak Penghasilan'),
                        ('potongan_jaminan_pensiun','[JHT] Potongan Pensiun atau Jaminan Hari Tua')],
                        string='Tanda Dasar Pengenaan Pajak Penghasilan')

    def _sum_salary_rule_base_pph(self, localdict, pph_type, amount):
        localdict['pph_types'].dict[pph_type] = pph_type in localdict['pph_types'].dict and localdict['pph_types'].dict[pph_type] + amount or amount
        return localdict

    def _hook_localdict(self, localdict, res_rule_amount, previous_amount):
        localdict = super(HrSalaryRule, self)._hook_localdict(localdict, res_rule_amount, previous_amount)
        if self.pph_mark_type == 'base_amount':
            if self.category_id.code in ('BASIC','ALW','GROSS'):
                localdict = self._sum_salary_rule_base_pph(localdict, 'BASEPPH', res_rule_amount - previous_amount)
            elif self.category_id.code=='DED':
                localdict = self._sum_salary_rule_base_pph(localdict, 'BASEPPH', (-1*res_rule_amount) - previous_amount)
        if self.pph_mark_type == 'potongan_jaminan_pensiun':
            localdict = self._sum_salary_rule_base_pph(localdict, 'JHT', res_rule_amount - previous_amount)
        return localdict
    