from odoo import http
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantation/lhm"

class ProfileApi(ApiBase):
    
    @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def submit_new_lhm(self):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        try:
            raw_list_to_create = datas.get('values', [])
            if not raw_list_to_create:
                raise ValidationError("Empty Data: Nothing to create")
            # Validate Mandatory Field
            mandatory_fields = ['date','kemandoran_id','lhm_line_ids']
            for line_to_check in raw_list_to_create:
                to_check_keys = line_to_check.keys()
                if any([(x not in to_check_keys) for x in mandatory_fields]):
                    raise ValidationError(f"This field are mandatory. ({','.join(mandatory_fields)})")
                for key in to_check_keys:
                    if key in mandatory_fields and not line_to_check.get(key, False):
                        raise ValidationError(f"Field '{key}' are a mandatory Field)")
                
            list_to_create = []
            data_validation_error = []
            line_validation_error = []
            for vals in raw_list_to_create:
                lhm_lines = []
                for line_vals in vals.get('lhm_line_ids',[]):
                    # contract = request.env['hr.contract'].sudo().browse(line_vals['contract_id'])
                    employee = request.env['hr.employee'].sudo().browse(line_vals['employee_id'])
                    if not employee.contract_id:
                        line_validation_error.append("Karyawan {employee.name} ({employee.no_induk or ''}) tidak memiliki Kontrak Aktif")
                        continue
                    lhm_lines.append((0,0,{
                        'date': line_vals.get('date', False),
                        'employee_id': line_vals.get('employee_id', False),
                        'work_day': line_vals.get('work_day', 0.0),
                        'attendance_id': line_vals.get('attendance_id', False),
                        # 'non_work_day': line_vals.get(' 'non_work_day', False),
                        'location_type_id': line_vals.get('location_type_id', False),
                        'varieties_id': line_vals.get('varieties_id', False),
                        'location_id': line_vals.get('location_id', False),
                        'activity_id': line_vals.get('activity_id', False),
                        # 'work_result': line_vals.get(' 'work_result', False),
                        # 'satuan_id': line_vals.get(' 'satuan_id', False),
                        'product_id': line_vals.get('product_id', False),
                        'hasil_1': line_vals.get('hasil_1', 0.0),
                        'satuan_1': line_vals.get('satuan_1', False),
                        'product_id_2': line_vals.get('product_id_2', False),
                        'hasil_2': line_vals.get('hasil_2', 0.0),
                        'satuan_2': line_vals.get('satuan_2', False),
                        # 'is_hasil_2': line_vals.get(' 'is_hasil_2', False),
                        'unit_price': line_vals.get('unit_price', 0.0),
                        'premi': line_vals.get('premi', 0.0),
                        'overtime_hour': line_vals.get('overtime_hour', 0),
                        # 'penalty': line_vals.get('penalty', 0.0),
                        'contract_id': employee.contract_id.id,
                        # 'contract_wage_value': round(contract.wage / contract.wage_day, 2)
                        'contract_wage_value': round(employee.contract_id.wage / employee.contract_id.wage_day, 2)
                    }))
                lhm_transaction = {
                    # 'name'
                    'date': vals['date'],
                    'kemandoran_id': vals['kemandoran_id'],
                    'lhm_line_ids': lhm_lines,
                    # emp_out_ids
                    # emp_in_ids
                    # 'doc_type_id'
                    'note': vals['note'],
                    # 'lhm_nap_line_ids'
                }
                list_to_create.append(lhm_transaction)
            
            if line_validation_error:
                raise ValidationError("\n".join(line_validation_error))

            if data_validation_error:
                raise ValidationError("\n".join(data_validation_error))

            created_lhm = False
            if list_to_create:
                created_lhm = request.env['lhm.transaction'].with_user(check_user).create(list_to_create)
            
            if created_lhm:
                result = {'data': list(map(lambda x: {'id': x.id, 'name': x.name}, created_lhm)), 'count': len(created_lhm.ids)}
                return Response(json.dumps({
                        'message': f"Successfully create a new Laporan Harian Mandor (LHM)",
                        'data': result
                    }, cls=DateEncoder), headers=HEADERS, status=201)
            else:
                raise MissingError("Failed to create Laporan Harian Mandor")
        except Exception as error:
            return self._handle_exception(error)
    
    @http.route([ROUTES, f"{ROUTES}/<lhm_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_lhm(self, lhm_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        try:
            result = {'data': [], 'count': 0}
            if not datas.get('kemandoran_id'):
                raise ValidationError("Field 'kemandoran_id' is mandatory field.")
            
            domain = [('kemandoran_id','=',datas['kemandoran_id'])]
            if lhm_id:
                domain.append(('id','=',int(lhm_id)))
            else:
                if datas.get('date_from') and datas.get('date_to'):
                    domain.extend([('date','>=',datas['date_from']),('date','<=',datas['date_to'])])
            fields = ['id','name','kemandoran_id','date','state']
            limit = datas.get('limit', 10)
            offset = datas.get('offset', 0)
            lhm_records = request.env['lhm.transaction'].search_read(domain=domain, fields=fields, order="date desc", limit=limit, offset=offset)
            if not lhm_records:
                raise MissingError("Data LHM not found")
            fields2 = ['employee_id','name','date','work_day','attendance_id',
                       'location_type_id','location_id','activity_id',
                       'hasil_1','satuan_1','product_id',
                       'hasil_2','satuan_2','product_id_2']
            for lhm in lhm_records:
                lhm_line_records = request.env['lhm.transaction.line'].search_read(domain=[('lhm_id','=',lhm['id'])], fields=fields2)
                lhm.update({
                    'lhm_line_ids': lhm_line_records
                })
            
            result['data'] = lhm_records
            result['count'] = len(lhm_records)
            return Response(json.dumps({
                    'message': f"Successfully get data Laporan Harian Mandor (LHM)",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)