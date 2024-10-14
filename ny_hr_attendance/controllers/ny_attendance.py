from odoo import http, exceptions, models, fields
from odoo.http import request, Response
import json
from datetime import datetime, time
import pytz
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/attendance"

class NyAttendance(ApiBase):
    def _verify_auth(self):
        '''
            Verification using nyalindung standard API
            we will verify based on Token
        '''
        # # Create or Update API Client List
        client_req_addrs = request.httprequest.environ['REMOTE_ADDR']
        # print(">>>>>>>>>>>>>>>>>>>>>>> verify_auth", client_req_addrs)
        added_addrs = request.env['c10i_base_api.client.list'].sudo().search([('name','=',client_req_addrs)])
        if not added_addrs:
            added_addrs = request.env['c10i_base_api.client.list'].sudo().create({'name': client_req_addrs})
        print(">>>>>>>>>>>>>>>>>>>>>>> verify_auth", added_addrs)
        # Blacklisted Address
        if added_addrs.blacklist:
            return False, 'Unauthorized, You have failed authorization proceess several times. Please contact the admin for further details.'
        elif added_addrs.number_of_error_half_hour_allowed<=0:
            return False, 'Temporary Blocked, You have failed authorization proceess several times. Please wait for 30 minutes or contact the admin for further details.'
        
        datas = self._get_payload() or {}
        print("::::::::::::::::::::::::", datas)
        token = str(datas.get('token'))
        print("::::::::::::::::::::::::", token)
        if not token:
            # added_addrs.write({
            #     'number_of_error_allowed': added_addrs.number_of_error_allowed-1,
            #     'number_of_error_half_hour_allowed': added_addrs.number_of_error_half_hour_allowed-1,
            # })
            return False, 'Unauthorized, please contact the admin for further details.'
        
        # check_user = request.env['res.users.apikeys']._check_credentials(scope='rpc', key=token)
        check_user = request.env['res.users'].sudo().search([('mydaya_api_token','=',token)])
        print("::::::::::::::::::::::::", check_user)
        # if not check_user:
        #     # Add to Client List
        #     added_addrs.write({
        #         'number_of_error_allowed': added_addrs.number_of_error_allowed-1,
        #         'number_of_error_half_hour_allowed': added_addrs.number_of_error_half_hour_allowed-1,
        #     })
        return check_user, 'Invalid token, please use a valid token.'

    # Request
    # Body
    # {
    #     "username":"12345",
    #     "pwdlain":"827ccb0eea8a706c4c34a16891f84e7b",
    #     "token":"73b12f9a7b97a77420215b14f2220d22",
    #     "subco":"2"
    # }
    # Response
    # {
    #     "status": 1,
    #     "uname": "12345",
    #     "fname": "PEGAWAI NYALINDUNG",
    #     "dept": "INFORMATION TECHNOLOGY",
    #     "uemail": null,
    #     "divisi": "IT CORPORATE",
    #     "sect": "",
    #     "area": "OFFICE",
    #     "golongan": "",
    #     "nip": "1",
    #     "latacuan": "-6.796132",
    #     "lngacuan": "107.4418337",
    #     "valjarak": 100,
    #     "subco": "2"
    # }
    @http.route(f"{ROUTES}/loginNew", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def do_login(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        # datas = self._get_payload() or {}
        try:
            result = {
                'status': 1,
                'uname': check_user.login,
                'fname': check_user.employee_id.name,
                'dept': check_user.employee_id.department_id.name,
                'uemail': check_user.login,
                'divisi': check_user.employee_id.department_id.name,
                'sect': '',
                'area': 'OFFICE',
                'golongan': '',
                'nip': check_user.employee_id.no_induk,
                'latacuan': check_user.employee_id.lat_acuan,
                'lngacuan': check_user.employee_id.long_acuan,
                'valjarak': check_user.employee_id.value_jarak,
                'subco': '2'
            }
            return Response(json.dumps(result, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)
    
    # Request
    # {
    #     "token":"73b12f9a7b97a77420215b14f2220d22",
    #     "nip":"1"
    # }
    # Response
    # {
    #     "masuk": "08:25",
    #     "pulang": "14:39"
    # }
    @http.route(f"{ROUTES}/dataPresensi", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def get_attendance_today(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        datas = self._get_payload() or {}
        try:
            today_att = request.env['hr.attendance.sheet'].sudo().search([('date','=',fields.Date.today()),('employee_id','=',check_user.employee_id.id)])
            result = {
                'masuk': today_att.check_in.strftime('%H:%M') if today_att and today_att.check_in else '',
                'pulang': today_att.check_out.strftime('%H:%M') if today_att and today_att.check_out else ''
            }
            return Response(json.dumps(result, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    # Request
    # {
    #     "token":"73b12f9a7b97a77420215b14f2220d22",
    #     "nip":"1",
    #     "longitude":"longitude",
    #     "latitude":"latitude",
    #     "waktu":"2024-09-19 14:53:53",
    #     "version":"2.0.1",
    #     "foto":"base64code",
    #     "keterangan":"keterangan",
    #     "statusmasuk":"WFO"// isi dengan WFO,WFH
    # }
    # Response
    # {
    #     "status": 1,
    #     "deskripsi": "Data berhasil disimpan"
    # }
    @http.route(f"{ROUTES}/kirimPresensi", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def update_attendance(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        # print("::::::::::::::::", datas)
        try:
            # VALIDASI FIELD

            # INSERT ATTENDANCE
            value_to_insert = {
                'employee_id': check_user.employee_id.id,
                'longitude': datas.get('longitude',''),
                'latitude': datas.get('latitude',''),
                'waktu': datas.get('waktu',False),
                # 'version': datas.get('version',''),
                # 'foto': datas.get('foto', False),
                'keterangan': datas.get('keterangan',''),
                'statusmasuk': datas.get('statusmasuk',''),
            }
            # print(".............value_to_insert", value_to_insert)
            new_attendance_log = request.env['ny.attendance.log'].sudo().create(value_to_insert)
            # print(".............new_attendance_log", new_attendance_log)

            result = {
                'status': 1,
                'deskripsi': 'Data berhasil disimpan'
            }
            return Response(json.dumps(result, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)
        
    # Request
    # {
    #     "token":"73b12f9a7b97a77420215b14f2220d22",
    #     "nip":"999999"
    # }
    # Response
    # [
    #     {
    #         "NIP": "999999",
    #         "masuk": "15:15, Jarak :0.05 Km, Keterangan: keterangan",
    #         "pulang": "15:16, Jarak :0.05 Km, Keterangan: keterangan",
    #         "namafile": "https://api-gateway.nyalindung.co.id/assets/uploads/presensi/999999/202409/999999_20240927151533.jpg",
    #         "namahari": "Jum'at",
    #         "tanggal": "27 Sep 2024",
    #         "statusmasuk": "WFO"
    #     }
    # ]
    @http.route(f"{ROUTES}/historyPresensi", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def get_attendance_log(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            # VALIDASI FIELD

            # GET ATTENDANCE
            domain = [('employee_id','=',check_user.employee_id.id),('date','=',fields.Date.today())]
            attendances = request.env['hr.attendance.sheet'].sudo().search(domain)
            week_day_names = {
                0: 'Senin',
                1: 'Selasa',
                2: 'Rabu',
                3: 'Kamis',
                4: "Jum'at",
                6: 'Sabtu',
                7: 'Minggu',
            }
            res_att = []
            for att in attendances:
                att_vals = {
                        "NIP": check_user.employee_id.no_induk,
                        "masuk": att.check_in.strftime('%H:%M') if att.check_in else '', #"15:15, Jarak :0.05 Km, Keterangan: keterangan",
                        "pulang": att.check_out.strftime('%H:%M') if att.check_out else '', #"15:16, Jarak :0.05 Km, Keterangan: keterangan",
                        "namafile": "https://api-gateway.nyalindung.co.id/assets/uploads/presensi/999999/202409/999999_20240927151533.jpg",
                        "namahari": week_day_names.get(att.check_in.weekday(),"") if att.check_in else "",
                        "tanggal": att.check_in.strftime("%d %b %Y") if att.check_in else "",
                        # "statusmasuk": "WFO"
                }
                res_att.append(att_vals)
            return Response(json.dumps(res_att), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    # Request
    # {
    #     "token":"73b12f9a7b97a77420215b14f2220d22",
    #     "nip":"1",
    #     "tgl":"2024-07-19"
    # }
    # Response
    # [
    #     {
    #         "NIP": "1",
    #         "masuk": "08:43, Jarak :18.52 Km, Keterangan: karena tes wfh",
    #         "pulang": "-",
    #         "namafile": "https://api-gateway.nyalindung.co.id/assets/uploads/presensi/1/202407/1_20240702084340.jpg",
    #         "namahari": "Selasa",
    #         "tanggal": "02 Jul 2024",
    #         "statusmasuk": "WFH"
    #     }
    # ]
    @http.route(f"{ROUTES}/historyPresensiBln", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def get_attendance_log_bln(self):
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            # VALIDASI FIELD

            # GET ATTENDANCE
            date = datetime.strptime(datas.get('tgl'), "%Y-%m-%d")
            start_date = date + relativedelta(day=1)
            end_date = date + relativedelta(months=1) + relativedelta(day=1)
            domain = [('employee_id','=',check_user.employee_id.id),
                    ('date','>=', start_date),
                    ('date','<=', end_date)]
            attendances = request.env['hr.attendance.sheet'].sudo().search(domain)
            week_day_names = {
                0: 'Senin',
                1: 'Selasa',
                2: 'Rabu',
                3: 'Kamis',
                4: "Jum'at",
                6: 'Sabtu',
                7: 'Minggu',
            }
            res_att = []
            for att in attendances:
                att_vals = {
                        "NIP": check_user.employee_id.no_induk,
                        "masuk": att.check_in.strftime('%H:%M') if att.check_in else '', #"15:15, Jarak :0.05 Km, Keterangan: keterangan",
                        "pulang": att.check_out.strftime('%H:%M') if att.check_out else '', #"15:16, Jarak :0.05 Km, Keterangan: keterangan",
                        "namafile": "https://api-gateway.nyalindung.co.id/assets/uploads/presensi/999999/202409/999999_20240927151533.jpg",
                        "namahari": week_day_names.get(att.check_in.weekday(),"") if att.check_in else "",
                        "tanggal": att.date.strftime("%d %b %Y") if att.date else "",
                        # "statusmasuk": "WFO"
                }
                res_att.append(att_vals)
            return Response(json.dumps(res_att), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)