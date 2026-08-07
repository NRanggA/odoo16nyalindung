from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/mr"

class MaterialRequest(ApiBase):
    
    @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def submit_new_mr(self):
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
            mandatory_fields = ['line_ids']
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
                mr_lines = []
                for line_vals in vals.get('line_ids',[]):
                    if not line_vals.get('product_id', False):
                        ValidationError("Field 'product_id' are a mandatory Field)")
                    if not line_vals.get('plant_block_id', False):
                        ValidationError("Field 'plant_block_id' are a mandatory Field)")
                    if not line_vals.get('activity_id', False):
                        ValidationError("Field 'activity_id' are a mandatory Field)")
                    plant_block = request.env['lhm.plant.block'].with_user(check_user).browse(line_vals['plant_block_id'])
                    mr_lines.append((0,0,{
                        'name': line_vals.get('name', False),
                        'product_id': line_vals.get('product_id', False),
                        'product_qty': line_vals.get('product_qty', 0.0),
                        'uom_id': line_vals.get('uom_id', 0.0),
                        
                        'location_type_id': plant_block.location_id.type_id.id,
                        'varieties_id': plant_block.varieties_id.id,
                        'location_id': plant_block.location_id.id,
                        'activity_id': line_vals.get('activity_id', False),
                    }))
                mr_vals = {
                    'requested_by': check_user,
                    'requested_by_2': request.env['res.users'].sudo().browse(check_user).employee_id.id,
                    'origin': datas.get('origin', False),
                    'description': datas.get('note', False),
                    'date_request': fields.Date.context_today(request.env['material.request']),
                    'line_ids': mr_lines,
                }
                list_to_create.append(mr_vals)
            
            if line_validation_error:
                raise ValidationError("\n".join(line_validation_error))

            if data_validation_error:
                raise ValidationError("\n".join(data_validation_error))

            created_mr = False
            if list_to_create:
                created_mr = request.env['material.request'].with_user(check_user).create(list_to_create)
                created_mr.with_user(check_user).action_submit()
            
            if created_mr:
                result = {'data': list(map(lambda x: {'id': x.id, 'name': x.name}, created_mr)), 'count': len(created_mr.ids)}
                return Response(json.dumps({
                        'message': f"Successfully create a new Material Request (MR)",
                        'data': result
                    }, cls=DateEncoder), headers=HEADERS, status=201)
            else:
                raise MissingError("Failed to create Laporan Harian Mandor")
        except Exception as error:
            return self._handle_exception(error)
    
    @http.route([ROUTES, f"{ROUTES}/<mr_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_mr(self, mr_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        try:
            result = {'data': [], 'count': 0}
            
            conditions = ["requested_by = %s"]
            params = [check_user]
            if mr_id:
                conditions.append("id = %s")
                params.append(int(mr_id))
            elif datas.get('date_from') and datas.get('date_to'):
                conditions.append("date_request >= %s AND date_request <= %s")
                params.extend([datas['date_from'], datas['date_to']])
            limit = datas.get('limit', 10)
            offset = datas.get('offset', 0)
            where_clause = "WHERE " + " AND ".join(conditions)
            params.extend([limit, offset])
            cr = request.env.cr
            cr.execute(f"""
                SELECT id, name, date_request, state, requested_by_2, origin
                FROM material_request
                {where_clause}
                ORDER BY date_request DESC
                LIMIT %s OFFSET %s
            """, params)
            mr_records = cr.dictfetchall()
            if not mr_records:
                raise MissingError("Data MR not found")
            for mr in mr_records:
                cr.execute("""
                    SELECT id, name, product_id, uom_id, activity_id, product_qty, location_id
                    FROM material_request_line
                    WHERE mr_id = %s
                """, (mr['id'],))
                mr_line_records = cr.dictfetchall()
                for line in mr_line_records:
                    if line.get('location_id'):
                        plant_block = request.env['lhm.plant.block'].with_user(check_user).search([('location_id','=',line['location_id'])], limit=1)
                    else:
                        plant_block = False
                    line.update({
                        'plant_block_id': (plant_block.id, plant_block.name) if plant_block else False
                    })
                    del line['location_id']

                mr.update({
                    'requested_by': mr['requested_by_2'],
                    'line_ids': mr_line_records
                })
                del mr['requested_by_2']
            
            result['data'] = mr_records
            result['count'] = len(mr_records)
            return Response(json.dumps({
                    'message': f"Successfully get data Material Request (MR)",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)