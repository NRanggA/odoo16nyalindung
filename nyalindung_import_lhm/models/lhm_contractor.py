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

        def handle_nan(value, default=None):
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return default
            if isinstance(value, str) and not value.strip():
                return default
            return value

        to_update = []
        error_message_list = []
        
        for row_no in range(1, sheet.nrows):  
            row = sheet.row(row_no)
            tanggal = datetime(*xlrd.xldate_as_tuple(row[0].value, workbook.datemode))
            # tanggal = row[0].value
            varieties_name = row[1].value
            tipe_name = row[2].value
            lokasi_name = row[3].value
            aktivitas_name = row[4].value
            uom_name = row[5].value
            hasil1 = row[6].value
            uom2_name = row[7].value
            hasil2 = row[8].value

            # CHECK TIPE LOKASI
            ############################## BEGIN CHECK TIPE LOKASI
            if not tipe_name: # Wajib isi Tipe Lokasi
                error_message_list.append(f"Baris ke- {row_no + 1} Tipe lokasi WAJIB diisi")
                continue

            type_location_found = self.env['lhm.location.type'].search([('code', '=', tipe_name)], limit=1)
            if not type_location_found:
                error_message_list.append(f"Baris ke- {row_no + 1} Tipe lokasi dengan kode {tipe_name} tidak ditemukan")
                continue
            ############################## END CHECK TIPE LOKASI
        
            # CHECK VARIETAS
            ############################## BEGIN CHECK VARIETAS
            varietas_code = handle_nan(varieties_name, 0)
            depend_on_varieties = type_location_found.code in ('FC','GC','IDC', 'PJ')
            if depend_on_varieties and not varietas_code:
                error_message_list.append(f"Baris ke-{row_no + 1} Tipe Lokasi {tipe_name} Wajib mengisi Varitas/ORG")
                continue
            
            if varietas_code:
                varietas_found = self.env['plant.varieties'].search([('code', '=', varietas_code)], limit=1)
                if not varietas_found:
                    error_message_list.append(f"Baris ke-{row_no + 1} Varietas dengan kode {varietas_code} tidak ditemukan!")
            else:
                varietas_found = None
            ############################## END CHECK VARIETAS
            
            if depend_on_varieties and varietas_found:
                ################## BEGIN CHECK LOKASI
                if not lokasi_name:
                    error_message_list.append(f"Baris ke- {row_no + 1} Lokasi Wajib Diisi")
                    continue
                
                location = self.env['lhm.location'].search([('code', '=', lokasi_name),
                                        ('type_id','=',type_location_found.id),
                                        ('varieties_id','=',varietas_found.id)], limit=1)
                if not location:
                    error_message_list.append(f"Baris ke- {row_no + 1} Lokasi dengan kode {lokasi_name} tidak ditemukan untuk ORG {varietas_found.code} ({varietas_found.name})")
                    continue
                ################## END CHECK LOKASI

                ################## BEGIN CHECK AKTIVITAS
                if not aktivitas_name:
                    error_message_list.append(f"Baris ke- {row_no + 1} Aktivitas Wajib Diisi")
                    continue

                if type_location_found.code=='PJ':
                    project_found = self.env['lhm.project'].search([('location_id','=',location.id)])
                    if project_found.activity_ids:
                        activity = project_found.activity_ids.filtered(lambda x: x.code==aktivitas_name)
                        if not activity:
                            error_message_list.append(f"Baris ke- {row_no + 1} Aktivitas dengan kode {aktivitas_name} tidak ditemukan pada Project {project_found.code}!")
                        else:
                            activity = activity[0]
                    else:
                        error_message_list.append(f"Baris ke- {row_no + 1} Project {project_found.code} tidak memiliki daftar aktifitas")
                elif type_location_found.code in ('WS','VH','MA','NS','LB'):
                    activity = self.env['lhm.activity'].search([('type_id','=',type_location_found.id),('code','=',aktivitas_name)], limit=1)
                    if not activity:
                        error_message_list.append(f"Baris ke- {row_no + 1} Aktivitas dengan kode {aktivitas_name} tidak ditemukan pada Tipe Lokasi {type_location_found.code}")
                else: # Plantation, GC, IDC
                    org_activities = self.env['lhm.activity']
                    if varietas_found.harvest_activity_ids:
                        org_activities |= varietas_found.harvest_activity_ids
                    if varietas_found.upkeep_activity_ids:
                        org_activities |= varietas_found.upkeep_activity_ids
                    if varietas_found.general_charges_activity_ids:
                        org_activities |= varietas_found.general_charges_activity_ids
                    if varietas_found.indirect_cost_activity_ids:
                        org_activities |= varietas_found.indirect_cost_activity_ids
                    if not org_activities:
                        error_message_list.append(f"Baris ke- {row_no + 1} ORG {varietas_found.code} tidak memiliki Aktifitas yang terdaftar")
                        continue
                    activity = self.env['lhm.activity'].search([('code', '=', aktivitas_name),('type_id','=',type_location_found.id),('id','in',org_activities.ids)], limit=1)
                    if not activity:
                        error_message_list.append(f"Baris ke- {row_no + 1} Aktivitas dengan kode {aktivitas_name} tidak ditemukan pada ORG {varietas_found.code}")
                ################## END CHECK AKTIVITAS
            else:
                ################## BEGIN CHECK LOKASI
                if not lokasi_name:
                    error_message_list.append(f"Baris ke- {row_no + 1} Lokasi Wajib Diisi")
                    continue

                location = self.env['lhm.location'].search([('code', '=', lokasi_name),
                                        ('type_id','=',type_location_found.id)], limit=1)
                if not location:
                    error_message_list.append(f"Baris ke- {row_no + 1} Lokasi dengan kode {lokasi_name} tidak ditemukan pada Tipe Lokasi {type_location_found.code}")
                    continue
                ################## END CHECK LOKASI

                ################## BEGIN CHECK AKTIVITAS
                if not aktivitas_name:
                    error_message_list.append(f"Baris ke- {row_no + 1} Aktivitas Wajib Diisi")
                    continue

                activity = self.env['lhm.activity'].search([('code', '=', aktivitas_name),
                                        ('type_id','=',type_location_found.id)], limit=1)
                if not activity:
                    error_message_list.append(f"Baris ke- {row_no + 1} Aktivitas dengan kode {aktivitas_name} tidak ditemukan pada Tipe Lokasi {type_location_found.code}")
                
                ################## END CHECK AKTIVITAS

            # START CHECK NYA MAUL
            # varieties_id = self.env['plant.varieties'].search([('code', '=', varieties_name)], limit=1)
            # if not varieties_id:
            #     raise UserError(_(f"Varietas '{varieties_name}' tidak ditemukan dalam database."))

            # location_type_id = self.env['lhm.location.type'].search([('code', '=', tipe_name)], limit=1)
            # if not location_type_id:
            #     raise UserError(_(f"Tipe lokasi '{tipe_name}' tidak ditemukan dalam database."))

            # lokasi_code = str(lokasi_name).rstrip('.0') if isinstance(lokasi_name, (int, float)) else lokasi_name
            # location_id = self.env['lhm.location'].search([('code', '=', lokasi_code)], limit=1)
            # if not location_id:
            #     raise UserError(_(f"Lokasi '{lokasi_name}' tidak ditemukan dalam database."))

            # activity_code = str(aktivitas_name).rstrip('.0') if isinstance(aktivitas_name, (int, float)) else aktivitas_name
            # activity_id = self.env['lhm.activity'].search([('code', '=', activity_code)], limit=1)
            # if not activity_id:
            #     raise UserError(_(f"Aktivitas '{aktivitas_name}' tidak ditemukan dalam database."))
            #END CHECK NYA MAUL

            if uom_name:
                uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
                if not uom_id:
                    raise UserError(_(f"UoM '{uom_name}' tidak ditemukan dalam database."))
            else:
                uom_id = False

            if uom2_name:
                uom2_id = self.env['uom.uom'].search([('name', '=', uom2_name)], limit=1)
                if not uom2_id:
                    raise UserError(_(f"UoM 2 '{uom2_name}' tidak ditemukan dalam database."))
            else:
                uom2_id = False

            wage_borongan = self.env['lhm.wage.borongan.contractor'].search([
                ('activity_id', '=', activity.id)
            ], limit=1)

            unit_price = 0.0
            if wage_borongan:
                if wage_borongan.price:
                    unit_price = wage_borongan.price

            to_update.append({
                'contractor_id': self.id, 
                'date': tanggal,
                'varieties_id': varietas_found.id if varietas_found else None,
                'location_type_id': type_location_found.id,
                'location_id': location.id,
                'activity_id': activity.id,
                'uom_id': uom_id.id if uom_id else None,
                'nilai': hasil1,
                'uom2_id': uom2_id.id if uom2_id else None,
                'nilai2': hasil2,
                'unit_price': unit_price, 
            })
        if error_message_list:
            error_message = '\n'.join(error_message_list)
            # self.error_message = error_message
            raise ValidationError(_("Import data gagal dengan error berikut:\n%s") % error_message)

        self.env['lhm.contractor.line'].create(to_update)

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
        
            if self.env.context.get('is_harian'):
                location_type_id = self.env['lhm.location.type'].search([('code', '=', type_name)], limit=1)
                if not location_type_id:
                    raise UserError(_(f"Tipe lokasi '{type_name}' tidak ditemukan dalam database."))

                varieties_id = self.env['plant.varieties'].search([('code', '=', varieties_name)], limit=1)
                if not varieties_id:
                    raise UserError(_(f"Varietas '{varieties_name}' tidak ditemukan dalam database."))

                lokasi_code = str(lokasi_name).rstrip('.0') if isinstance(lokasi_name, (int, float)) else lokasi_name
                location_id = self.env['lhm.location'].search([('code', '=', lokasi_code)], limit=1)
                if not location_id:
                    raise UserError(_(f"Lokasi '{lokasi_name}' tidak ditemukan dalam database."))

                activity_code = str(aktivitas_name).rstrip('.0') if isinstance(aktivitas_name, (int, float)) else aktivitas_name
                activity_id = self.env['lhm.activity'].search([('code', '=', activity_code)], limit=1)
                if not activity_id:
                    raise UserError(_(f"Aktivitas '{aktivitas_name}' tidak ditemukan dalam database."))

                if product_name:
                    product_id = self.env['product.product'].search([('name', '=', product_name)], limit=1)
                    if not product_id:
                        raise UserError(_(f"Produk '{product_name}' tidak ditemukan dalam database."))
                else:
                    product_id = False
                
                if uom_name:
                    uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
                    if not uom_id:
                        raise UserError(_(f"UoM '{uom_name}' tidak ditemukan dalam database."))
                else:
                    uom_id = False

                if product_2_name:
                    product_id_2 = self.env['product.product'].search([('name', '=', product_2_name)], limit=1)
                    if not product_id_2:
                        raise UserError(_(f"Produk 2 '{product_2_name}' tidak ditemukan dalam database."))
                else:
                    product_id_2 = False

                if uom2_name:
                    uom2_id = self.env['uom.uom'].search([('name', '=', uom2_name)], limit=1)
                    if not uom2_id:
                        raise UserError(_(f"UoM 2 '{uom2_name}' tidak ditemukan dalam database."))
                else:
                    uom2_id = False

                wage_borongan = self.env['lhm.wage.borongan.contractor'].search([
                    ('activity_id', '=', activity_id.id)
                ], limit=1)

                unit_price = None
                if wage_borongan:
                    if wage_borongan.price:
                        unit_price = wage_borongan.price
                
                unit_price_2 = None
                if wage_borongan:
                    if wage_borongan.price2:
                        unit_price_2 = wage_borongan.price2

                self.env['lhm.contractor.line'].create({
                    'contractor_id': self.id, 
                    'location_type_id': location_type_id.id, 
                    'varieties_id': varieties_id.id, 
                    'location_id': location_id.id,
                    'activity_id': activity_id.id,
                    'product_id': product_id.id if product_id else None,
                    'uom_id': uom_id.id if uom_id else None,
                    'nilai': nilai if nilai else None,
                    'product_id_2': product_id_2.id if product_id_2 else None,
                    'uom2_id': uom2_id.id if uom2_id else None,
                    'nilai2': nilai2 if nilai2 else None,
                    'unit_price': unit_price,
                    'unit_price_2': unit_price_2,
                })