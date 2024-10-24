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
    is_import = fields.Boolean('Import LHM line', default=False)
    file = fields.Binary('File', attachment=True)
    error_message = fields.Text('Error Message')

    def import_data(self):
        def cell_to_string(cell_value):
            if cell_value and (isinstance(cell_value, (float, np.floating)) or isinstance(cell_value, (int, np.integer))):
                return str(int(cell_value)) if not np.isnan(cell_value) else ''
            else:
                return cell_value.strip()
        
        # Fungsi untuk menangani NaN dan mengembalikan nilai default
        def handle_nan(value, default):
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return default
            return value
        
        if self.is_import:
            if not self.file:
                raise UserError(_("Masukkan File Terlebih Dahulu"))      

        data        = base64.b64decode(self.file)
        excel_file  = io.BytesIO(data)
        df          = pd.read_excel(excel_file, header=0)

        to_update   = []
        error_message_list = []

        for index, row in df.iterrows():

            if not self.id:
                raise ValidationError("Silakan Save Terlebih Dahulu !")

            lhm_line = self.env['lhm.transaction.line'].search([('employee_id.no_induk', '=', cell_to_string(row.get('NIK', ''))), ('lhm_id', '=', self.id)], limit=1)
            if not lhm_line:
                error_message_list.append(f"Baris ke- {index + 2} karyawan dengan nip {row.get('NIK', '')} dan nama {row.get('NAME', '')} tidak ditemukan pada LHM {self.name} saat ini!")
            if not lhm_line.employee_id.contract_id:
                error_message_list.append(f"Baris ke- {index + 2} kontrak karyawan dengan nip {row.get('NIK', '')} dan nama {row.get('NAME', '')} tidak ditemukan pada data LHM {self.name} saat ini!")

            # ========== ATTENDANCE ==============
            # ==================================
            attendance_sheet = self.env['hr.attendance.sheet'].search([('employee_id', '=', lhm_line.employee_id.id), ('check_in', '!=', False), ('date', '=', self.date)], limit=1)
            if lhm_line and not attendance_sheet:
                error_message_list.append(f"Baris ke- {index + 2} absensi karyawan dengan nip {lhm_line.employee_id.no_induk} dan nama {row.get('NAME', '')} tidak ditemukan!")
            
            # ========== TIPE LOKASI ==============
            # ==================================
            type_location = self.env['lhm.location.type'].search([('code', '=', row.get('TIPE', ''))], limit=1)
            if lhm_line and not type_location:
                error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')} Tipe dengan kode {row.get('TIPE', '')} tidak ditemukan!")
            
            # ========== VARIETAS ==============
            # ==================================
            varietas_found = self.env['plant.varieties'].search([('code', '=', row.get('VARIETAS', ''))], limit=1)
            if lhm_line and not varietas_found:
                error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')} Varietas dengan kode {row.get('VARIETAS', '')} tidak ditemukan!")


            # ========== LOKASI ==============
            # ================================
            location = self.env['lhm.location'].search([('code', '=',  row.get('LOKASI', ''))], limit=1)
            if lhm_line and not location:
                error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')} Lokasi dengan kode {row.get('LOKASI', '')} tidak ditemukan!")
            
            if lhm_line and type_location:
                location_2 = self.env['lhm.location'].search([('type_id', '=',type_location.id )])
                if not location_2:
                    error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')} Lokasi {row.get('LOKASI','')} memiliki tipe yang tidak sama dengan {type_location.code}")
            
            if lhm_line and varietas_found and type_location and type_location.code not in ('PJ','NA','WS','VH','MA','NS'):
                location_3 = self.env['lhm.location'].search([('code', '=',  location.code),('varieties_id','=',varietas_found.id)], limit=1)
                if not location_3:
                    error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')} Lokasi kode {row.get('LOKASI', '')} tidak ditemukan di dalam Varietas code {varietas_found.code}")
            
            # ========== Aktivitas ==============
            # ===================================
            activity = self.env['lhm.activity'].search([('code', '=', row.get('AKTIVITAS', ''))], limit=1)
            if not activity:
                error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak ditemukan!")
            
            # cari aktifitas berdasarkan tipe lokasi yang dipilih
            activity_2 = self.env['lhm.activity'].search([('code', '=', row.get('AKTIVITAS', '')) ,('type_id', '=', type_location.id)], limit=1)
            if type_location and not activity_2:
                error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')} Aktivitas dengan kode {row.get('AKTIVITAS', '')} tidak ditemukan berdasarkan Tipe {type_location.code} yang dimasukkan!")

            # Pencarian berdasarkan Tipe Lokasi [PJ]
            
            
            # Pencarian berdasarkan Varietas


            # Validasi HK lebih dari 1 
            work_day = handle_nan(row.get('HK', ''), 0)
            if work_day > 1:
                error_message_list.append(f"Baris ke- {index + 2} untuk karyawan {row.get('NAME', '')}, HK yang dimasukkan {row.get('HK', '')} tidak boleh lebih dari 1!")


            # ========== SATUAN ==============
            # ================================
            # satuan_1 = self.env['uom.uom'].search([('name', '=', row.get('Satuan 1', ''))], limit=1)
            # if not satuan_1:
            #     error_message_list.append(f"Baris ke- {index + 2}  pada Satuan 1 dengan nama {row.get('Satuan 1', '')} tidak ditemukan!")
            # # Satuan 2
            # satuan_2 = self.env['uom.uom'].search([('name', '=', row.get('Satuan 2', ''))], limit=1)
            # if not satuan_2:
            #     error_message_list.append(f"Baris ke- {index + 2}  pada Satuan 2 dengan nama {row.get('Satuan 2', '')} tidak ditemukan!")


            # Mencari data abasensi 
            absensi_kj  = self.env['hr.attendance.type'].search([('code', '=', 'KJ')], limit=1)

            # Menambahkan data
            to_update.append((1, lhm_line.id, {
                'attendance_id'     : absensi_kj.id,
                'location_type_id'  : type_location.id,
                'varieties_id'      : varietas_found.id,
                'location_id'       : location.id,
                'activity_id'       : activity.id,
                'is_borong'         : handle_nan(row.get('IS BORONG', ''), False),
                'is_hasil_2'        : handle_nan(row.get('IS HASIL 2', ''), False),
                'work_day'          : handle_nan(row.get('HK', ''), 0),
                'product_id'        : varietas_found.product_id.id,
                'hasil_1'           : handle_nan(row.get('HASIL 1', ''), 0),
                # 'satuan_1'          : satuan_1.id,
                'product_id_2'      : varietas_found.secondary_product_id.id,
                'hasil_2'           : handle_nan(row.get('HASIL 2', ''), 0),
                # 'satuan_2'          : satuan_2.id,
            }))

        
        if error_message_list:
            error_message = '\n'.join(error_message_list)
            self.error_message = error_message
            raise ValidationError(_("Import data gagal dengan error berikut:\n%s") % error_message)
        
        logging.info(f"======== IMPORT LHM LINE BERHASIL {to_update} =======")
        
        self.lhm_line_ids = to_update
        return True
