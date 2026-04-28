from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/hanca"

class BlokHancaApi(ApiBase):
    @http.route([ROUTES, f"{ROUTES}/<hanca_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_hanca(self, hanca_id=None):
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
            if hanca_id is not None:
                conditions.append("id = %s")
                params.append(int(hanca_id))
            elif last_sync_date:
                conditions.append("(create_date > %s OR write_date > %s)")
                params.extend([last_sync_date, last_sync_date])
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cr = request.env.cr
            cr.execute(f"SELECT id, name, description, plant_block_id, geo_map_center, geo_map_border, perimeter, area, create_date, write_date FROM lhm_hanca {where_clause}", params)
            result['data'] = cr.dictfetchall()
            result['count'] = len(result['data'])
            
            if not result['count']:
                raise MissingError("Blok Hanca not Found")
            
            return Response(json.dumps({
                    'message': f"Successfully get data Blok Hanca(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)