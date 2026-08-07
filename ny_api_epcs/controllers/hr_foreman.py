from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/foreman"

class HrForemanApi(ApiBase):
    @http.route([ROUTES, f"{ROUTES}/<foreman_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_foreman(self, foreman_id=None):
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
            if foreman_id is not None:
                conditions.append("hf.id = %s")
                params.append(int(foreman_id))
            elif last_sync_date:
                conditions.append("(hf.create_date > %s OR hf.write_date > %s)")
                params.extend([last_sync_date, last_sync_date])
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cr = request.env.cr
            cr.execute(f"""
                SELECT hf.id, hf.name, hf.afdeling_id, hf.create_date, hf.write_date,
                       ARRAY_REMOVE(ARRAY_AGG(he.id), NULL) AS employee_ids
                FROM hr_foreman hf
                LEFT JOIN hr_employee he ON he.kemandoran_id = hf.id
                {where_clause}
                GROUP BY hf.id, hf.name, hf.afdeling_id, hf.create_date, hf.write_date
            """, params)
            result['data'] = cr.dictfetchall()
            result['count'] = len(result['data'])

            if not result['count']:
                raise MissingError("Foreman not Found")
            
            return Response(json.dumps({
                    'message': f"Successfully get data Foreman(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)