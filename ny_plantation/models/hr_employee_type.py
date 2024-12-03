from odoo import models, fields, api, _

class hr_employee_type(models.Model):
    _inherit          = 'hr.employee.type'

    penyadap = fields.Boolean('Penyadap', default=False)