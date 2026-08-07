from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/employee"

class EmployeeApi(ApiBase):
    @http.route([ROUTES, f"{ROUTES}/<employee_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_employee(self, employee_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        last_sync_date = datas.get('last_sync_date')
        try:
            result = {'data': []}
            conditions = []
            params = []
            if employee_id is not None:
                conditions.append("id = %s")
                params.append(int(employee_id))
            elif last_sync_date:
                conditions.append("(create_date > %s OR write_date > %s)")
                params.extend([last_sync_date, last_sync_date])
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cr = request.env.cr
            cr.execute(f"SELECT he.id, he.name, he.kemandoran_id, hf.afdeling_id, null as job_id, he.no_induk, he.identification_id, he.create_date, he.write_date FROM hr_employee he left join hr_foreman hf on hf.id=he.kemandoran_id {where_clause}", params)
            result['data'] = cr.dictfetchall()
            result['count'] = len(result['data'])
            
            if not result['count']:
                raise MissingError("Employee not Found")

            return Response(json.dumps({
                    'message': f"Successfully get data Employee(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)