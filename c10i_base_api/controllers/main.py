from odoo import http, exceptions
from odoo.http import request, Response
import json
import datetime
import pytz

HEADERS = {'Content-Type': 'application/json'}
BASE_ROUTE = "/api"

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super(DateEncoder, self).default(obj)

# API Base Class
class ApiBase(http.Controller):
    
    def _convert_tz(self, date_clock):
        local_tz = pytz.timezone('Asia/Jakarta')
        local_time = local_tz.localize(datetime.datetime.strptime(date_clock, '%Y-%m-%d %H:%M:%S'))
        utc_time = local_time.astimezone(pytz.utc)
        return utc_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def _verify_auth(self):
        """
        Verifies the authentication token.
    
        Returns:
            tuple: A boolean indicating if authentication was successful, and an error message if not.
        """
        # Create or Update API Client List
        client_req_addrs = request.httprequest.environ['REMOTE_ADDR']
        added_addrs = request.env['c10i_base_api.client.list'].sudo().search([('name','=',client_req_addrs)], limit=1)
        if not added_addrs:
            added_addrs = request.env['c10i_base_api.client.list'].sudo().create({'name': client_req_addrs})
        # Blacklisted Address
        if added_addrs.blacklist:
            # return False, 'Unauthorized, You have failed authorization proceess several times. Please contact the admin for further details.'
            pass
        elif added_addrs.number_of_error_half_hour_allowed<=0:
            return False, 'Temporary Blocked, You have failed authorization proceess several times. Please wait for 30 minutes or contact the admin for further details.'
        auth_header = request.httprequest.headers.get('Authorization')
        scope = request.httprequest.headers.get('service-name')
        if not scope:
            return False, 'Invalid API Service'

        if not auth_header or not auth_header.startswith('Bearer '):
            added_addrs.write({
                'number_of_error_allowed': added_addrs.number_of_error_allowed-1,
                'number_of_error_half_hour_allowed': added_addrs.number_of_error_half_hour_allowed-1,
            })
            return False, 'Unauthorized, please contact the admin for further details.'
        token = auth_header.split(' ')[-1]
        check_user = request.env['res.users.apikeys']._check_credentials(scope=scope, key=token)
        
        if not check_user:
            # Add to Client List
            added_addrs.write({
                'number_of_error_allowed': added_addrs.number_of_error_allowed-1,
                'number_of_error_half_hour_allowed': added_addrs.number_of_error_half_hour_allowed-1,
            })
        return check_user, 'Invalid token, please use a valid token.'
    
    # ambil payload 
    def _get_payload(self):
        """ 
        Decode payload into json format
        
        Returns:
            dictionary : A dictionary contains data to update
        """
        
        payload = request.httprequest.data.decode()
        if not payload:
            return None
        try:
            parsed_data = json.loads(payload)
            return parsed_data
        except json.JSONDecodeError:
            return None


    # error handling
    def _handle_exception(self, error):
        """ Error Handling Response in Except

        Returns:
            Exception : get error message when failed to update data
        """
        exception_mappings = {
            exceptions.AccessDenied: 401,
            exceptions.AccessError: 403,
            exceptions.CacheMiss: 404,
            exceptions.MissingError: 404,
            exceptions.ValidationError: 422
        }
        
        status_code = exception_mappings.get(type(error), 400)
        
        if not status_code:
            status_code = 500
            message = f"General Error: {str(error)}"
        else:
            message = f"{type(error).__name__} : {str(error)}"
        
        return Response(json.dumps({'message' : message}), headers=HEADERS, status=status_code)