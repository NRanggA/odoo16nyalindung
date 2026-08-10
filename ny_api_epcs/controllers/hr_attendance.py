from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

import json
from datetime import datetime
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


ROUTES = f"{BASE_ROUTE}/plantationai/attendance"

class Attendance(ApiBase):
    @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_attendance(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            result = {'data': [], 'count': 0}
            
            # GET ATTENDANCE
            jakarta = timezone('Asia/Jakarta')
            
            today = utc.localize(fields.Datetime.now()).astimezone(jakarta)
            
            conditions = []
            params = []
            if not datas.get('date_from'):
                start_date = today - relativedelta(days=7)
            else:
                start_date = datetime.strptime(datas.get('date_from'), "%Y-%m-%d")
            if start_date:
                conditions.append("date >= %s")
                params.append(start_date)
            
            if not datas.get('date_to'):
                end_date = today
            else:
                end_date = datetime.strptime(datas.get('date_to'), "%Y-%m-%d")
            if end_date:
                conditions.append("date <= %s")
                params.append(end_date)
            
            if datas.get('employee_ids'):
                conditions.append("employee_id IN %s")
                params.append(tuple(datas.get('employee_ids')))
            
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            cr = request.env.cr
            cr.execute(f"SELECT id, date, employee_id, type_id, check_in, check_out FROM hr_attendance_sheet {where_clause}", params)
            result['data'] = cr.dictfetchall()
            result['count'] = len(result['data'])
            return Response(json.dumps({
                    'message': f"Successfully get data Employee(s).",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def create_attendance(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        # API Payload
        # {
        #     "data": [
        #         {
        #             "employee_id": 12,
        #             "type_id": 1,
        #             "check_in": "2026-01-01 07:00:00",
        #             "check_out": "2026-01-01 17:00:00"
        #         },{
        #             "employee_id": 12,
        #             "type_id": 1,
        #             "check_in": "2026-01-01 07:00:00",
        #             "check_out": "2026-01-01 17:00:00"
        #         }
        #     ]
        # }
        jakarta_tz = timezone('Asia/Jakarta')
        try:
            raw_list_to_create = datas.get('data', [])
            if not raw_list_to_create:
                raise ValidationError("Empty Data: Nothing to create")
            # Validate Mandatory Field
            mandatory_fields = ['employee_id', 'type_id']
            for line_to_check in raw_list_to_create:
                to_check_keys = line_to_check.keys()
                if any([(x not in to_check_keys) for x in mandatory_fields]):
                    raise ValidationError(f"This field are mandatory. ({','.join(mandatory_fields)})")

            AttSheet = request.env['hr.attendance.sheet']
            created_records = AttSheet.browse()
            updated_records = AttSheet.browse()

            for vals in raw_list_to_create:
                # 1. Cek apakah employee ada
                employee_found = request.env['hr.employee'].sudo().search([('id', '=', vals.get('employee_id'))], limit=1)
                if not employee_found:
                    raise ValidationError(f"Employee with id {vals.get('employee_id')} not found")
                attendance_type = request.env['hr.attendance.type'].sudo().search([('id', '=', vals.get('type_id'))], limit=1)
                if not attendance_type:
                    raise ValidationError(f"Attendance Type with id {vals.get('type_id')} not found")
                if attendance_type.code == 'KJ' and not (vals.get('check_in') or vals.get('check_out')):
                    raise ValidationError(f"Attendance Type 'KJ' requires both 'check_in' or 'check_out' times")
                elif (vals.get('check_in') or vals.get('check_out')) and attendance_type.code != 'KJ':
                    raise ValidationError(f"Attendance Type '{attendance_type.code}' does not allow 'check_in' or 'check_out' times")

                # Tentukan tanggal dari check_in atau check_out
                check_in_str = vals.get('check_in')
                check_out_str = vals.get('check_out')
                attendance_date = None
                if check_in_str:
                    check_in = jakarta_tz.localize(datetime.strptime(check_in_str, "%Y-%m-%d %H:%M:%S")).astimezone(utc).replace(tzinfo=None)
                    attendance_date = check_in.date()
                    check_in_str = check_in.strftime("%Y-%m-%d %H:%M:%S")
                elif check_out_str:
                    check_out = jakarta_tz.localize(datetime.strptime(check_out_str, "%Y-%m-%d %H:%M:%S")).astimezone(utc).replace(tzinfo=None)
                    attendance_date = check_out.date()
                    check_out_str = check_out.strftime("%Y-%m-%d %H:%M:%S")

                # 2. Cek existing attendance sheet berdasarkan employee dan tanggal check_in/check_out
                domain = [('employee_id', '=', employee_found.id)]
                if attendance_date:
                    domain.append(('date', '=', attendance_date))
                att_found = AttSheet.sudo().search(domain, limit=1)

                att_vals = {
                    'employee_id': employee_found.id,
                    'type_id': vals.get('type_id'),
                    'date': attendance_date,
                    'check_in': check_in_str,
                    'check_out': check_out_str,
                }

                if att_found:
                    att_found.with_user(check_user).write(att_vals)
                    updated_records |= att_found
                else:
                    new_att = AttSheet.with_user(check_user).create(att_vals)
                    created_records |= new_att

            all_records = created_records | updated_records
            if not all_records:
                raise MissingError("Failed to create or update Attendance")

            def _serialize(rec):
                return {
                    'id': rec.id,
                    'employee_id': rec.employee_id.id,
                    'type_id': rec.type_id.id,
                    'date': rec.date,
                    'check_in': rec.check_in,
                    'check_out': rec.check_out
                }

            result = {
                'data': list(map(_serialize, all_records)),
                'count': len(all_records),
            }
            return Response(json.dumps({
                    'message': "Successfully processed Attendance Sheet(s)",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)