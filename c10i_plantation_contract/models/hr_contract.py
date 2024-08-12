from odoo import fields, models, api, _

class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_id          = fields.Many2one('hr.contract.wage', string='Wage Type')
    employee_type_id = fields.Many2one('hr.employee.type', string="Tipe Karyawan")

    def write(self, vals):
        res = super(HrContract, self).write(vals)
        
        if vals.get('state') == 'open':
            # self._assign_open_contract()

            if self.employee_type_id:
                employees = self.env['hr.employee'].search([('type_id', '=', self.employee_type_id.id)])
                for employee in employees:
                    employee.write({'contract_id': self.id})
                    print(f"== Memperbaruhi field contract id untuk employee : {employee.name}")
        
        return res
