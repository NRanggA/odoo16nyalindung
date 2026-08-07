from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/afdeling"

class BlokHancaApi(ApiBase):
    @http.route([ROUTES, f"{ROUTES}/<afdeling_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_afdeling(self, afdeling_id=None):
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
            if afdeling_id is not None:
                conditions.append("id = %s")
                params.append(int(afdeling_id))
            elif last_sync_date:
                conditions.append("(create_date > %s OR write_date > %s)")
                params.extend([last_sync_date, last_sync_date])
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cr = request.env.cr
            cr.execute(f"SELECT id, name, code, create_date, write_date FROM res_afdeling {where_clause}", params)
            result['data'] = cr.dictfetchall()
            result['count'] = len(result['data'])
            
            if not result['count']:
                raise MissingError("Afdeling not Found")
            
            return Response(json.dumps({
                    'message': f"Successfully get data Afdeling(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)