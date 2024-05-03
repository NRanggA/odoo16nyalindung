# -*- coding: utf-8 -*-
##############################################################################
#
#    deby@C10i, Consult10Indonesia
#    Copyright (C) 2018 Consult10Indonesia
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WizardMoveEmployeeAll(models.TransientModel):
    _name = "wizard.move.employee.all"
    _description = "Wizard Move Employee All"

    name = fields.Char("Name", default="Perpindahan Karyawan")
    line_ids = fields.One2many(comodel_name="wizard.move.employee", inverse_name="parent_id", string="Details")

class WizardMoveEmployee(models.TransientModel):
    _name = "wizard.move.employee"
    _description = "Wizard Move Employee"

    name = fields.Char("Name", default="Perpindahan Karyawan")
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Nama Karyawan")
    src_foreman_id = fields.Many2one(comodel_name="hr.foreman", string="Asal Kemandoran")
    dest_foreman_id = fields.Many2one(comodel_name="hr.foreman", string="Tujuan Kemandoran")
    parent_id = fields.Many2one(comodel_name="wizard.move.employee.all", string="Parent")
    date = fields.Date(string='Tanggal Pengajuan Pindah', default=lambda self: fields.Date.today())
    moved_date = fields.Date(string='Tanggal Pindah')
    note = fields.Text("Catatan")

    @api.model
    def default_get(self, fields):
        res = super(WizardMoveEmployee, self).default_get(fields)
        record_ids = self._context.get('active_ids')
        if record_ids:
            data = self.env['hr.employee'].browse(record_ids)
            if data and data.kemandoran_id:
                res.update({
                    'src_foreman_id': data.kemandoran_id.id,
                    'employee_id': data.id
                })
        return res

    # @api.multi
    def move_employee(self):
        emp_move_obj = self.env['hr.foreman.movement']
        if self.employee_id and self.dest_foreman_id and self.date:
            values = {
                'name': 'Moved From ' + str(self.src_foreman_id.name or "") + ' To ' + str(self.dest_foreman_id.name or ""),
                'date': self.date,
                'moved_date': False,
                'employee_id': self.employee_id.id,
                'src_foreman_id': self.src_foreman_id.id,
                'dest_foreman_id': self.dest_foreman_id.id,
                'note': self.note or "",
                'state': 'ongoing',
            }
            new_move = emp_move_obj.create(values)
            if new_move:
                self.employee_id.write({'move_state': 'ongoing'})
