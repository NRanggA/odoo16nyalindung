from odoo import http
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc
from passlib.context import CryptContext

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantation"

API_KEY_SIZE = 20 # in bytes
INDEX_SIZE = 8 # in hex digits, so 4 bytes, or 20% of the key
KEY_CRYPT_CONTEXT = CryptContext(
    # default is 29000 rounds which is 25~50ms, which is probably unnecessary
    # given in this case all the keys are completely random data: dictionary
    # attacks on API keys isn't much of a concern
    ['pbkdf2_sha512'], pbkdf2_sha512__rounds=6000,
)

class ProfileApi(ApiBase):
    def _get_profile(self, user_id):
        user_data = request.env['res.users'].sudo().search_read(domain=[('id','=',user_id)], fields=['name','employee_ids'])
        if not user_data:
            raise MissingError("User not Found")
        
        if user_data[0].get('employee_ids',[]):
            employee_data = request.env['hr.employee'].sudo().search_read(domain=[('id','=',user_data[0]['employee_ids'][0])], 
                    fields=['name','department_id','job_id','no_induk','identification_id'])
            if employee_data:
                del employee_data[0]['id']
                user_data[0].update(employee_data[0])
                foreman = request.env['hr.foreman'].sudo().search([('mandor_id','=',user_data[0]['employee_ids'][0])])
                if foreman:
                    user_data[0].update({'allowed_kemandoran_ids': foreman.ids})
        return user_data
    
    @http.route(f"{ROUTES}/dosignin", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def login(self):
        datas = self._get_payload() or {}
        try:
            pre_uid = request.session.authenticate(datas['db'], datas['username'], datas['password'])
            if pre_uid != request.session.uid:
                raise MissingError("Failed to Sign in to Odoo")
            result = self._get_profile(pre_uid)
            
            # Create a new Token
            scope = datas.get('service-name')
            if not scope:
                raise MissingError("Invalid API Service")

            desription = f"Token for Plantation Mobile App"
            user_token = request.env['res.users.apikeys']._generate(scope, desription)
            if user_token:
                result[0].update({'token': user_token})
            
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
    
    @http.route(f"{ROUTES}/dosignout", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def logout(self):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)

        # datas = self._get_payload() or {}
        try:
            scope = request.httprequest.headers.get('service-name')
            if not scope:
                raise MissingError("Invalid API Service")
            existing_token = request.env['res.users.apikeys'].sudo().search([('user_id','=',check_user),
                    ('scope','=',scope)])
            if existing_token:
                existing_token.unlink()
            return Response(json.dumps({
                    'message': f"Successfully Sign Out from Odoo",
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)