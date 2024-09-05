# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from odoo.addons.c10i_hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.addons.c10i_hr_payroll_pph.models.browsable_object import Payslips2

import logging
_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    pph_slip_id = fields.Many2one('hr.payslip.pph', string='Perhitungan PPH')

    def create_slip_pph21(self):
        pkp_progresif = self.env['hr.pkp'].search([], order='sequence asc')
        for slip in self:
            # Prepare PKP Lines
            prev_range_stop = 0.0
            rate_denda = slip.employee_id._get_percent_denda() if not slip.employee_id._check_npwp() else 0.0
            
            pph21_progresif_lines = []
            
            for pkp in pkp_progresif:
                pph21_progresif_lines.append((0,0,{
                    'pkp_id': pkp.id,
                    'prev_range_stop': prev_range_stop,
                    'range_start': pkp.range_start,
                    'range_stop': pkp.range_stop,
                    'rate': pkp.percentage / 100.0,
                    'rate_denda': rate_denda,
                    }))
                prev_range_stop = pkp.range_stop

            to_create_vals = {
                'slip_id': slip.id,
                'ptkp_id': slip.employee_id.ptkp_id.id,
                'date': slip.date_to,
                'first_contract_date': slip.employee_id.first_contract_date,
                'termination_date': slip.employee_id.termination_date,
            }
            to_create_vals.update({
                    'pph_progresif_line_ids': pph21_progresif_lines,
                })
            new_pph21_slip = self.env['hr.payslip.pph'].create(to_create_vals)

            slip.pph_slip_id = new_pph21_slip.id

    @api.model_create_multi
    def create(self, vals_list):
        payslips = super().create(vals_list)

        pkp_progresif = self.env['hr.pkp'].search([], order='sequence asc')
        for slip in payslips:
            prev_range_stop = 0.0
            rate_denda = slip.employee_id._get_percent_denda() if not slip.employee_id._check_npwp() else 0.0
            
            pph21_progresif_lines = []
            
            for pkp in pkp_progresif:
                pph21_progresif_lines.append((0,0,{
                    'pkp_id': pkp.id,
                    'prev_range_stop': prev_range_stop,
                    'range_start': pkp.range_start,
                    'range_stop': pkp.range_stop,
                    'rate': pkp.percentage / 100.0,
                    'rate_denda': rate_denda,
                    }))
                prev_range_stop = pkp.range_stop

            to_create_vals = {
                'slip_id': slip.id,
                'ptkp_id': slip.employee_id.ptkp_id.id,
                'date': slip.date_to,
                'first_contract_date': slip.employee_id.first_contract_date,
                'termination_date': slip.employee_id.termination_date,
            }
            to_create_vals.update({
                'pph_progresif_line_ids': pph21_progresif_lines,
            })
            new_pph21_slip = self.env['hr.payslip.pph'].create(to_create_vals)

            slip.pph_slip_id = new_pph21_slip.id

        return payslips

    # Override method _get_localdict on hr_payroll.models.hr_payslip.HrPayslip._get_localdict
    # 1. To add BrowseableObject for payslip_lines which will be used for PPH 21 only
    # 2. To add BrowseableObject for income_adjustment (other income) which will be used to add other source 
    #    for getting result on slip python expression
    def _get_localdict(self):
        self.ensure_one()
        localdict = super()._get_localdict()
        localdict = {
            **localdict,
            **{
                'pph_types': BrowsableObject(self.employee_id.id, {}, self.env),
                'payslip': Payslips2(self.employee_id.id, self, self.env),
            }
        }
        return localdict

    def action_view_payslip_pph(self):
        result = self.env["ir.actions.actions"]._for_xml_id('c10i_hr_payroll_pph.hr_payslip_pph_action')
        res = self.env.ref('c10i_hr_payroll_pph.hr_payslip_pph_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
        else:
            result['views'] = form_view
        result['res_id'] = self.pph_slip_id.id
        return result