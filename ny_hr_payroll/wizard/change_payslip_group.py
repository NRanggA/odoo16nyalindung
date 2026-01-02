from odoo import models, fields, api, _

class ChangePayslipGroup(models.TransientModel):
    _name = 'hr.change.payslip.group'
    _description = 'Change Payslip Group'

    payslip_ids = fields.Many2many('hr.payslip', string='Payslip Details')
    payslip_group_id = fields.Many2one('hr.payslip.group', string='Payslip Group', required=True)

    def default_get(self, fields_list):
        res = super(ChangePayslipGroup, self).default_get(fields_list)
        if self._context.get('active_model')=='hr.payslip' and self._context.get('active_ids'):
            payslips = self.env['hr.payslip'].browse(self._context.get('active_ids'))
            res['payslip_ids'] = [(6,0,payslips.ids)]
        return res

    def change_group(self):
        self.ensure_one()
        self.payslip_ids.payslip_group_id = self.payslip_group_id.id
        self.payslip_ids.employee_id.payslip_group_id = self.payslip_group_id.id
        return True