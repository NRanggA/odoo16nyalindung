from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

import json
from datetime import datetime
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


ROUTES = f"{BASE_ROUTE}/plantationai/attendance"

class Attendance(ApiBase):
    @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_attendance(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            result = {'data': [], 'count': 0}
            
            # GET ATTENDANCE
            jakarta = timezone('Asia/Jakarta')
            
            today = utc.localize(fields.Datetime.now()).astimezone(jakarta)
            
            conditions = []
            params = []
            if not datas.get('date_from'):
                start_date = today - relativedelta(days=7)
            else:
                start_date = datetime.strptime(datas.get('date_from'), "%Y-%m-%d")
            if start_date:
                conditions.append("date >= %s")
                params.append(start_date)
            
            if not datas.get('date_to'):
                end_date = today
            else:
                end_date = datetime.strptime(datas.get('date_to'), "%Y-%m-%d")
            if end_date:
                conditions.append("date <= %s")
                params.append(end_date)
            
            if datas.get('employee_ids'):
                conditions.append("employee_id IN %s")
                params.append(tuple(datas.get('employee_ids')))
            
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            cr = request.env.cr
            cr.execute("SELECT id, date, employee_id, type_id, check_in, check_out FROM hr_attendance_sheet {where_clause}", params)
            result['data'] = cr.dictfetchall()
            result['count'] = len(result['data'])
            return Response(json.dumps({
                    'message': f"Successfully get data Employee(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    # @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['POST'])
    # def create_attendance(self):
    #     check_user, message = self._verify_auth()
    #     if not check_user:
    #         return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
    #     datas = self._get_payload() or {}
    #     try:
    #         raw_list_to_create = datas.get('values', [])
    #         if not raw_list_to_create:
    #             raise ValidationError("Empty Data: Nothing to create")
    #         # Validate Mandatory Field
    #         mandatory_fields = ['employee_id', 'type_id', 'date']
    #         for line_to_check in raw_list_to_create:
    #             to_check_keys = line_to_check.keys()
    #             if any([(x not in to_check_keys) for x in mandatory_fields]):
    #                 raise ValidationError(f"This field are mandatory. ({','.join(mandatory_fields)})")
            
    #         list_to_create = []
    #         for vals in raw_list_to_create:
    #             employee_found = request.env['hr.employee'].sudo().search([('id','=',vals.get('employee_id'))], limit=1)
    #             if not employee_found:
    #                 raise ValidationError(f"Employee with id {vals.get('employee_id')} not found")
    #             att_vals = {
    #                 'employee_id': employee_found.id,
    #                 'type_id': vals.get('type_id'),
    #                 'date': vals.get('date'),
    #                 'check_in': vals.get('check_in'),
    #                 'check_out': vals.get('check_out'),
    #             }
    #             list_to_create.append(att_vals)
            
    #         created_att = False
    #         if list_to_create:
    #             created_att = request.env['hr.attendance.sheet'].with_user(check_user).create(list_to_create)
            
    #         if created_att:
    #             result = {'data': list(map(lambda x: {'id': x.id, 'employee_id': (x.employee_id.id, x.employee_id.name),
    #                 'type_id': (x.type_id.id, x.type_id.name), 
    #                 'date': x.date, 'check_in': x.check_in, 'check_out': x.check_out
    #                 }, created_att)), 'count': len(created_att.ids)}
    #             return Response(json.dumps({
    #                     'message': f"Successfully create a new Attendance Sheet",
    #                     'data': result
    #                 }, cls=DateEncoder), headers=HEADERS, status=201)
    #         else:
    #             raise MissingError("Failed to create Attendance")
    #     except Exception as error:
    #         return self._handle_exception(error)