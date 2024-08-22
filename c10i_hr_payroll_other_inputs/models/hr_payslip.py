# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.c10i_hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.addons.c10i_hr_payroll_other_inputs.models.browsable_object import OtherInput

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    other_input_ids = fields.One2many('hr.payslip.other.input', 'payslip_id', string='Other Inputs')

    def _get_localdict(self):
        self.ensure_one()
        localdict = super(HrPayslip, self)._get_localdict()
        other_inputs_dict = {oiline.type_code: oiline for oiline in self.other_input_ids if oiline.type_code}
        localdict.update({
            'other_input': OtherInput(self.employee_id.id, other_inputs_dict, self.env),
        })
        return localdict

    def get_other_inputs(self):
        """
        @return: returns a list of tuple containing the other input id that should be linked for the given period between date_from and date_to
        """
        self.ensure_one()
        domain = [('batch_id.state','=','confirm'),('employee_id','=',self.employee_id.id),
                  ('date','>=',self.date_from),('date','<=',self.date_to),
                  ('payslip_id','=',False)]
        other_inputs = self.env['hr.payslip.other.input'].search(domain)
        return list(map(lambda l: (4, l.id), other_inputs)) if other_inputs else []

    def compute_sheet(self):
        payslips = self.filtered(lambda p: p.state in ['draft', 'verify'])
        for slip in payslips:
            slip.other_input_ids = slip.get_other_inputs()
        res = super(HrPayslip, self).compute_sheet()
        return res