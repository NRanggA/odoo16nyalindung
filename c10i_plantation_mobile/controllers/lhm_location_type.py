from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantation/loctype"

class LocationTypeApi(ApiBase):
    @http.route([ROUTES, f"{ROUTES}/<loc_type_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_location_type(self, loc_type_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        last_sync_date = datas.get('last_sync_date')
        try:
            result = {'data': [], 'count': 0}
            domain = []
            if loc_type_id is not None:
                domain.append(('id','=',int(loc_type_id)))
            else:
                if last_sync_date:
                    domain.extend(['|',('create_date','>',last_sync_date),('write_date','>',last_sync_date)])
            
            for loc_type in request.env['lhm.location.type'].sudo().search(domain):
                result['data'].append({
                    'id': loc_type.id,
                    'code': loc_type.code,
                    'name': loc_type.name,
                    'depend_on_varieties': loc_type.code in ('FC','GC','IDC', 'PJ', 'NS'),
                    'create_date': loc_type.create_date,
                    'write_date': loc_type.write_date,
                })
                result['count'] += 1
            
            if not result['count']:
                raise MissingError("Location Type not Found")

            return Response(json.dumps({
                    'message': f"Successfully get data Location Type(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)