from odoo import models, fields, _
from odoo.osv import expression

class Employee(models.Model):
    _inherit = 'hr.employee'

    def _get_contracts(self, date_from, date_to, states=['open'], kanban_state=False):
        """
        Returns the contracts of the employee between date_from and date_to
        """
        if self.basic_salary_type=='employee_type':
            state_domain = [('state', 'in', states)]
            if kanban_state:
                state_domain = expression.AND([state_domain, [('kanban_state', 'in', kanban_state)]])

            return self.env['hr.contract'].search(
                expression.AND([[('employee_type_id', '=', self.type_id.id)],
                state_domain,
                [('date_start', '<=', date_to),
                    '|',
                        ('date_end', '=', False),
                        ('date_end', '>=', date_from)]]))
        else:
            return super(Employee, self)._get_contracts(date_from, date_to, states=states, kanban_state=kanban_state)