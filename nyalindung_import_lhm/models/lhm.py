from odoo import models, api, fields, _ 
from odoo.exceptions import UserError, ValidationError

import pandas as pd
import numpy as np
import io
import base64
import math
import logging


class lhm_transaction(models.Model):
    _inherit = 'lhm.transaction'

    # Field untuk kebutuhan import LHM line 
    is_import       = fields.Boolean('Import LHM line', default=False)
    file            = fields.Binary('File', attachment=True)
    error_message   = fields.Text('Error Message')

    def import_data(self):
        def cell_to_string(cell_value):
            if cell_value and (isinstance(cell_value, (float, np.floating)) or isinstance(cell_value, (int, np.integer))):
                return str(int(cell_value)) if not np.isnan(cell_value) else ''
            else:
                return cell_value.strip()
        
        # def handle_nan(value, default):
        #     if value is None or (isinstance(value, float) and math.isnan(value)):
        #         return default
        #     return value

        def handle_nan(value, default=None):
            # Periksa jika nilai None atau NaN
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return default
            # Periksa jika nilai adalah string kosong atau hanya berisi spasi
            if isinstance(value, str) and not value.strip():
                return default
            return value


        if self.is_import:
            if not self.file:
                raise UserError(_("Masukkan File Terlebih Dahulu"))      

        data = base64.b64decode(self.file)
        excel_file = io.BytesIO(data)
        df = pd.read_excel(excel_file, dtype={'NIK':str}, header=0)

        to_update = []
        error_message_list = []

        # Lacak NIK yang sudah diperbarui pada iterasi pertama
        processed_employees = {}
        # untuk melacak hk setiap employee
        hk_tracker          = {}

        for index, row in df.iterrows():
            if not self.id:
                raise ValidationError("Silakan Save Terlebih Dahulu!")

            employee_nik = cell_to_string(row.get('NIK', ''))
            
            # CHECK EMPLOYEE
            # Cari employee di master data
            ############################## BEGIN CHECK EMPLOYEE
            employee = self.env['hr.employee'].sudo().search([('no_induk', '=', employee_nik)], limit=1)
            if not employee:
                error_message_list.append(f"Baris ke- {index + 2} karyawan dengan NIK {employee_nik} dan nama {row.get('NAME', '')} tidak ditemukan di master data!")
                continue
            # CONTRACT EMPLOYEE
            if not employee.contract_id:
                error_message_list.append(f"Baris ke- {index + 2} kontrak karyawan dengan NIK {employee_nik} dan nama {row.get('NAME', '')} tidak ditemukan pada data LHM {self.name} saat ini!")
            ############################## END CHECK EMPLOYEE
            
            # CHECK TIPE LOKASI
            ############################## BEGIN CHECK TIPE LOKASI
            if not row.get('TIPE'): # Wajib isi Tipe Lokasi
                error_message_list.append(f"Baris ke- {index + 2} Tipe lokasi WAJIB diisi")
                continue

            type_location_found = self.env['lhm.location.type'].search([('code', '=', row.get('TIPE', ''))], limit=1)
            if not type_location_found:
                error_message_list.append(f"Baris ke- {index + 2} Tipe lokasi dengan kode {row.get('TIPE', '')} tidak ditemukan")
                continue
            ############################## END CHECK TIPE LOKASI
        
            # CHECK VARIETAS
            ############################## BEGIN CHECK VARIETAS
            varietas_code = handle_nan(row.get('VARIETAS', ''), 0)
            depend_on_varieties = type_location_found.code in ('FC','GC','IDC', 'PJ')
            if depend_on_varieties and not varietas_code:
                error_message_list.append(f"Baris ke-{index + 2} Tipe Lokasi {row.get('TIPE')} Wajib mengisi Varitas/ORG")
                continue
            
            if varietas_code:
                varietas_found = self.env['plant.varieties'].search([('code', '=', varietas_code)], limit=1)
                if not varietas_found:
                    error_message_list.append(f"Baris ke-{index + 2} Varietas dengan kode {varietas_code} tidak ditemukan!")
            else:
                varietas_found = None
            ############################## END CHECK VARIETAS
            
            if depend_on_varieties and varietas_found:
                ################## BEGIN CHECK LOKASI
                if not row.get('LOKASI',''):
                    error_message_list.append(f"Baris ke- {index + 2} Lokasi Wajib Diisi")
                    continue
                
                location = self.env['lhm.location'].search([('code', '=', row.get('LOKASI', '')),
                                        ('type_id','=',type_location_found.id),
                                        ('varieties_id','=',varietas_found.id)], limit=1)
                if not location:
                    error_message_list.append(f"Baris ke- {index + 2} Lokasi dengan kode {row.get('LOKASI', '')} tidak ditemukan untuk ORG {varietas_found.code} ({varietas_found.name})")
                    continue
                ################## END CHECK LOKASI

                ################## BEGIN CHECK AKTIVITAS
                if not row.get('AKTIVITAS',''):
                    error_message_list.append(f"Baris ke- {index + 2} Aktivitas Wajib Diisi")
                    continue

                if type_location_found.code=='PJ':
                    project_found = self.env['lhm.project'].search([('location_id','=',location.id)])
                    if project_found.activity_ids:
                        activity = project_found.activity_ids.filtered(lambda x: x.code==row.get('AKTIVITAS', ''))
                        if not activity:
                            error_message_list.append(f"Baris ke- {index + 2} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak ditemukan pada Project {project_found.code}!")
                        else:
                            activity = activity[0]
                    else:
                        error_message_list.append(f"Baris ke- {index + 2} Project {project_found.code} tidak memiliki daftar aktifitas")
                elif type_location_found.code in ('WS','VH','MA','NS','LB'):
                    activity = self.env['lhm.activity'].search([('type_id','=',type_location_found.id),('code','=',row.get('AKTIVITAS', ''))], limit=1)
                    if not activity:
                        error_message_list.append(f"Baris ke- {index + 2} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak ditemukan pada Tipe Lokasi {type_location_found.code}")
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
                        error_message_list.append(f"Baris ke- {index + 2} ORG {varietas_found.code} tidak memiliki Aktifitas yang terdaftar")
                        continue
                    activity = self.env['lhm.activity'].search([('code', '=', row.get('AKTIVITAS', '')),('type_id','=',type_location_found.id),('id','in',org_activities.ids)], limit=1)
                    if not activity:
                        error_message_list.append(f"Baris ke- {index + 2} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak ditemukan pada ORG {varietas_found.code}")
                ################## END CHECK AKTIVITAS
            else:
                ################## BEGIN CHECK LOKASI
                if not row.get('LOKASI',''):
                    error_message_list.append(f"Baris ke- {index + 2} Lokasi Wajib Diisi")
                    continue

                location = self.env['lhm.location'].search([('code', '=', row.get('LOKASI', '')),
                                        ('type_id','=',type_location_found.id)], limit=1)
                if not location:
                    error_message_list.append(f"Baris ke- {index + 2} Lokasi dengan kode {row.get('LOKASI', '')} tidak ditemukan pada Tipe Lokasi {type_location_found.code}")
                    continue
                ################## END CHECK LOKASI

                ################## BEGIN CHECK AKTIVITAS
                if not row.get('AKTIVITAS',''):
                    error_message_list.append(f"Baris ke- {index + 2} Aktivitas Wajib Diisi")
                    continue

                activity = self.env['lhm.activity'].search([('code', '=', row.get('AKTIVITAS', '')),
                                        ('type_id','=',type_location_found.id)], limit=1)
                if not activity:
                    error_message_list.append(f"Baris ke- {index + 2} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak ditemukan pada Tipe Lokasi {type_location_found.code}")
                
                ################## END CHECK AKTIVITAS
            
            ################### PUNYA RIAN ############################
            # ######## ======== Validasi LOKASI dan AKTIVITAS ======== ########
            # # Periksa jika lokasi tipe nya Project (project == True), maka aktivitas nya di ambil dari master data project (detail project Aktivitas)
            # # LOKASI
            # location = self.env['lhm.location'].search([('code', '=', row.get('LOKASI', ''))], limit=1)

            # if not location:
            #     error_message_list.append(f"Baris ke- {index + 2} Lokasi dengan kode {row.get('LOKASI', '')} tidak ditemukan!")
            # # AKAN DI CEK lagi
            # # # VALIDASI LOKASI BERDASARKAN TIPE LOKASI
            # # if type_location_found.code in ('WS','VH','MA','GC','MC','LB'):
            # #     locations = self.env['lhm.location'].search([('type_id','=',type_location_found.id)])
            # # else:
            # #     locations = self.env['lhm.location'].search([('id', '=', location.id), ('type_id','=',type_location_found.id),('varieties_id','=',varietas_found.id)])


            # if type_location_found and location:
            #     location_2 = self.env['lhm.location'].search([('id', '=', location.id),('type_id', '=', type_location_found.id)])
            #     if not location_2:
            #         # error_message_list.append(f"Baris ke- {index + 2} Tipe lokasi {row.get('TIPE', '')} tidak sesuai, dengan lokasi {row.get('LOKASI', '')}")
            #         error_message_list.append(f"Baris ke- {index + 2} Type pada Lokasi {row.get('LOKASI', '')} tidak sesuai dengan type yang diinput {row.get('TIPE', '')}")
            
            # if varietas_found and type_location_found and type_location_found.code not in ('PJ','NA','WS','VH','MA','NS'):
            #     location_3 = self.env['lhm.location'].search([
            #         ('code', '=', location.code),
            #         ('varieties_id', '=', varietas_found.id)
            #     ], limit=1)
            #     if not location_3:
            #         error_message_list.append(f"Baris ke- {index + 2} Varietas kode {row.get('VARIETAS', '')} tidak sesuai dengan lokasi kode {row.get('LOKASI', '')}!")
            
            # # AKTIVITAS
            # activity = self.env['lhm.activity'].search([('code', '=', row.get('AKTIVITAS', ''))], limit=1)
            # if not activity:
            #     error_message_list.append(f"Baris ke- {index + 2} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak ditemukan!")
            
            # if type_location_found:
            #     activity_2 = self.env['lhm.activity'].search([('code', '=', row.get('AKTIVITAS', '')), ('type_id', '=', type_location_found.id)], limit=1)
            #     if not activity_2:
            #         error_message_list.append(f"Baris ke- {index + 2} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak sesuai dengan tipe {row.get('TIPE', '')}!")
            ################### PUNYA RIAN ############################

            ######## ======== Validasi HK ======== ########
            # Validasi HK lebih dari 1
            work_day = handle_nan(row.get('HK', ''), 0)
            if work_day > 1:
                error_message_list.append(f"Baris ke- {index + 2} HK yang dimasukkan {row.get('HK', '')} tidak boleh lebih dari 1!")
            
            # Validasi total HK
            if employee.id not in hk_tracker:
                hk_tracker[employee.id] = 0
            hk_tracker[employee.id] += work_day

            if hk_tracker[employee.id] > 1:
                error_message_list.append(
                    f"Total HK untuk karyawan {employee.name} melebihi batas maksimum (1). HK saat ini: {hk_tracker[employee.id]} pada file yang di import."
                )
                # continue
            
            # Mendapatkan data absensi KJ
            absensi_kj = self.env['hr.attendance.type'].sudo().search([('code', '=', 'KJ')], limit=1)

            # Cek apakah employee sudah diproses pada iterasi pertama
            if employee_nik not in processed_employees:
                # Cari lhm_line yang ada dengan employee_id dan lhm_id saat ini
                lhm_line = self.env['lhm.transaction.line'].search([
                    ('employee_id', '=', employee.id),
                    ('lhm_id', '=', self.id)
                ], limit=1)

                if lhm_line:
                    # JIKA ADA DI DALAM LHM LINE MAKA AKAN DITAMBAHKAN
                    # Cek apakah dia employee yan tidak pada kemandoran yang sama namun tidak ada absen pada lhm_line
                    if employee not in self.kemandoran_id.employee_ids:
                        absensi = self.env['hr.attendance.sheet'].sudo().search([
                            ('employee_id', 'in', lhm_line.employee_id.ids),
                            ('date', '=', self.date),
                        ])
                        if absensi.check_in == False or absensi.check_out == False:
                            error_message_list.append(
                                f"Baris ke- {index + 2} Employee '{employee.name}' tidak lengkap secara absensi di tanggal '{absensi.date}' dengan tipe absensi '{absensi.type_id.code}', silahkan perbaiki absensi terlebih dahulu."
                            )
                    to_update.append((1, lhm_line.id, {
                        'date'              : self.date,      
                        'employee_id'       : employee.id,
                        'attendance_id'     : absensi_kj.id,
                        'location_type_id'  : type_location_found.id,
                        'varieties_id'      : varietas_found.id if varietas_found else None,
                        'location_id'       : location.id,
                        'activity_id'       : activity.id,
                        'is_borong'         : handle_nan(row.get('IS BORONG', ''), False),
                        'is_hasil_2'        : activity.is_hasil_2,
                        'work_day'          : work_day,
                        # 'product_id'        : varietas_found.product_id.id if activity.id in varietas_found.harvest_activity_ids.ids else False,
                        'product_id': (
                            varietas_found.product_id.id
                            if varietas_found and activity.id in (varietas_found.harvest_activity_ids.ids if varietas_found.harvest_activity_ids else [])
                            else False
                        ),
                        'hasil_1'           : handle_nan(row.get('HASIL 1', ''), 0),
                        'satuan_1'          : activity.uom_id.id if activity and activity.uom_id else False,
                        # 'product_id_2'      : varietas_found.secondary_product_id.id if activity.id in varietas_found.harvest_activity_ids.ids else False,
                        'product_id_2': (
                            varietas_found.secondary_product_id.id
                            if varietas_found and activity.id in (varietas_found.harvest_activity_ids.ids if varietas_found.harvest_activity_ids else [])
                            else False
                        ),
                        'hasil_2'           : handle_nan(row.get('HASIL 2', ''), 0),
                        'satuan_2'          : activity.uom2_id.id if activity and activity.uom2_id else False,
                    }))
                    processed_employees[employee_nik] = True
                else:
                    # BUAT ENTRY BARU JIKA EMPLOYEE TIDAK ADA DI LHM LINE 
                    # Cek apakah dia employee berada pada kemandoran yang sama namun tidak ada absen
                    if employee in self.kemandoran_id.employee_ids:
                        absensi_kemandoran = self.env['hr.attendance.sheet'].sudo().search([
                            ('employee_id', '=', employee.id),
                            ('date', '=', self.date),
                        ])
                        if absensi_kemandoran.check_in == False or absensi_kemandoran.check_out == False:
                            error_message_list.append(
                                f"Baris ke- {index + 2} Employee '{employee.name}' tidak lengkap secara absensi di tanggal '{absensi_kemandoran.date}' dengan tipe absensi '{absensi_kemandoran.type_id.code}', silahkan perbaiki absensi terlebih dahulu."
                            )
                    
                    if employee not in self.kemandoran_id.employee_ids:
                        absensi_not_kemandoran = self.env['hr.attendance.sheet'].sudo().search([
                            ('employee_id', '=', employee.id),
                            ('date', '=', self.date),
                        ])
                        if absensi_not_kemandoran.check_in == False or absensi_not_kemandoran.check_out == False:
                            error_message_list.append(
                                f"Baris ke- {index + 2} Employee '{employee.name}' tidak lengkap secara absensi di tanggal '{absensi_not_kemandoran.date}' dengan tipe absensi '{absensi_not_kemandoran.type_id.code}', silahkan perbaiki absensi terlebih dahulu."
                            )
                        
                        error_message_list.append(
                            f"Baris ke- {index + 2} Employee '{employee.name}' berasal dari kemandoran lain, silahkan 'Tambah Karyawan' terlebih dahulu !"
                        )

                    # Cek jika employee Tidak pada kemandoran yang sama
                    # if employee not in self.kemandoran_id.employee_ids:
                    #     error_message_list.append(
                    #         f"Baris ke- {index + 2} Employee '{employee.name}' berasal dari kemandoran lain, silahkan 'Tambah Karyawan' terlebih dahulu !"
                    #     )

                    # CEK DUPLIKASI DATA YANG SAMA PADA FILE YANG DI IMPORT dibedakan berdasarkan employee_id, location_id, activity_id
                    # Cek apakah employee_id dan location_id sudah ada di to_update
                    is_duplicate = False
                    for update in to_update:
                        # Ambil data yang ada dalam to_update
                        existing_employee_id = update[2].get('employee_id')
                        existing_location_id = update[2].get('location_id')
                        existing_activity_id = update[2].get('activity_id')

                        if str(existing_employee_id) == str(employee.id) and str(existing_location_id) == str(location.id) and str(existing_activity_id) == str(activity.id):
                            is_duplicate = True
                            break

                    if is_duplicate:
                        error_message_list.append(
                            f"Baris ke- {index + 2} Duplikat entri ditemukan untuk karyawan {employee.name} pada lokasi {location.code} dan aktivitas {activity.code} dalam data yang sedang diimpor!"
                        )
                        continue
                    
                    to_update.append((0, 0, {
                        'date'              : self.date,
                        'employee_id'       : employee.id,
                        'attendance_id'     : absensi_kj.id,
                        'location_type_id'  : type_location_found.id,
                        # 'varieties_id'      : varietas_found.id,
                        'varieties_id'      : varietas_found.id if varietas_found else None,
                        'location_id'       : location.id,
                        'activity_id'       : activity.id,
                        'is_borong'         : handle_nan(row.get('IS BORONG', ''), False),
                        # 'is_hasil_2'        : handle_nan(row.get('IS HASIL 2', ''), False),
                        'is_hasil_2'        : activity.is_hasil_2,
                        'work_day'          : work_day,
                        # 'product_id'        : varietas_found.product_id.id if activity.id == varietas_found.harvest_activity_id.id else False,
                        # 'product_id'        : varietas_found.product_id.id if activity.id in varietas_found.harvest_activity_ids.ids else False,
                        'product_id': (
                            varietas_found.product_id.id
                            if varietas_found and activity.id in (varietas_found.harvest_activity_ids.ids if varietas_found.harvest_activity_ids else [])
                            else False
                        ),
                        'hasil_1'           : handle_nan(row.get('HASIL 1', ''), 0),
                        'satuan_1'          : activity.uom_id.id if activity and activity.uom_id else False,
                        # 'product_id_2'      : varietas_found.secondary_product_id.id if activity.id == varietas_found.harvest_activity_id.id else False,
                        # 'product_id_2'      : varietas_found.secondary_product_id.id if activity.id in varietas_found.harvest_activity_ids.ids else False,
                        'product_id_2': (
                            varietas_found.secondary_product_id.id
                            if varietas_found and activity.id in (varietas_found.harvest_activity_ids.ids if varietas_found.harvest_activity_ids else [])
                            else False
                        ),
                        'hasil_2'           : handle_nan(row.get('HASIL 2', ''), 0),
                        'satuan_2'          : activity.uom2_id.id if activity and activity.uom2_id else False,
                    }))
            else:
                # I
                
                # Cek apakah employee_id dan location_id sudah ada di to_update
                is_duplicate = False
                for update in to_update:
                    # Ambil data yang ada dalam to_update
                    existing_employee_id = update[2].get('employee_id')
                    existing_location_id = update[2].get('location_id')
                    existing_activity_id = update[2].get('activity_id')


                    if str(existing_employee_id) == str(employee.id) and str(existing_location_id) == str(location.id) and str(existing_activity_id) == str(activity.id):
                        is_duplicate = True
                        break

                if is_duplicate:
                    error_message_list.append(
                        f"Baris ke- {index + 2} Duplikat entri ditemukan untuk karyawan {employee.name} pada lokasi {location.code} dan aktivitas {activity.code} dalam data yang sedang diimpor!"
                    )
                    continue

                to_update.append((0, 0, {
                    'date'              : self.date,
                    'employee_id'       : employee.id,
                    'attendance_id'     : absensi_kj.id,
                    'location_type_id'  : type_location_found.id,
                    # 'varieties_id'      : varietas_found.id,
                    'varieties_id'      : varietas_found.id if varietas_found else None,
                    'location_id'       : location.id,
                    'activity_id'       : activity.id,
                    'is_borong'         : handle_nan(row.get('IS BORONG', ''), False),
                    # 'is_hasil_2'        : handle_nan(row.get('IS HASIL 2', ''), False),
                    'is_hasil_2'        : activity.is_hasil_2,
                    'work_day'          : work_day,
                    # 'product_id'        : varietas_found.product_id.id if activity.id == varietas_found.harvest_activity_id.id else False,
                    # 'product_id'        : varietas_found.product_id.id if activity.id in varietas_found.harvest_activity_ids.ids else False,
                    'product_id': (
                            varietas_found.product_id.id
                            if varietas_found and activity.id in (varietas_found.harvest_activity_ids.ids if varietas_found.harvest_activity_ids else [])
                            else False
                    ),
                    'hasil_1'           : handle_nan(row.get('HASIL 1', ''), 0),
                    'satuan_1'          : activity.uom_id.id if activity and activity.uom_id else False,
                    # 'product_id_2'      : varietas_found.secondary_product_id.id if activity.id == varietas_found.harvest_activity_id.id else False,
                    # 'product_id_2'      : varietas_found.secondary_product_id.id if activity.id in varietas_found.harvest_activity_ids.ids else False,
                    'product_id_2': (
                            varietas_found.secondary_product_id.id
                            if varietas_found and activity.id in (varietas_found.harvest_activity_ids.ids if varietas_found.harvest_activity_ids else [])
                            else False
                    ),
                    'hasil_2'           : handle_nan(row.get('HASIL 2', ''), 0),
                    'satuan_2'          : activity.uom2_id.id if activity and activity.uom2_id else False,
                }))
        

        if error_message_list:
            error_message = '\n'.join(error_message_list)
            self.error_message = error_message
            raise ValidationError(_("Import data gagal dengan error berikut:\n%s") % error_message)

        self.lhm_line_ids = to_update
        return True
