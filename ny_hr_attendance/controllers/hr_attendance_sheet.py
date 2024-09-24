from odoo import http, exceptions, models
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/attendance"

class AttendanceSheetApi(ApiBase):
    # view attendance
    # Header {
    #   Authorization : Bearer access_token_xxxx,
    # }
    # Payload
    # {
    #   # OPTIONAL
    #   "filter": {
    #       "nip": ['1000001','1000002']
    #   }
    # }
    @http.route(f"{ROUTES}/<string:date_str>", auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def view_attendance(self, date_str):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        filter = datas.get('filter',{})
        if 'nip' in filter and not isinstance(filter['nip'], list):
            return Response(json.dumps({'message': "Invalid data format for nip. Filter 'nip' data type should be in array format"}), headers=HEADERS, status=422)
        
        try:
            domain = [('date','=',date_str)]
            if 'nip' in filter:
                if len(filter['nip']) > 1:
                    domain.append(('employee_id.no_induk','in',filter['nip']))
                elif len(filter['nip'])==1:
                    domain.append(('employee_id.no_induk','=',filter['nip'][0]))
            print("aaaaaaaaaaa", domain)
            attendance_found = request.env['hr.attendance.sheet'].with_user(check_user).search(domain)
            result = {'data': []}
            for attendance in attendance_found:
                result['data'].append({
                    # 'id': attendance.id, 
                    'employee_nip': attendance.employee_id.no_induk,
                    'employee_name': attendance.employee_id.name,
                    'check_in': attendance.check_in.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in else "",
                    'check_out': attendance.check_out.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_out else "",
                    'date': attendance.date,
                    'attendance_type': attendance.type_id.code,
                })
            
            return Response(json.dumps({
                    'message': f"Attendance at date {date_str} is found.",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

	# create attendance
    # Header {
    #   Authorization : Bearer access_token_xxxx,
    # }
    # Payload
    # {
    #   # MANDATORY
    #   "data": [
    #   {
    #      "employee_nip": "OT001",
    #      "check_in": "2024-09-30 07:00:00",
    #      "check_out": "2024-09-30 17:00:00",
    #   },
    #   {
    #      "employee_nip": "OT001",
    #      "check_in": "2024-09-30 07:00:00",
    #      "check_out": "2024-09-30 17:00:00",
    #   },
    #   ]
    # }
    @http.route(f"{ROUTES}/create_or_update", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def create_attendance(self):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)

        # decode token
        datas = self._get_payload()
        if datas is None or not datas:
            return Response(json.dumps({'message': 'Invalid JSON payload or format'}), headers=HEADERS, status=400)
        ############# BEGIN : VALIDATION DATA
        ########### Validate mandatory field ##########
        required_field = ['employee_nip', 'check_in']
        for data in datas['data']:
            if not all(field in data for field in required_field):
                field = ', '.join(list(field for field in required_field if field not in data))
                return Response(json.dumps({'message': f"Mandatory Field Required. Please complete {field}!"}), headers=HEADERS, status=400)
        employee = request.env['hr.employee']
        employee_not_found = []
        for nip in [l['employee_nip'] for l in datas['data']]:
            employee_existed = employee.with_user(check_user).search([('no_induk','=',nip)], limit=1)
            if not employee_existed:
                employee_not_found.append(nip)
        if employee_not_found:
            employee_not_found_err = ', '.join(employee_not_found)
            return Response(json.dumps({'message': f"Employee with NIP {employee_not_found_err} does not exist!"}), headers=HEADERS, status=400)
        ############# END : VALIDATION DATA
        
        ########### CHECK PARTNER ##########
        try:
            res_attendance = request.env['hr.attendance.sheet'].with_user(check_user)
            vals_to_create = []
            for data in datas['data']:
                employee = employee.with_user(check_user).search([('no_induk','=',data['employee_nip'])], limit=1)
                check_in = timezone('Asia/Jakarta').localize(datetime.strptime(data['check_in'], '%Y-%m-%d %H:%M:%S')).astimezone(utc)
                if data['check_out']:
                    check_out = timezone('Asia/Jakarta').localize(datetime.strptime(data['check_out'], '%Y-%m-%d %H:%M:%S')).astimezone(utc)
                else:
                    check_out = False
                date = check_in.strftime('%Y-%m-%d')
                existing_att = request.env['hr.attendance.sheet'].with_user(check_user).search([('employee_id','=',employee.id),('date','=',date)])
                if existing_att:
                    res_attendance |= existing_att
                    existing_att.with_user(check_user).write({
                        'check_in': check_in.strftime('%Y-%m-%d %H:%M:%S'),
                        'check_out': check_out.strftime('%Y-%m-%d %H:%M:%S') if check_out else False,
                        'type_id': request.env['hr.attendance.type'].with_user(check_user).search([('code','=','KJ')], limit=1).id,
                        'is_data_from_my_daya': True,
                    })
                else:
                    vals_to_create.append({
                        'employee_id': employee.id,
                        'check_in': check_in.strftime('%Y-%m-%d %H:%M:%S'),
                        'check_out': check_out.strftime('%Y-%m-%d %H:%M:%S') if check_out else False,
                        'date': date,
                        'is_data_from_my_daya': True,
                    })
            if vals_to_create:
                new_attendances = request.env['hr.attendance.sheet'].with_user(check_user).create(vals_to_create)
                if new_attendances:
                    res_attendance |= new_attendances

            result = {'data': []}
            for attendance in res_attendance:
                att_res = {
                    'id': attendance.id, 
                    'employee_nip': attendance.employee_id.no_induk,
                    'employee_name': attendance.employee_id.name,
                    'check_in': attendance.check_in.strftime('%Y-%m-%d %H:%M:%S'),
                    'check_out': attendance.check_out.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_out else "",
                    'date': attendance.date,
                    'attendance_type': attendance.type_id.code,
                }
                result['data'].append(att_res)
            return Response(json.dumps({
                'message': f"Success. Attedancen Sheet has been created/update.",
                'data': result
            }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)