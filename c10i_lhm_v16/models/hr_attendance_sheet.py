from odoo import models, fields, api, _

class HrAttendanceSheet(models.Model):
    _inherit = 'hr.attendance.sheet'

    kemandoran_id = fields.Many2one(related='employee_id.kemandoran_id', string='Kemandoran', store=True)
    