# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.c10i_plantation_payroll.models.browsable_object import Payslips3

from datetime import date, datetime, time
from pytz import timezone
from dateutil.relativedelta import relativedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    lhm_line_ids = fields.One2many('lhm.transaction.line', 'payslip_id', string='LHM Lines')
                                 
    def get_lhm_transaction(self):
        """
        @return: returns a list of tuple containing the overtime id that should be linked for the given period between date_from and date_to
        """
        self.ensure_one()
        domain = [('employee_id','=',self.employee_id.id),
                    ('lhm_id.state','=','done'),
                    ('date','>=',self.date_from),('date','<=',self.date_to),
                    ('payslip_id','=',False)]
        lhm_lines = self.env['lhm.transaction.line'].search(domain)
        return list(map(lambda l: (4, l.id), lhm_lines)) if lhm_lines else []

    def compute_sheet(self):
        payslips = self.filtered(lambda p: p.state in ['draft', 'verify'])
        for slip in payslips:
            slip.lhm_line_ids = slip.get_lhm_transaction()
        res = super(HrPayslip, self).compute_sheet()
        return res
    
    ############################################################
    #                           HELPER                         #
    ############################################################
    def _get_localdict(self):
        self.ensure_one()
        localdict = super()._get_localdict()
        localdict = {
            **localdict,
            **{
                'payslip': Payslips3(self.employee_id.id, self, self.env),
            }
        }
        return localdict

    def get_worked_day_lines(self, contracts, date_from, date_to):
        '''
            Summarize attendance sheet
        '''
        if False:
            res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        else:
            res = []
            query_att = """SELECT hat.code, hat.name, count(has.id) as num_of_days FROM hr_attendance_sheet has, hr_employee he,hr_attendance_type hat  
                WHERE has.employee_id=he.id and has.type_id=hat.id and 
                    has.check_in between '%(date_from)s' and '%(date_to)s'
                GROUP BY hat.code, hat.name"""
            self.env.cr.execute(query_att%({
                'date_from': datetime.combine(fields.Date.from_string(date_from), time.min), 
                'date_to': datetime.combine(fields.Date.from_string(date_to), time.max)
            }))
            for contract in contracts:
                total_hk = 0.0
                for row_res in self.env.cr.dictfetchall():
                    attendances = {
                        'name': _(row_res.get('name','')),
                        'sequence': 10,
                        'code': row_res.get('code', ''),
                        'number_of_days': row_res.get('num_of_days',0),
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    }
                    total_hk += attendances['number_of_days']
                    res.append(attendances)
                attendances = {
                    'name': 'Total Hari kerja',
                    'sequence': 100,
                    'code': 'TOTALHK',
                    'number_of_days': total_hk,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                }
                res.append(attendances)
        return res