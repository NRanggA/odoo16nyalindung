from odoo import http
from odoo.http import request, Response
from odoo.exceptions import MissingError
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantation"

class ProfileApi(ApiBase):
    def _get_profile(self, user_id):
        user_data = request.env['res.users'].sudo().search_read(domain=[('id','=',user_id)], fields=['name','employee_ids'])
        if not user_data:
            raise MissingError("User not Found")
        
        if user_data[0].get('employee_ids',[]):
            employee_data = request.env['hr.employee'].sudo().search_read(domain=[('id','=',user_data[0]['employee_ids'][0])], 
                    fields=['name','department_id','job_id','no_induk','identification_id'])
            if employee_data:
                user_data[0].update(employee_data[0])
        return user_data
    
    @http.route(f"{ROUTES}/dosignin", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def login(self):
        datas = self._get_payload() or {}
        try:
            pre_uid = request.session.authenticate(datas['db'], datas['username'], datas['password'])
            if pre_uid != request.session.uid:
                raise MissingError("Failed to Sign in to Odoo")
            result = self._get_profile(pre_uid)
            return Response(json.dumps({
                    'message': f"Successfully Sign In to Odoo",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    @http.route(f"{ROUTES}/profile/<user_id>", auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_profile(self, user_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        # datas = self._get_payload() or {}
        try:
            result = {'data': self._get_profile(int(user_id)), 'count': 1}
            return Response(json.dumps({
                    'message': f"Successfully get User Profile",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)