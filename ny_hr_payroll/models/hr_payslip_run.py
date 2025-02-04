# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.addons.c10i_plantation_payroll.models.browsable_object import Payslips3

from datetime import date, datetime, time

class BatchHrPayslip(models.Model):
    _inherit = 'hr.payslip.run'
    
    def action_print_report(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.payroll_report_wizard_action")
        action['context'] = {'default_payslip_ids': [(6,0,self.slip_ids.ids)]}
        return action

    def action_print_report_detail(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.payroll_report_detail_wizard_action")
        action['context'] = {'default_payslip_ids': [(6,0,self.slip_ids.ids)]}
        return action
    
    def action_edit_payroll_gc_distribution(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_hr_payroll.action_edit_payroll_gc_distribution")
        # action['domain'] = [('varieties_id.name','=','Karet')]
        return action