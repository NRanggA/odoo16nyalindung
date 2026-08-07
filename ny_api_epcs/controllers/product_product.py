from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/product"

class ProductApi(ApiBase):
    @http.route([ROUTES, f"{ROUTES}/<product_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_product(self, product_id=None):
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
            if product_id is not None:
                conditions.append("id = %s")
                params.append(int(product_id))
            elif last_sync_date:
                conditions.append("(create_date > %s OR write_date > %s)")
                params.extend([last_sync_date, last_sync_date])
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cr = request.env.cr
            cr.execute(f"SELECT pp.id, pt.name->>'en_US' as name, pp.default_code as code, pt.uom_id, pt.categ_id, pp.create_date, pp.write_date FROM product_product pp inner join product_template pt on pt.id=pp.product_tmpl_id {where_clause}", params)
            result['data'] = cr.dictfetchall()
            result['count'] = len(result['data'])

            if not result['count']:
                raise MissingError("Product not Found")

            return Response(json.dumps({
                    'message': f"Successfully get data Product(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    @http.route([f"{ROUTES}/onhand", f"{ROUTES}/onhand/<product_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_product_onhand(self, product_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        last_sync_date = datas.get('last_sync_date')
        try:
            result = {'data': []}
            domain = []
            if product_id is not None:
                domain.append(('id','=',int(product_id)))
            else:
                if last_sync_date:
                    domain.extend(['|',('create_date','>',last_sync_date),('write_date','>',last_sync_date)])
            
            fields = ['id','name','uom_id','qty_available']
            result['data'] = request.env['product.product'].sudo().search_read(domain=domain, fields=fields)
            result['count'] = request.env['product.product'].sudo().search_count(domain=domain)

            if not result['count']:
                raise MissingError("Product not Found")

            return Response(json.dumps({
                    'message': f"Successfully get data Product(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)