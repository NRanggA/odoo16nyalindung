# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime, time

class NyBatchOtherInput(models.Model):
    _name = 'ny.payslip.batch.other.input'
    _description = 'Batch Payslip Other Input'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char('Reference', required=True)
    date = fields.Date('Date', required=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirm')
    ], default='draft', string='Status')
    line_ids = fields.One2many('ny.payslip.other.input', 'batch_id', string='Lines')
    
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
        df = pd.read_excel(excel_file, header=0)

        ######### Validation Column
        mandatory_column_to_check = ['NIP','TIPE','AMOUNT']
        numeric_column_to_check = ['AMOUNT']
        # date_column_to_check = []
        error_msg_list = []
        mapped_type =  {}
        type_not_found = []
        for index, row in df.iterrows():
            for check_col1 in mandatory_column_to_check:
                if not row[check_col1]:
                    error_msg_list.append(f"Kolom {check_col1} pada baris {index} wajib diisi")
            for check_col2 in numeric_column_to_check:
                if not isinstance(row[check_col2], (float, np.floating)) and not isinstance(row[check_col2], (int, np.integer)):
                    error_msg_list.append(f"Kolom {check_col2} pada baris {index} wajib diisi dengan format Angka/Numeric")
            if row['TIPE'] not in mapped_type and row['TIPE'] not in type_not_found:
                type_found = self.env['hr.payslip.other.input.type'].search([('name','=',row['TIPE'])], limit=1)
                if type_found:
                    mapped_type.update({row['TIPE']: type_found.id})
                else:
                    type_not_found.append(row['TIPE'])
                    error_msg_list.append(f"Kolom TIPE {row['TIPE']} Tidak dapat ditemukan")

        ######### Mapping Dict to Create
        to_create = []
        for index, row in df.iterrows():
            nip = row['NIP'].strip() if isinstance(row['NIP'],str) else str(row['NIP']).strip()    
            employee = self.env['hr.employee'].search([('no_induk', '=', nip)], limit=1)
            if not employee:
                error_msg_list.append(f"Karyawan dengan NIP {row['NIP']} tidak dapat ditemukan pada baris {index}")
            vals = {
                'employee_id': employee.id,
                'type_id': mapped_type.get(row['TIPE'], False),
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
        for rec in self:
            for type in rec.line_ids.type_id:
                values = {
                    'name': f"{type.name} Periode {rec.date_from.strftime('%d/%m/%Y')} s.d {rec.date_to.strftime('%d/%m/%Y')}",
                    'date': rec.date_to,
                    'type_id': type.id,
                }
                new_batch_oth_input = self.env['hr.payslip.batch.other.input'].create(values)
                
                for line in rec.line_ids.filtered(lambda x: x.type_id.id==type.id):
                    if not line.other_input_id and line.amount:
                        line_values = {
                            'batch_id': new_batch_oth_input.id,
                            'employee_id': line.employee_id.id,
                            'amount': line.amount
                        }
                        new_oth_input_line = self.env['hr.payslip.other.input'].create(line_values)
                        line.write({
                            'other_input_id': new_oth_input_line.id
                        })
                    else:
                        line.other_input_id.amount = line.amount
            rec.write({'state': 'confirm'})
    
    def action_set_draft(self):
        # Check for other inputs that already used inside hr.payslip
        # for line in self.line_ids:
        #     if not line.payslip_id:
        #         continue
        #     if line.payslip_id.state == 'draft':
        #         line.payslip_id = False
        #         continue
        #     else:
        #         raise ValidationError(_("Other input %s for %s already used inside Payslip")%(line.type_id.name, line.employee_id.name))
            
        self.write({'state': 'draft'})

class NyBatchOtherInputLine(models.Model):
    _name = 'ny.payslip.other.input'
    _description = 'Payslip Other Input'

    batch_id = fields.Many2one('ny.payslip.batch.other.input', string='Batch', ondelete='cascade')
    date = fields.Date(related='batch_id.date', store=True, string='Date')
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='restrict', required=True)
    type_id = fields.Many2one('hr.payslip.other.input.type', string='Type', ondelete='restrict', required=True)
    type_code = fields.Char(related='type_id.code', store=True, string='Code')
    amount = fields.Float()
    other_input_id = fields.Many2one('hr.payslip.other.input', string='Other Input')

    def unlink(self):
        for rec in self:
            if rec.batch_id.state!='draft':
                raise ValidationError(_("Cannot delete other input which is the state of its Batch are not in draft state"))
            # if rec.payslip_id:
            #     raise ValidationError(_("Cannot delete other input batch which is already linked with Payslip"))
        return super().unlink()