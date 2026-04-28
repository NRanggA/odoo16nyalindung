from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError
import json
from datetime import datetime, time
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/lhm"

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
            mandatory_fields = ['date','kemandoran_id']
            for line_to_check in raw_list_to_create:
                to_check_keys = line_to_check.keys()
                if any([(x not in to_check_keys) for x in mandatory_fields]):
                    raise ValidationError(f"This field are mandatory. ({','.join(mandatory_fields)})")
                for key in to_check_keys:
                    if key in mandatory_fields and not line_to_check.get(key, False):
                        raise ValidationError(f"Field '{key}' are a mandatory Field)")
                if not line_to_check.get('lhm_line_ids', []) or not line_to_check.get('contractor_line_ids', []):
                    raise ValidationError("Field 'lhm_line_ids' or 'contractor_line_ids' are mandatory field and must be filled.")

            list_to_create = [] # lhm.transaction
            list_to_create2 = {} # lhm.contractor
            data_validation_error = []
            line_validation_error = []
            for vals in raw_list_to_create:
                ############# LHM
                lhm_lines = []
                for line_vals in vals.get('lhm_line_ids',[]):
                    # contract = request.env['hr.contract'].sudo().browse(line_vals['contract_id'])
                    employee = request.env['hr.employee'].sudo().browse(line_vals['employee_id'])
                    if not employee.contract_id:
                        line_validation_error.append("Karyawan {employee.name} ({employee.no_induk or ''}) tidak memiliki Kontrak Aktif")
                        continue
                    lhm_lines.append((0,0,{
                        'date': vals['date'],
                        # 'date': line_vals.get('date', False),
                        'employee_id': line_vals.get('employee_id', False),
                        'work_day': line_vals.get('work_day', 0.0),
                        'attendance_id': line_vals.get('attendance_id', False),
                        # 'non_work_day': line_vals.get(' 'non_work_day', False),
                        'varieties_id': line_vals.get('varieties_id', False),
                        'location_type_id': line_vals.get('location_type_id', False),
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
                
                material_lines = []
                for material_vals in vals.get('material_line_ids',[]):
                    material_lines.append((0,0,{
                        'date': vals['date'],
                        'from_mobile_apps': True,
                        'product_id': material_vals.get('product_id', False),
                        'activity_id': material_vals.get('activity_id', False),
                        'location_id': material_vals.get('location_id', False),
                        'product_uom_id': material_vals.get('product_uom_id', False),
                        'realization': material_vals.get('realization', 0.0)
                    }))

                lhm_transaction = {
                    # 'name'
                    'date': vals['date'],
                    'kemandoran_id': vals['kemandoran_id'],
                    'lhm_line_ids': lhm_lines,
                    'material_line_ids': material_lines,
                    # emp_out_ids
                    # emp_in_ids
                    'note': vals['note'],
                    # 'lhm_nap_line_ids'
                }
                list_to_create.append(lhm_transaction)
            
                ############# LHM CONTRACTOR
                for cvals in vals.get('contractor_line_ids', []):
                    if not cvals.get('contractor_id', False):
                        data_validation_error.append("Field 'contractor_id' is mandatory in contractor_line_ids")
                        continue

                    contractor = request.env['res.partner'].sudo().browse(cvals['contractor_id'])
                    if contractor.id not in list_to_create2:
                        list_to_create2[contractor.id] = {
                            'supplier_id': contractor.id,
                            'date': vals['date'],
                            'date_start': vals['date'],
                            # 'date_end': vals['date'],
                            # 'is_harian': True,
                            'line_ids': [],
                            # 'material_line_ids': [],
                            'note': vals['note'],
                            'user_id': check_user
                        }
                    for cvals in vals.get('contractor_line_ids', []):
                        if cvals.get('contractor_id', False) != contractor.id:
                            continue
                        list_to_create2[contractor.id]['line_ids'].append((0,0,{
                            'date': vals['date'],
                            'varieties_id': cvals.get('varieties_id', False),
                            'location_type_id': cvals.get('location_type_id', False),
                            'location_id': cvals.get('location_id', False),
                            'activity_id': cvals.get('activity_id', False),
                            'product_id': cvals.get('product_id', False),
                            'nilai': cvals.get('hasil_1', 0.0),
                            'uom_id': cvals.get('satuan_1', False),
                            'product_id_2': cvals.get('product_id_2', False),
                            'nilai2': cvals.get('hasil_2', 0.0),
                            'uom2_id': cvals.get('satuan_2', False),
                        }))
            
            if line_validation_error:
                raise ValidationError("\n".join(line_validation_error))

            if data_validation_error:
                raise ValidationError("\n".join(data_validation_error))

            created_lhm = False
            if list_to_create:
                created_lhm = request.env['lhm.transaction'].with_user(check_user).create(list_to_create)
            created_contractor = False
            if list_to_create2:
                created_contractor = request.env['lhm.contractor'].with_user(check_user).create(list(list_to_create2.values()))
            
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
            conditions = []
            params = []
            if lhm_id:
                conditions.append("id = %s")
                params.append(int(lhm_id))
            elif datas.get('date_from') and datas.get('date_to'):
                conditions.append("date >= %s AND date <= %s")
                params.extend([datas['date_from'], datas['date_to']])
            limit = datas.get('limit', 10)
            offset = datas.get('offset', 0)
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            params.extend([limit, offset])
            cr = request.env.cr
            cr.execute(f"""
                SELECT id, name, kemandoran_id, date, origin, state
                FROM lhm_transaction
                {where_clause}
                ORDER BY date DESC
                LIMIT %s OFFSET %s
            """, params)
            lhm_records = cr.dictfetchall()
            if not lhm_records:
                raise MissingError("Data LHM not found")
            # This is for Material Line in LHM

            for lhm in lhm_records:
                # lhm_line_records = request.env['lhm.transaction.line'].with_user(check_user).search_read(domain=[('lhm_id','=',lhm['id'])], fields=fields2)
                query_line = """SELECT 
                        lhm_line.id,
                        lhm_line.employee_id,
                        lhm_line.date,
                        block.id as plant_block_id,
                        lhm_line.activity_id,
                        lhm_line.hasil_1,
                        lhm_line.satuan_1,
                        lhm_line.product_id,
                        lhm_line.hasil_2,
                        lhm_line.satuan_2,
                        lhm_line.product_id_2
                    FROM lhm_transaction_line lhm_line
                        left join lhm_plant_block block on block.location_id = lhm_line.location_id
                    WHERE lhm_line.lhm_id = %s
                    """
                request.env.cr.execute(query_line, (lhm['id'],))
                lhm_line_records = request.env.cr.dictfetchall()
                
                # material_line_records = request.env['lhm.transaction.material.line'].with_user(check_user).search_read(domain=[('lhm_id','=',lhm['id'])], fields=fields3)
                query_material_line = """SELECT
                        material_line.id,
                        material_line.product_id,
                        material_line.activity_id,
                        block.id as plant_block_id,
                        material_line.product_uom_id as uom_id,
                        material_line.realization as product_qty
                    FROM lhm_transaction_material_line material_line
                        left join lhm_plant_block block on block.location_id = material_line.location_id
                    WHERE material_line.lhm_id = %s
                """
                request.env.cr.execute(query_material_line, (lhm['id'],))
                material_line_records = request.env.cr.dictfetchall()
                lhm.update({
                    'lhm_line_ids': lhm_line_records,
                    'material_line_ids': material_line_records
                })
            
            result['data'] = lhm_records
            result['count'] = len(lhm_records)
            return Response(json.dumps({
                    'message': f"Successfully get data Laporan Harian Mandor (LHM)",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)