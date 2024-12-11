from odoo import models, api, fields, _ 
from odoo.exceptions import UserError, ValidationError

import pandas as pd
import numpy as np
import io
import base64
import math
import logging
import xlrd
from datetime import datetime

class LHMContractor(models.Model):
    _inherit = 'lhm.contractor'

    is_import = fields.Boolean('Is Import', default=False)
    is_import_harian = fields.Boolean('Is Import', default=False)
    file = fields.Binary('File Import')

    def import_data(self):
        if not self.file:
            raise UserError(_("Silakan pilih file Excel untuk diimport."))

        file_data = base64.b64decode(self.file)
        
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0) 
        
        for row_no in range(1, sheet.nrows):  
            row = sheet.row(row_no)
            tanggal = datetime(*xlrd.xldate_as_tuple(row[0].value, workbook.datemode))
            varieties_name = row[1].value
            tipe_name = row[2].value
            lokasi_name = row[3].value
            aktivitas_name = row[4].value
            uom_name = row[5].value
            hasil1 = row[6].value
            uom2_name = row[7].value
            hasil2 = row[8].value

            varieties_id = self.env['plant.varieties'].search([('code', '=', varieties_name)], limit=1)
            if not varieties_id:
                raise UserError(_(f"Varietas '{varieties_name}' tidak ditemukan dalam database."))

            location_type_id = self.env['lhm.location.type'].search([('code', '=', tipe_name)], limit=1)
            if not location_type_id:
                raise UserError(_(f"Tipe lokasi '{tipe_name}' tidak ditemukan dalam database."))

            location_id = self.env['lhm.location'].search([('code', '=', lokasi_name)], limit=1)
            if not location_id:
                raise UserError(_(f"Lokasi '{lokasi_name}' tidak ditemukan dalam database."))

            activity_id = self.env['lhm.activity'].search([('code', '=', aktivitas_name)], limit=1)
            if not activity_id:
                raise UserError(_(f"Aktivitas '{aktivitas_name}' tidak ditemukan dalam database."))

            uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
            if not uom_id:
                raise UserError(_(f"Satuan UOM '{uom_name}' tidak ditemukan dalam database."))

            uom2_id = self.env['uom.uom'].search([('name', '=', uom2_name)], limit=1)
            if not uom2_id:
                raise UserError(_(f"Satuan UOM kedua '{uom2_name}' tidak ditemukan dalam database."))

            wage_borongan = self.env['lhm.wage.borongan.contractor'].search([
                ('activity_id', '=', activity_id.id)
            ], limit=1)

            unit_price = 0.0
            if wage_borongan:
                if wage_borongan.price:
                    unit_price = wage_borongan.price

            self.env['lhm.contractor.line'].create({
                'contractor_id': self.id, 
                'date': tanggal,
                'varieties_id': varieties_id.id,
                'location_type_id': location_type_id.id,
                'location_id': location_id.id,
                'activity_id': activity_id.id,
                'uom_id': uom_id.id,
                'nilai': hasil1,
                'uom2_id': uom2_id.id,
                'nilai2': hasil2,
                'unit_price': unit_price, 
            })

    def import_data_harian(self):
        if not self.file:
            raise UserError(_("Silakan pilih file Excel untuk diimport."))

        file_data = base64.b64decode(self.file)
        
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0) 
        
        for row_no in range(1, sheet.nrows):  
            row = sheet.row(row_no)
            
            type_name = row[0].value
            varieties_name = row[1].value
            lokasi_name = row[2].value
            aktivitas_name = row[3].value
            product_name = row[4].value
            uom_name = row[5].value
            nilai = row[6].value
            product_2_name = row[7].value
            uom2_name = row[8].value
            nilai2 = row[9].value

            location_type_id = self.env['lhm.location.type'].search([('code', '=', type_name)], limit=1)
            if not location_type_id:
                raise UserError(_(f"Tipe lokasi '{type_name}' tidak ditemukan dalam database."))

            varieties_id = self.env['plant.varieties'].search([('code', '=', varieties_name)], limit=1)
            if not varieties_id:
                raise UserError(_(f"Varietas '{varieties_name}' tidak ditemukan dalam database."))

            location_id = self.env['lhm.location'].search([('code', '=', lokasi_name)], limit=1)
            if not location_id:
                raise UserError(_(f"Lokasi '{lokasi_name}' tidak ditemukan dalam database."))

            activity_id = self.env['lhm.activity'].search([('code', '=', aktivitas_name)], limit=1)
            if not activity_id:
                raise UserError(_(f"Aktivitas '{aktivitas_name}' tidak ditemukan dalam database."))

            product_id = self.env['product.product'].search([('name', '=', product_name)], limit=1)
            if not product_id:
                raise UserError(_(f"Produk '{product_name}' tidak ditemukan dalam database."))

            uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
            if not uom_id:
                raise UserError(_(f"Satuan UOM '{uom_name}' tidak ditemukan dalam database."))

            product_id_2 = self.env['product.product'].search([('name', '=', product_2_name)], limit=1)
            if not product_id_2:
                raise UserError(_(f"Produk kedua '{product_2_name}' tidak ditemukan dalam database."))

            uom2_id = self.env['uom.uom'].search([('name', '=', uom2_name)], limit=1)
            if not uom2_id:
                raise UserError(_(f"Satuan UOM kedua '{uom2_name}' tidak ditemukan dalam database."))

            wage_borongan = self.env['lhm.wage.borongan.contractor'].search([
                ('activity_id', '=', activity_id.id)
            ], limit=1)

            unit_price = 0.0
            if wage_borongan:
                if wage_borongan.price:
                    unit_price = wage_borongan.price
            
            unit_price_2 = 0.0
            if wage_borongan:
                if wage_borongan.price2:
                    unit_price_2 = wage_borongan.price2

            self.env['lhm.contractor.line'].create({
                'contractor_id': self.id, 
                'location_type_id': location_type_id.id, 
                'varieties_id': varieties_id.id, 
                'location_id': location_id.id,
                'activity_id': activity_id.id,
                'product_id': product_id.id,
                'uom_id': uom_id.id,
                'nilai': nilai,
                'product_id_2': product_id_2.id,
                'uom2_id': uom2_id.id,
                'nilai2': nilai2,
                'unit_price': unit_price,
                'unit_price_2': unit_price_2,
            })