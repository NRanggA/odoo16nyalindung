# -*- coding: utf-8 -*-
import babel
from odoo import api, fields, models, tools, _
from odoo.addons.c10i_plantation_payroll.models.browsable_object import Payslips3

from datetime import date, datetime, time

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_worked_day_lines(self, contracts, employee_id, date_from, date_to):
        '''
            Summarize attendance sheet
        '''
        res = []
        query_att = """SELECT hat.code, hat.name, count(has.id) as num_of_days FROM hr_attendance_sheet has, hr_employee he,hr_attendance_type hat  
            WHERE has.employee_id=he.id and has.type_id=hat.id 
                and has.check_in between '%(date_from)s' and '%(date_to)s'
                and he.id=%(employee_id)s
            GROUP BY hat.code, hat.name"""
        
        self.env.cr.execute(query_att%({
            'date_from': datetime.combine(fields.Date.from_string(date_from), time.min), 
            'date_to': datetime.combine(fields.Date.from_string(date_to), time.max),
            'employee_id': employee_id,
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
            holiday_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
                            ('date','>=',date_from),('date','<=',date_to),('is_holiday','=',True),
                            ('type_id.code','=','KJ')])
            attendances_kjl = {
                'name': 'Kerja di Hari Libur/Raya',
                'sequence': 200,
                'code': 'KJL',
                'number_of_days': holiday_days,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(attendances_kjl)
            should_worked_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
                            ('date','>=',date_from),('date','<=',date_to),('is_holiday','=',False)])
            currmonth_hke_total = {
                'name': 'Hari Kerja Sebulan',
                'sequence': 200,
                'code': 'TOTALHK',
                'number_of_days': should_worked_days,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(currmonth_hke_total)
            mydaya_worked_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
                            ('date','>=',date_from),('date','<=',date_to),('is_holiday','=',False),
                            ('type_id.code','=','KJ'),('is_data_from_my_daya','=',True)])
            my_daya_attendance = {
                'name': 'Absensi dari MyDaya',
                'sequence': 200,
                'code': 'KJMYDAYA',
                'number_of_days': mydaya_worked_days,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(my_daya_attendance)

            # Sakit
            sakit_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
                            ('date','>=',date_from),('date','<=',date_to),
                            ('type_id.code','=','S1')])
            sakit_attendance = {
                'name': 'Sakit',
                'sequence': 200,
                'code': 'S1',
                'number_of_days': sakit_days,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(sakit_attendance)

            # Cuti
            cuti_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
                            ('date','>=',date_from),('date','<=',date_to),
                            ('type_id.code','=','CT')])
            cuti_attendance = {
                'name': 'Cuti',
                'sequence': 200,
                'code': 'CT',
                'number_of_days': cuti_days,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(cuti_attendance)
        return res

    def action_print_report(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.payroll_report_wizard_action")
        action['context'] = {'default_payslip_ids': [(6,0,self.ids)]}
        return action