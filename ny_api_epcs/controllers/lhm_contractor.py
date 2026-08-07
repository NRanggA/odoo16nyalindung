from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError
import json
from datetime import datetime, time
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/contractor"

class LhmContractor(ApiBase):
    
    @http.route([ROUTES, f"{ROUTES}/<contractor_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_contractor(self, contractor_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        try:
            result = {'data': [], 'count': 0}
            
            # domain = [('contractor_id.user_id','=',check_user)]
            domain = []
            if contractor_id:
                domain.append(('id','=',int(contractor_id)))
            else:
                if datas.get('date') and datas.get('date'):
                    domain.extend([('date','>=',datas['date_from']),('date','<=',datas['date_to'])])
            limit = datas.get('limit', 10)
            offset = datas.get('offset', 0)
            cont_records = request.env['lhm.contractor.line'].with_user(check_user).search(domain=domain, order="date desc", limit=limit, offset=offset)
            if not cont_records:
                raise MissingError("Data BK not found")
            line_data = []
            for line in cont_records:
                line_data.append({
                    'date': line.date.strftime('%Y-%m-%d') if line.date else line.contractor_id.date.strftime('%Y-%m-%d'),
                    'supplier_id': [line.contractor_id.supplier_id.id, line.contractor_id.supplier_id.name] if line.contractor_id.supplier_id else False,
                    'varieties_id': [line.varieties_id.id, line.varieties_id.display_name] if line.varieties_id else False,
                    'location_type_id': [line.location_type_id.id, line.location_type_id.display_name] if line.location_type_id else False,
                    'location_id': [line.location_id.id, line.location_id.name] if line.location_id else False,
                    'activity_id': [line.activity_id.id, line.activity_id.display_name] if line.activity_id else False,
                    'product_id': [line.product_id.id, line.product_id.name] if line.product_id else False,
                    'nilai': line.nilai,
                    'uom_id': [line.uom_id.id, line.uom_id.name] if line.uom_id else False,
                    'product_id_2': [line.product_id_2.id, line.product_id_2.name] if line.product_id_2 else False,
                    'nilai2': line.nilai2,
                    'uom2_id': [line.uom2_id.id, line.uom2_id.name] if line.uom2_id else False,
                })
            
            print(">>>>>>>>>>>>>>>>>>>get_contractor", line_data)
            result['data'] = line_data
            result['count'] = len(line_data)
            return Response(json.dumps({
                    'message': f"Successfully get data LHM Contractor",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)