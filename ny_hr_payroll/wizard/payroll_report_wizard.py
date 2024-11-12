from odoo import models, fields, api, _

class PayrollReportWizard(models.Model):
    _name = 'payroll.report.wizard'
    _description = 'Payroll Report'

    type = fields.Selection([('payroll_csv', 'CSV Payroll'),
                ('payroll_submission','Excel Pengajuan Gaji')], 'Type', required=True, default='payroll_submission')
    payslip_ids = fields.Many2many('hr.payslip', 'payroll_report_slip_rel', string='Payslips')

    # def default_get(self, fields_list):
    #     res = super(PayrollReportWizard, self).default_get(fields_list)
    #     if self._context.get('active_model')=='hr.payslip.run' and self._context.get('active_id'):
    #         batch = self.env['hr.payslip.run'].browse(self._context.get('active_id'))
    #         res['payslip_ids'] = [(6,0,batch.slip_ids.ids)]
    #     elif self._context.get('active_model')=='hr.payslip' and self._context.get('active_ids'):
    #         payslips = self.env['hr.payslip'].browse(self._context.get('active_ids'))
    #         res['payslip_ids'] = [(6,0,payslips.ids)]
    #     return res

    def print_report(self):
        if self.type=='payroll_csv':
            return self.env.ref('ny_hr_payroll.action_report_payroll_report_csv').report_action(self, data={
                'options': {'src_model': self._name, 'src_id': self.id, 'dest_model': 'hr.payslip'}
                })
        else:
            return self.env.ref('ny_hr_payroll.action_report_payroll_report_xlsx').report_action(self, data={
                'options': {'src_model': self._name, 'src_id': self.id, 'dest_model': 'hr.payslip'}
                })