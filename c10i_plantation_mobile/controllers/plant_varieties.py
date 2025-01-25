from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantation/varieties"

class VarietiesApi(ApiBase):
    @http.route([ROUTES, f"{ROUTES}/<varieties_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_varieties(self, varieties_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        last_sync_date = datas.get('last_sync_date')
        try:
            result = {'data': [], 'count': 0}
            domain = []
            if varieties_id is not None:
                domain.append(('id','=',int(varieties_id)))
            else:
                if last_sync_date:
                    domain.extend(['|',('create_date','>',last_sync_date),('write_date','>',last_sync_date)])
            for varieties in request.env['plant.varieties'].sudo().search(domain):
                result['data'].append({
                    'id': varieties.id,
                    'name': varieties.name,
                    'code': varieties.code,
                    'allowed_location_id': varieties.plant_block_ids.location_id.ids + varieties.project_ids.location_id.ids,
                    'allowed_fc_activity_id': varieties.harvest_activity_ids.ids + varieties.upkeep_activity_ids.ids,
                    'allowed_gc_activity_id': varieties.general_charges_activity_ids.ids,
                    'allowed_idc_activity_id': varieties.indirect_cost_activity_ids.ids,
                    'create_date': varieties.create_date,
                    'write_date': varieties.write_date,
                })
                result['count'] += 1
            
            if not result['count']:
                raise MissingError("Varieties not Found")
            
            return Response(json.dumps({
                    'message': f"Successfully get data Unit of Varieties(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)