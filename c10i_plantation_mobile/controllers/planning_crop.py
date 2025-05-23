from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantation/planning"

class ProfileApi(ApiBase):
    
    @http.route([f"{ROUTES}/weekly",
        f"{ROUTES}/monthly"], auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def submit_new_plan(self):
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
            mandatory_fields = ['date_from', 'date_to','plantation_block_id','task_ids']
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
            plan_type = request.httprequest.base_url.split('/')[-1]
            for vals in raw_list_to_create:
                task_lines = []
                for line_vals in vals.get('task_ids',[]):
                    task_lines.append((0,0,{
                        'activity_id': line_vals.get('activity_id', False),
                        'plan_work_day': line_vals.get('plan_work_day', 0.0),
                        'plan_result': line_vals.get('plan_hasil_1', 0.0),
                        'plan_result_2': line_vals.get('plan_hasil_2', 0.0)
                    }))
                lhm_transaction = {
                    'date_from': vals['date_from'],
                    'date_to': vals['date_to'],
                    'task_ids': task_lines,
                    'type': plan_type,
                }
                list_to_create.append(lhm_transaction)
            
            if line_validation_error:
                raise ValidationError("\n".join(line_validation_error))

            if data_validation_error:
                raise ValidationError("\n".join(data_validation_error))

            created_plan = False
            if list_to_create:
                created_plan = request.env['planning.crop'].with_user(check_user).create(list_to_create)
            
            if created_plan:
                result = {'data': list(map(lambda x: {'id': x.id, 'name': x.display_name}, created_plan)), 'count': len(created_plan.ids)}
                return Response(json.dumps({
                        'message': f"Successfully create a new Laporan Harian Mandor (LHM)",
                        'data': result
                    }, cls=DateEncoder), headers=HEADERS, status=201)
            else:
                raise MissingError("Failed to create Laporan Harian Mandor")
        except Exception as error:
            return self._handle_exception(error)
    
    @http.route([f"{ROUTES}/weekly",
        f"{ROUTES}/weekly/<planning_id>",
        f"{ROUTES}/monthly",
        f"{ROUTES}/monthly/<planning_id>",
        f"{ROUTES}/<planning_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_plan(self, planning_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        try:
            result = {'data': [], 'count': 0}
            domain = [('create_uid','=',check_user),('state','=','confirm')]
            if planning_id:
                domain.append(('id','=',int(planning_id)))
            else:
                domain.append(('type','=',request.httprequest.base_url.split('/')[-1]))
                date_today = fields.Date.context_today(request.env['planning.crop'])
                domain.extend([('date_from','<=',date_today),('date_to','>=',date_today)])
            
            limit = datas.get('limit', 10)
            offset = datas.get('offset', 0)
            planning_found = request.env['planning.crop'].with_user(check_user).search(domain, order="date_to desc", limit=limit, offset=offset)
            if not planning_found:
                raise MissingError("Data Planning not found")
            
            planning_records = []
            for planning in planning_found:
                plan_vals = {
                    'name': planning.display_name,
                    'date_from': planning.date_from.strftime('%Y-%m-%d'),
                    'date_to': planning.date_to.strftime('%Y-%m-%d'),
                    'state': planning.state,
                    'planted_block_id': (planning.plant_block_id.id, planning.plant_block_id.display_name),
                    'task_ids': [{
                        'plan_work_day': task.plan_work_day,
                        'product_id': (task.product_id.id, task.product_id.display_name) if task.product_id else False,
                        'product_id_2': (task.product_id_2.id, task.product_id_2.display_name) if task.product_id_2 else False,
                        'plan_result': task.plan_result,
                        'plan_result_2': task.plan_result_2,
                        'act_emp_work_day': task.act_emp_work_day,
                        'act_emp_result': task.act_emp_result,
                        'act_emp_result_2': task.act_emp_result_2,
                        'act_partner_result': task.act_partner_result,
                        'act_partner_result_2': task.act_partner_result_2,
                        'plan_material_ids': [(0, 0, {
                            'product_id': (material.product_id.id, material.product_id.display_name) if material.product_id else False,
                            'uom_id': (material.uom_id.id, material.uom_id.display_name) if material.uom_id else False,
                            'plan_qty': material.plan_qty,
                            'cost_price': material.cost_price,
                            'plan_cost': material.plan_cost
                            # 'actual_qty': material.actual_qty,
                            # 'actual_cost': material.actual_cost,
                        }) for material in task.plan_material_ids],
                    } for task in planning.task_ids]
                }
                planning_records.append(plan_vals)
            
            result['data'] = planning_records
            result['count'] = len(planning_records)
            return Response(json.dumps({
                    'message': f"Successfully get data Planning",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)