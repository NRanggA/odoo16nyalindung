#-*- coding:utf-8 -*-
from odoo import fields
from odoo.addons.c10i_hr_payroll.models.browsable_object import Payslips

import logging
_logger = logging.getLogger(__name__)

class Payslips2(Payslips):
    def prepare_pph21_values(self, fix_income, jht):
        _logger.info(":::::::::::::::::::::::::::::::::: PPH21 ::::::::: get employee")
        employee = self.env['hr.employee'].browse(self.employee_id)
        this_period_jht = jht
        # Prev of PPH 21 slips paid this Month
        _logger.info(":::::::::::::::::::::::::::::::::: PPH21 ::::::::: start query 1")
        self.env.cr.execute("""
            SELECT 
                sum(case when hp.credit_note = True then (-hpp.current_income_base_pph_amount) else (hpp.current_income_base_pph_amount) end) as income_base_pph_amount,
                sum(case when hp.credit_note = True then (-hpp.pph_amount) else (hpp.pph_amount) end) as paid_pph_amount
            FROM 
                hr_payslip hp, hr_payslip_pph hpp
            WHERE
                hp.id = hpp.slip_id AND hp.employee_id = %s AND hp.state = 'done' 
                AND extract(month from hpp.date)=%s AND extract(year from hpp.date)=%s
            """,
            (self.employee_id, self.date_to.month, self.date_to.year))
        _logger.info(":::::::::::::::::::::::::::::::::: PPH21 ::::::::: query 1 done")
        prev = self.env.cr.dictfetchone()

        # Prev of PPH 21 slips paid all months this year
        _logger.info(":::::::::::::::::::::::::::::::::: PPH21 ::::::::: start query 2")
        self.env.cr.execute("""
            SELECT 
                sum(case when hp.credit_note = True then (-hpp.current_income_base_pph_amount) else (hpp.current_income_base_pph_amount) end) as income_base_pph_amount,
                sum(case when hp.credit_note = True then (-hpp.current_jht) else (hpp.current_jht) end) as jht_amount,
                sum(case when hp.credit_note = True then (-hpp.pph_amount) else (hpp.pph_amount) end) as paid_pph_amount
            FROM 
                hr_payslip hp, hr_payslip_pph hpp
            WHERE
                hp.id = hpp.slip_id AND hp.employee_id = %s AND hp.state = 'done' 
                AND extract(year from hpp.date)=%s
            """,
            (self.employee_id, self.date_to.year))
        _logger.info(":::::::::::::::::::::::::::::::::: PPH21 ::::::::: query 2 done")
        prev_all = self.env.cr.dictfetchone()
        
        to_update = {
            'date': self.date_to,
            'termination_date': employee.termination_date,
            'employee_id': employee.id,
            'ptkp_id': employee.ptkp_id.id,
            'ptkp_amount': employee.ptkp_id.value,

            'current_income_base_pph_amount': fix_income,
            'current_jht': this_period_jht,
            
            'prev_income_base_pph_amount': (prev.get('income_base_pph_amount',0.0) if prev.get('income_base_pph_amount') is not None else 0.0),
            'this_month_pph_paid_amount': (prev.get('paid_pph_amount',0.0) if prev.get('paid_pph_amount') is not None else 0.0),

            'prev_pph_paid_amount': prev_all.get('paid_pph_amount',0.0) if prev_all.get('paid_pph_amount') is not None else 0.0,
            'prev_income_this_year': prev_all.get('income_base_pph_amount',0.0) if prev_all.get('income_base_pph_amount') is not None else 0.0,
            'a_year_jht': 
                (prev_all.get('jht_amount',0.0) if prev_all.get('jht_amount') is not None else 0.0) \
                + this_period_jht,
        }
        _logger.info(f":::::::::::::::::::::::::::::::::: PPH21 ::::::::: HASIL SUM {str(to_update)}")
        
        _logger.info(f":::::::::::::::::::::::::::::::::: PPH21 ::::::::: SLIP PPH 1 {str(self.pph_slip_id)}")
        slip_pph21 = self.env['hr.payslip.pph'].browse(self.pph_slip_id.id)
        _logger.info(f":::::::::::::::::::::::::::::::::: PPH21 ::::::::: SLIP PPH 2 {str(slip_pph21.id)}")
        if slip_pph21:
            slip_pph21.write(to_update)
            _logger.info(f":::::::::::::::::::::::::::::::::: PPH21 ::::::::: AFTER WRITE {str(slip_pph21.pph_amount)}")
            return slip_pph21.pph_amount
        else:
            return 0.0

    def compute_pp58(self, gross_income):
        employee = self.env['hr.employee'].browse(self.employee_id)
        range_pph = self.env['hr.rate.pp58'].sudo().search([
                        ('pp58_tier_type','=',employee.ptkp_id.pp58_tier_type),
                        ('range_start','<',gross_income),
                        ('range_stop','>=',gross_income)], limit=1)
        rate_pph = range_pph.percentage if range_pph else 0.0
        return (gross_income * rate_pph / 100.0)