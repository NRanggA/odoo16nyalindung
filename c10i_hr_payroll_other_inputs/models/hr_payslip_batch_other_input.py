# -*- coding: utf-8 -*-
from odoo import models, fields, Command, api, _
from odoo.exceptions import UserError, ValidationError

import base64
import io
import pandas as pd
import numpy as np
from datetime import date,datetime

class HrPayslipBatchOtherInput(models.Model):
    _name = 'hr.payslip.batch.other.input'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payroll Batch Other Input'
    _order = 'date desc, id desc'

    name = fields.Char('Reference', required=True)
    date = fields.Date('Date', required=True)
    type_id = fields.Many2one('hr.payslip.other.input.type', string='Type', required=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirm')
    ], default='draft', string='Status')
    line_ids = fields.One2many('hr.payslip.other.input', 'batch_id', string='Lines')
    
    uploaded_file = fields.Binary(string='Upload File', attachment=True)
    uploaded_filename = fields.Char('Upload Filename')
    error_upload_msg = fields.Text('Error Message')

    def unlink(self):
        for batch in self:
            if batch.state!='draft':
                raise ValidationError(_("Cannot delete other input batch which its state not in draft state"))
        return super().unlink()

    def remove_line_to_upload(self):
        for batch in self:
            batch.line_ids.unlink()
            batch.uploaded_file = False
            batch.uploaded_filename = False
        return True

    def consume_file_excel(self):
        if not self.uploaded_file:
            raise UserError(_("Upload File Terlebih Dahulu"))
        
        excel_file = io.BytesIO(base64.b64decode(self.uploaded_file))
        df = pd.read_excel(excel_file, header=0, converters={'NIP':str,'AMOUNT':float})

        ######### Validation Column
        mandatory_column_to_check = ['NIP','AMOUNT']
        numeric_column_to_check = ['AMOUNT']
        # date_column_to_check = []
        error_msg_list = []
        for index, row in df.iterrows():
            for check_col1 in mandatory_column_to_check:
                if not row[check_col1]:
                    error_msg_list.append(f"Kolom {check_col1} pada baris {index} wajib diisi")
            for check_col2 in numeric_column_to_check:
                if not isinstance(row[check_col2], (float, np.floating)) and not isinstance(row[check_col2], (int, np.integer)):
                    error_msg_list.append(f"Kolom {check_col2} pada baris {index} wajib diisi dengan format Angka/Numeric")
            # for check_col3 in date_column_to_check:
            #     if not isinstance(row[check_col3], date) and not isinstance(row[check_col3], datetime):
            #         error_msg_list.append(f"Kolom {check_col3} pada baris {index} wajib diisi dengan format Tanggal")

        ######### Mapping Dict to Create
        to_create = []
        for index, row in df.iterrows():
            employee = self.env['hr.employee'].search([('no_induk', '=', row['NIP'])], limit=1)
            if not employee:
                error_msg_list.append(f"Karyawan dengan NIP {row['NIP']} tidak dapat ditemukan pada baris {index}")
            vals = {
                'employee_id': employee.id,
                'amount': row['AMOUNT'],
            }
            
            to_create.append(vals)

        if error_msg_list:
            self.error_upload_msg = "\n".join(error_msg_list)
        else:
            self.line_ids = [Command.create(val) for val in to_create]        
            self.error_upload_msg = ""
        return True

    def action_confirm(self):
        self.write({'state': 'confirm'})
    
    def action_set_draft(self):
        # Check for other inputs that already used inside hr.payslip
        for line in self.line_ids:
            if not line.payslip_id:
                continue
            if line.payslip_id.state == 'draft':
                line.payslip_id = False
                continue
            else:
                raise ValidationError(_("Other input %s for %s already used inside Payslip")%(line.type_id.name, line.employee_id.name))
        
        self.write({'state': 'draft'})