from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_type_id          = fields.Many2one('hr.contract.wage.type', string='Wage Type')
    employee_type_id      = fields.Many2one('hr.employee.type', string="Tipe Karyawan")
    work_day              = fields.Integer(string="Work Day", default=25)
    wage_day              = fields.Float(string="Wage Daily", compute='_compute_worked_hours', store=True, readonly=True)
    is_lhm                = fields.Boolean('LHM', default=False)

    @api.depends('wage', 'work_day')
    def _compute_worked_hours(self):
        for wage in self:
            if wage.wage > 0 or wage.work_day > 0:
                wage.wage_day = wage.wage / wage.work_day

    def write(self, vals):
        res = super(HrContract, self).write(vals)
        
        if vals.get('state') == 'open':
            # self._assign_open_contract()

            if self.structure_type_id.id==2 and self.employee_type_id:
                employees = self.env['hr.employee'].search([('type_id', '=', self.employee_type_id.id),('basic_salary_type','=','employee_type')])
                # cek employee pada tipe karyawan tersebut apakah contract_id nya memiliki field employee_id yang mengarah ke dia
                for employee in employees:
                    # if not employee.contract_id.employee_id.id==employee.id:
                    #     raise ValidationError(_("Employee dengan nama %s memiliki contract_id yang mengarah ke dia") % employee.name)
                    employee.write({'contract_id': self.id})
                    # print(f"== Memperbaruhi field contract id untuk employee : {employee.name}")
            
            elif self.structure_type_id.id==1 and self.employee_type_id:
                # print(f"===== {self.structure_type_id.name}")
                # print(f"===== karyawan")
                # if not self.employee_id.basic_salary_type=='employee':
                #     raise ValidationError(_("Acuan Gaji harus disesuaikan"))
                self.employee_id.write({'contract_id': self.id})
        
        return res
