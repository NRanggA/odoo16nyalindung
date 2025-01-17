# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
    help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    hra = fields.Monetary(string='HRA', help="House rent allowance.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    da = fields.Monetary(string="DA", help="Dearness allowance")
    meal_allowance = fields.Monetary(string="Meal Allowance", help="Meal allowance")
    medical_allowance = fields.Monetary(string="Medical Allowance", help="Medical allowance")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")
    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True, help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    
    bpjs_kesehatan = fields.Boolean('BPJS Kesehatan', default=True)
    add_person_bpjs_kesehatan = fields.Integer('Tambahan Tanggungan BPJS Kesehatan')
    bpjs_ketenagakerjaan = fields.Boolean('BPJS Ketenagakerjaan', default=True)
    bpjs_tk_pensiun = fields.Boolean('BPJS TK Pensiun', default=True)

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0

    def get_amount_bpjs(self, type, base_amount, person_addition=0):
        self.ensure_one()
        res = {'tunjangan': 0.0, 'potongan': 0.0, 'iuran': 0.0}
        proceed_compute = False
        if type=='bpjs_kesehatan' and self.bpjs_kesehatan:
            proceed_compute = True
        elif type in ('bpjs_ketenagakerjaan','bpjs_tk_jht', 'bpjs_tk_jkm', 'bpjs_tk_jkk') and self.bpjs_ketenagakerjaan:
            proceed_compute = True
        elif type=='bpjs_tk_pensiun' and self.bpjs_tk_pensiun:
            proceed_compute = True
        
        if proceed_compute:
            bpjs_found = self.env['hr.bpjs'].search([('type','=',type)
                # ,('date','<=',fields.Date.today())
                ], limit=1)
            if bpjs_found:
                if bpjs_found.plafond_salary:
                    base_bpjs = base_amount if base_amount<=bpjs_found.plafond_salary else bpjs_found.plafond_salary
                else:
                    base_bpjs = base_amount
                res['tunjangan'] = base_bpjs * bpjs_found.allowance_pct/100.0
                if type=='bpjs_kesehatan' and (person_addition or self.add_person_bpjs_kesehatan):
                    res['potongan'] = base_bpjs * (bpjs_found.deduction_pct + float(person_addition or self.add_person_bpjs_kesehatan))/100.0
                else:
                    res['potongan'] = base_bpjs * bpjs_found.deduction_pct/100.0
                res['iuran'] = res['tunjangan'] + res['potongan']
        return res

class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')
