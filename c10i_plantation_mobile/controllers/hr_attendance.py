from odoo import http, fields
from odoo.http import request, Response
# from odoo.exceptions import MissingError, ValidationError

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

import json
from datetime import datetime
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


ROUTES = f"{BASE_ROUTE}/plantation/attendance"

class Attendance(ApiBase):
    @http.route(f"{ROUTES}/today", auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_attendance_today2(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        datas = self._get_payload() or {}
        try:
            current_user = request.env['res.users'].sudo().browse(check_user)
            employee_found = current_user.employee_id
            if not employee_found:
                return Response(json.dumps({'message': f"Pegawai atas User {current_user.name} tidak ditemukan"}), headers=HEADERS, status=422)
            
            # GET ATTENDANCE
            jakarta = timezone('Asia/Jakarta')
            today = utc.localize(fields.Datetime.now()).astimezone(jakarta)
            today_att = request.env['hr.attendance.sheet'].sudo().search([('date','=',today),
                                            ('employee_id','=',employee_found.id)])
            
            checkin = checkout = breakin = breakout = overtimein = overtimeout = ""
            if today_att.check_in:
                checkin = today_att.check_in.astimezone(timezone('Asia/Jakarta'))
            if today_att.check_out:
                checkout = today_att.check_out.astimezone(timezone('Asia/Jakarta'))
            if today_att.break_in:
                breakin = today_att.break_in.astimezone(timezone('Asia/Jakarta'))
            if today_att.break_out:
                breakout = today_att.break_out.astimezone(timezone('Asia/Jakarta'))
            if today_att.overtime_in:
                overtimein = today_att.overtime_in.astimezone(timezone('Asia/Jakarta'))
            if today_att.overtime_out:
                overtimeout = today_att.overtime_out.astimezone(timezone('Asia/Jakarta'))
            result = {
                'check_in': checkin.strftime('%H:%M') if checkin else '',
                'check_out': checkout.strftime('%H:%M') if checkout else '',
                'break_out': breakout.strftime('%H:%M') if breakout else '',
                'break_in': breakin.strftime('%H:%M') if breakin else '',
                'overtime_in': overtimein.strftime('%H:%M') if overtimein else '',
                'overtime_out': overtimeout.strftime('%H:%M') if overtimeout else '',
            }
            return Response(json.dumps(result, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)        
    
    _week_day_names = {0: 'Senin', 1: 'Selasa', 2: 'Rabu',
                3: 'Kamis', 4: "Jum'at", 5: 'Sabtu', 6: 'Minggu'}
    _base_url = ""
    def _get_attendance_info(self, attendance):
        checkin_picture_url = ketmasuk = ketkeluar = ""
        checkin = checkout = overtimein = overtimeout = ""

        if attendance.att_log_ids:
            if len(attendance.att_log_ids.ids)>1:
                first_att = attendance.att_log_ids.sorted(key=lambda t: t.waktu)[0]
                # last_att = attendance.att_log_ids.sorted(key=lambda t: t.waktu, reverse=True)[0]
            else:
                first_att = attendance.att_log_ids
                # last_att = attendance.att_log_ids
            # ketmasuk = first_att.keterangan
            # ketkeluar = last_att.keterangan
            query_attachment = f"""SELECT id,name FROM ir_attachment WHERE res_model='ny.attendance.log' 
                and res_field='foto' and res_id={first_att.id}"""
            request.env.cr.execute(query_attachment)
            attc_ids = request.env.cr.fetchone()
            if attc_ids:
                checkin_picture_url = f"{self._base_url}/web/image/{attc_ids[0]}/{attc_ids[1]}"
        
        if attendance.check_in:
            checkin = attendance.check_in.astimezone(timezone('Asia/Jakarta'))
        if attendance.check_out:
            checkout = attendance.check_out.astimezone(timezone('Asia/Jakarta'))
        if attendance.overtime_in:
            overtimein = attendance.overtime_in.astimezone(timezone('Asia/Jakarta'))
        if attendance.overtime_out:
            overtimeout = attendance.overtime_out.astimezone(timezone('Asia/Jakarta'))
        
        return {
            # "date": attendance.date.strftime("%d %b %Y") if attendance.date else "",
            "date": attendance.date.strftime("%Y-%m-%d") if attendance.date else "",
            "day_of_week": self._week_day_names.get(attendance.date.weekday(),"") if attendance.date else "",
            "check_in_picture": checkin_picture_url,
            "check_in": f"{checkin.strftime('%H:%M')}{', '+str(round(attendance.distance_in,2))+' km' if attendance.distance_in else ''}{', '+ketmasuk}" if checkin else '', #"15:15, Jarak :0.05 Km, Keterangan: keterangan",
            "check_out": f"{checkout.strftime('%H:%M')}{', '+str(round(attendance.distance_out,2))+' km' if attendance.distance_out else ''}{', '+ketkeluar}" if checkout else '', #"15:16, Jarak :0.05 Km, Keterangan: keterangan",
            "overtime_in": overtimein.strftime('%H:%M') if overtimein else '',
            "overtime_out": overtimeout.strftime('%H:%M') if overtimeout else '',
        }

    @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_attendance(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            current_user = request.env['res.users'].sudo().browse(check_user)
            employee_found = current_user.employee_id
            if not employee_found:
                return Response(json.dumps({'message': f"Pegawai atas User {current_user.name} tidak ditemukan"}), headers=HEADERS, status=422)
            
            # GET ATTENDANCE
            jakarta = timezone('Asia/Jakarta')
            
            today = utc.localize(fields.Datetime.now()).astimezone(jakarta)
            
            if not datas.get('date_from'):
                start_date = today - relativedelta(days=7)
            else:
                start_date = datetime.strptime(datas.get('date_from'), "%Y-%m-%d")
            
            if not datas.get('date_to'):
                end_date = today
            else:
                end_date = datetime.strptime(datas.get('date_to'), "%Y-%m-%d")
            domain = [('employee_id','=',employee_found.id), ('date','>=', start_date), 
                        ('date','<=', end_date)]
            attendances = request.env['hr.attendance.sheet'].sudo().search(domain, order='date desc')
            res_att = []
            self._base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1).value
            for att in attendances:
                if att.type_id.code!='KJ' and not att.att_log_ids:
                    continue
                res_att.append(self._get_attendance_info(att))
            return Response(json.dumps({
                    "message": "Get Data Successfull",
                    "data": res_att
                }), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)
    
    
    @http.route([f"{ROUTES}/check-in",
                f"{ROUTES}/check-out", 
                f"{ROUTES}/break-in", 
                f"{ROUTES}/break-out", 
                f"{ROUTES}/overtime-in", 
                f"{ROUTES}/overtime-out"],
                auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def set_attendance(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}        
        try:
            current_user = request.env['res.users'].sudo().browse(check_user)
            employee_found = current_user.employee_id
            if not employee_found:
                return Response(json.dumps({'message': f"Pegawai atas User {current_user.name} tidak ditemukan"}), headers=HEADERS, status=422)
            
            # INSERT ATTENDANCE
            type = request.httprequest.base_url.split('/')[-1]
            message_mark = {
                'check-in': "Check In",
                'check-out': "Check Out",
                'break-in': "Break In",
                'break-out': "Break Out",
                'overtime-in': "Overtime In",
                'overtime-out': "Overtime Out"
            }
            
            value_to_insert = {
                'employee_id': employee_found.id,
                'latitude': datas.get('latitude','0.0'),
                'longitude': datas.get('longitude','0.0'),
                'waktu': fields.Datetime.now(),
                # 'date': fields.Datetime.now(),
                'keterangan': datas.get('note',''),
                # 'statusmasuk': datas.get('statusmasuk',''),
                'type': type
            }
            new_att_log = request.env['ny.attendance.log'].with_user(check_user).create(value_to_insert)
            if datas.get('image'):
                request.env['ir.attachment'].sudo().create({
                    'name': 'Attendance.jpeg',
                    'datas': datas['image'].encode('utf-8'),
                    'res_model': 'ny.attendance.log',
                    'res_id': new_att_log.id,
                    'res_field': 'foto',
                    'mimetype': 'image/jpeg',
                    'public': True,
                })
            new_att_log.find_attendance_sheet()
            return Response(json.dumps({
                'message': f"{message_mark.get(type)} Successfull!"
                # 'data': result,
            }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)
