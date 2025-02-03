# -*- coding: utf-8 -*-
import babel
from odoo import api, fields, models, tools, _
from odoo.addons.c10i_plantation_payroll.models.browsable_object import Payslips3

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_worked_day_lines(self, contracts, employee_id, date_from, date_to):
        '''
            Summarize attendance sheet
        '''
        res = []
        query_att = """SELECT hat.code, hat.name, count(has.id) as num_of_days FROM hr_attendance_sheet has, hr_employee he,hr_attendance_type hat  
            WHERE has.employee_id=he.id and has.type_id=hat.id 
                and has.date between '%(date_from)s' and '%(date_to)s'
                and he.id=%(employee_id)s
            GROUP BY hat.code, hat.name"""
        
        self.env.cr.execute(query_att%({
            # 'date_from': datetime.combine(fields.Date.from_string(date_from), time.min), 
            'date_from': date_from, 
            # 'date_to': datetime.combine(fields.Date.from_string(date_to), time.max),
            'date_to': date_to,
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
            # should_worked_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
            #                 ('date','>=',date_from),('date','<=',date_to),('is_holiday','=',False)])
            # currmonth_hke_total = {
            #     'name': 'Hari Kerja Sebulan',
            #     'sequence': 200,
            #     'code': 'TOTALHK',
            #     'number_of_days': should_worked_days,
            #     'number_of_hours': 0.0,
            #     'contract_id': contract.id,
            # }
            # res.append(currmonth_hke_total)
            # mydaya_worked_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
            #                 ('date','>=',date_from),('date','<=',date_to),('is_holiday','=',False),
            #                 ('type_id.code','=','KJ'),('is_data_from_my_daya','=',True)])
            # my_daya_attendance = {
            #     'name': 'Absensi dari MyDaya',
            #     'sequence': 200,
            #     'code': 'KJMYDAYA',
            #     'number_of_days': mydaya_worked_days,
            #     'number_of_hours': 0.0,
            #     'contract_id': contract.id,
            # }
            # res.append(my_daya_attendance)

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

            # Premi Kehadiran
            hadir_tanpa_koreksi_days = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
                            ('date','>=',date_from),('date','<=',date_to),
                            ('type_id.code','=','KJ'),('is_correction','=',False)])
            # ('is_data_from_my_daya','=',True)
            hadir_tanpa_koreksi_attendance = {
                'name': 'Hadir Tanpa Koreksi',
                'sequence': 200,
                'code': 'KJTK',
                'number_of_days': hadir_tanpa_koreksi_days,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(hadir_tanpa_koreksi_attendance)

            diliburkan_day = self.env['hr.attendance.sheet'].search_count([('employee_id','=',employee_id),
                            ('date','>=',date_from),('date','<=',date_to),
                            ('type_id.code','!=','KJ'),('is_diliburkan','=',True)])
            n_sunday = 0
            # first_date = datetime.strptime(date_from,'%Y-%m-%d')
            first_date = date_from
            # date_to = datetime.strptime(date_to,'%Y-%m-%d')
            while first_date <= date_to:  # or use `<` if you don't want it inclusive
                if first_date.weekday() == 6:
                    n_sunday += 1
                first_date += relativedelta(days=1)
            basis_premi_koreksi_attendance = {
                'name': 'Basis Premi Kehadiran',
                'sequence': 200,
                'code': 'BPKJ',
                'number_of_days': (date_to - date_from).days + 1 - (n_sunday + diliburkan_day),
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(basis_premi_koreksi_attendance)
        return res

    def action_print_report(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.payroll_report_wizard_action")
        action['context'] = {'default_payslip_ids': [(6,0,self.ids)]}
        return action