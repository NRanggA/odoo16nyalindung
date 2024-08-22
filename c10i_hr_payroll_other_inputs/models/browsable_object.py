#-*- coding:utf-8 -*-
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

from odoo.addons.c10i_hr_payroll.models.browsable_object import BrowsableObject

class OtherInput(BrowsableObject):
    """a class that will be used into the python code, mainly for usability purposes"""
    def sum(self, code, from_date, to_date=None):
        if to_date is None:
            to_date = fields.Date.today()
        self.env.cr.execute("""
            SELECT sum(amount) as sum
            FROM hr_payslip as hp, hr_payslip_other_input as poi
            WHERE hp.employee_id = %s AND hp.state in ('done', 'paid')
            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = poi.payslip_id AND poi.type_code = %s""",
            (self.employee_id, from_date, to_date, code))
        return self.env.cr.fetchone()[0] or 0.0