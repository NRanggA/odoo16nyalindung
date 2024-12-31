from odoo import http, exceptions, models, fields
from odoo.http import request, Response
import json
from io import BytesIO
from datetime import datetime, time
import pytz
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta
import base64

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
        # added_addrs = request.env['c10i_base_api.client.list'].sudo().search([('name','=',client_req_addrs)])
        # if not added_addrs:
            # added_addrs = request.env['c10i_base_api.client.list'].sudo().create({'name': client_req_addrs})
        # Blacklisted Address
        # if added_addrs.blacklist:
            # return False, 'Unauthorized, You have failed authorization proceess several times. Please contact the admin for further details.'
        # elif added_addrs.number_of_error_half_hour_allowed<=0:
            # return False, 'Temporary Blocked, You have failed authorization proceess several times. Please wait for 30 minutes or contact the admin for further details.'
        
        datas = self._get_payload() or {}
        token = str(datas.get('token'))
        if not token:
            # added_addrs.write({
            #     'number_of_error_allowed': added_addrs.number_of_error_allowed-1,
            #     'number_of_error_half_hour_allowed': added_addrs.number_of_error_half_hour_allowed-1,
            # })
            return False, 'Unauthorized, please contact the admin for further details.'
        
        # check_token = request.env['res.users'].sudo().search([('mydaya_api_token','=',token)])
        global_token = request.env['ir.config_parameter'].sudo().get_param('mydaya_api_token', False)
        check_token = token == global_token
        # if not check_token:
            # Add to Client List
            # added_addrs.write({
            #     'number_of_error_allowed': added_addrs.number_of_error_allowed-1,
            #     'number_of_error_half_hour_allowed': added_addrs.number_of_error_half_hour_allowed-1,
            # })
        return check_token, 'Invalid token, please use a valid token.'

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
        check_token, message = self._verify_auth()
        if not check_token:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            # VALIDASI FIELD
            if not datas.get('username',False):
                return Response(json.dumps({'message': "username Wajib diisi"}), headers=HEADERS, status=404)
            employee_found = request.env['hr.employee'].sudo().search([('mydaya_user_login','=',datas['username'])])
            if not employee_found:
                return Response(json.dumps({'message': "Unauthorized, username not found."}), headers=HEADERS, status=401)
            if employee_found.mydaya_user_pwd != datas.get('pwdlain', False):
                return Response(json.dumps({'message': "Unauthorized, please contact the admin for further details."}), headers=HEADERS, status=401)

            result = {
                'status': 1,
                'uname': employee_found.mydaya_user_login or '',
                'fname': employee_found.name or '',
                'dept': employee_found.department_id.name if employee_found.department_id else '',
                'uemail': employee_found.work_email or '',
                'divisi': employee_found.department_id.name if employee_found.department_id else '',
                'sect': '',
                'area': 'OFFICE',
                'golongan': '',
                'nip': employee_found.no_induk or '',
                'latacuan': str(employee_found.company_id.company_latitude or ''),
                'lngacuan': str(employee_found.company_id.company_longitude or ''),
                'valjarak': int(employee_found.company_id.attendance_radius_distance or '0'),
                'subco': '2'
            }
            return Response(json.dumps(result, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)
    
    @http.route(f"{ROUTES}/foto", auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_employee_image(self, nip):
        # check_token, message = self._verify_auth()
        # if not check_token:
        #     return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        try:
            # VALIDASI FIELD
            if not nip:
                return Response(json.dumps({'message': "Nomor Induk Pegawai Wajib diisi"}), headers=HEADERS, status=404)
            employee_found = request.env['hr.employee'].sudo().search([('no_induk','=',nip)])
            if not employee_found:
                return Response(json.dumps({'message': f"Nomor Induk Pegawai {nip} tidak ditemukan"}), headers=HEADERS, status=422)
            result = {}
            # record = request.env['ir.binary']._find_record(xmlid, model, id and int(id), access_token)
            stream = request.env['ir.binary']._get_image_stream_from(employee_found, 'image_1920')
            # if request.httprequest.args.get('access_token'):
            #     stream.public = True
            send_file_kwargs = {
                'as_attachment': False,
                'download_name': 'profile-picture.jpg',
                'max_age': None
            }
            res = stream.get_response(**send_file_kwargs)
            # res.headers['Content-Security-Policy'] = "default-src 'none'"
            return res
            # return Response(json.dumps(result, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    # Request
    # {
    #     "token":"73b12f9a7b97a77420215b14f2220d22",
    #     "nip":"111111111111111"
    # }
    # Response
    # {
    #     "masuk": "08:25",
    #     "pulang": "14:39"
    # }
    @http.route(f"{ROUTES}/dataPresensi", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def get_attendance_today(self):
        check_token, message = self._verify_auth()
        if not check_token:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        datas = self._get_payload() or {}
        try:
            # VALIDASI FIELD
            if not datas.get('nip',False):
                return Response(json.dumps({'message': "Nomor Induk Pegawai Wajib diisi"}), headers=HEADERS, status=404)
            employee_found = request.env['hr.employee'].sudo().search([('no_induk','=',datas['nip'])])
            if not employee_found:
                return Response(json.dumps({'message': f"Nomor Induk Pegawai {datas['nip']} tidak ditemukan"}), headers=HEADERS, status=422)
            
            # GET ATTENDANCE
            today_att = request.env['hr.attendance.sheet'].sudo().search([('date','=',fields.Date.today()),
                                            ('employee_id','=',employee_found.id)])
            masuk = pulang = ""
            if today_att.check_in:
                masuk = today_att.check_in.astimezone(timezone('Asia/Jakarta'))
            if today_att.check_out:
                pulang = today_att.check_out.astimezone(timezone('Asia/Jakarta'))
            result = {
                'masuk': masuk.strftime('%H:%M') if masuk else '',
                'pulang': pulang.strftime('%H:%M') if pulang else ''
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
        check_token, message = self._verify_auth()
        if not check_token:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            # VALIDASI FIELD
            if not datas.get('nip',False):
                return Response(json.dumps({'message': "Nomor Induk Pegawai Wajib diisi"}), headers=HEADERS, status=404)
            employee_found = request.env['hr.employee'].sudo().search([('no_induk','=',datas['nip'])])
            if not employee_found:
                return Response(json.dumps({'message': f"Nomor Induk Pegawai {datas['nip']} tidak ditemukan"}), headers=HEADERS, status=422)
            
            # INSERT ATTENDANCE
            value_to_insert = {
                'employee_id': employee_found.id,
                'longitude': datas.get('longitude','0.0'),
                'latitude': datas.get('latitude','0.0'),
                # 'waktu': datas.get('waktu',False),
                'waktu': fields.Datetime.now(),
                # 'version': datas.get('version',''),
                # 'foto': datas.get('foto', False),
                'keterangan': datas.get('keterangan',''),
                'statusmasuk': datas.get('statusmasuk',''),
            }
            new_att_log = request.env['ny.attendance.log'].sudo().create(value_to_insert)
            if datas.get('foto'):
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': 'Attendance.jpeg',
                    'datas': datas['foto'].encode('utf-8'),
                    'res_model': 'ny.attendance.log',
                    'res_id': new_att_log.id,
                    'res_field': 'foto',
                    'mimetype': 'image/jpeg',
                    'public': True,
                })
            new_att_log.find_attendance_sheet()
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
    #         "nip": "999999",
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
        check_token, message = self._verify_auth()
        if not check_token:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            # VALIDASI FIELD
            if not datas.get('nip',False):
                return Response(json.dumps({'message': "Nomor Induk Pegawai Wajib diisi"}), headers=HEADERS, status=404)
            employee_found = request.env['hr.employee'].sudo().search([('no_induk','=',datas['nip'])])
            if not employee_found:
                return Response(json.dumps({'message': f"Nomor Induk Pegawai {datas['nip']} tidak ditemukan"}), headers=HEADERS, status=422)
            
            # GET ATTENDANCE
            start_date = fields.Date.today() + relativedelta(day=1)
            end_date = start_date + relativedelta(months=1) + relativedelta(day=1) - relativedelta(days=1)
            domain = [('employee_id','=',employee_found.id), ('date','>=', start_date), 
                        ('date','<=', end_date)]
            attendances = request.env['hr.attendance.sheet'].sudo().search(domain, order='date desc')
            week_day_names = {0: 'Senin', 1: 'Selasa', 2: 'Rabu',
                3: 'Kamis', 4: "Jum'at", 6: 'Sabtu', 7: 'Minggu'}
            res_att = []
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1).value
            for att in attendances:
                if att.type_id.code!='KJ' and not att.att_log_ids:
                    continue
                namafile = statusmasuk = ketmasuk = ""

                first_att = att.att_log_ids.sorted(key=lambda t: t.waktu)[0]
                last_att = att.att_log_ids.sorted(key=lambda t: t.waktu, reverse=True)[0]
                statusmasuk = first_att.statusmasuk
                ketmasuk = first_att.keterangan
                ketkeluar = last_att.keterangan
                query_attachment = f"""SELECT id,name FROM ir_attachment WHERE res_model='ny.attendance.log' 
                    and res_field='foto' and res_id={first_att.id}"""
                request.env.cr.execute(query_attachment)
                attc_ids = request.env.cr.fetchone()
                if attc_ids:
                    namafile = f"{base_url}/web/image/{attc_ids[0]}/{attc_ids[1]}"
                masuk = pulang = ""
                if att.check_in:
                    masuk = att.check_in.astimezone(timezone('Asia/Jakarta'))
                if att.check_out:
                    pulang = att.check_out.astimezone(timezone('Asia/Jakarta'))
                att_vals = {
                    "nip": employee_found.no_induk,
                    "masuk": f"{masuk.strftime('%H:%M')}{', '+str(round(att.distance_in,2))+' km' if att.distance_in else ''}{', '+ketmasuk}" if masuk else '', #"15:15, Jarak :0.05 Km, Keterangan: keterangan",
                    "pulang": f"{pulang.strftime('%H:%M')}{', '+str(round(att.distance_out,2))+' km' if att.distance_out else ''}{', '+ketkeluar}" if pulang else '', #"15:16, Jarak :0.05 Km, Keterangan: keterangan",
                    "namafile": namafile,
                    "namahari": week_day_names.get(att.date.weekday(),"") if att.date else "",
                    "tanggal": att.date.strftime("%d %b %Y") if att.date else "",
                    "statusmasuk": statusmasuk
                }
                res_att.append(att_vals)
            return Response(json.dumps(res_att), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)

    # Request
    # {
    #     "token":"73b12f9a7b97a77420215b14f2220d22",
    #     "nip":"1111111111",
    #     "tgl":"202407"
    # }
    # Response
    # [
    #     {
    #         "nip": "1",
    #         "masuk": "08:43, Jarak :18.52 Km, Keterangan: karena tes wfh",
    #         "pulang": "-",
    #         "namafile": "https://api-gateway.nyalindung.co.id/assets/uploads/presensi/1/202407/1_20240702084340.jpg",
    #         "namahari": "Selasa",
    #         "tanggal": "02 July 2024",
    #         "statusmasuk": "WFH"
    #     }
    # ]
    @http.route(f"{ROUTES}/historyPresensiBln", auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def get_attendance_log_bln(self):
        check_token, message = self._verify_auth()
        if not check_token:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=401)
        
        datas = self._get_payload() or {}
        try:
            # VALIDASI FIELD
            if not datas.get('nip',False):
                return Response(json.dumps({'message': "Nomor Induk Pegawai Wajib diisi"}), headers=HEADERS, status=404)
            employee_found = request.env['hr.employee'].sudo().search([('no_induk','=',datas['nip'])])
            if not employee_found:
                return Response(json.dumps({'message': f"Nomor Induk Pegawai {datas['nip']} tidak ditemukan"}), headers=HEADERS, status=422)
            
            # GET ATTENDANCE
            start_date = datetime.strptime(datas.get('tgl'), "%Y%m")
            end_date = start_date + relativedelta(months=1) + relativedelta(day=1) - relativedelta(days=1)
            domain = [('employee_id','=',employee_found.id), ('date','>=', start_date), 
                        ('date','<=', end_date)]
            attendances = request.env['hr.attendance.sheet'].sudo().search(domain, order='date desc')
            week_day_names = {0: 'Senin', 1: 'Selasa', 2: 'Rabu',
                3: 'Kamis', 4: "Jum'at", 6: 'Sabtu', 7: 'Minggu'}
            res_att = []
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1).value
            for att in attendances:
                if att.type_id.code!='KJ' and not att.att_log_ids:
                    continue
                namafile = statusmasuk = ketmasuk = ketpulang = ""
                if att.att_log_ids:
                    first_att = att.att_log_ids.sorted(key=lambda t: t.waktu)[0]
                    last_att = att.att_log_ids.sorted(key=lambda t: t.waktu, reverse=True)[0]
                    statusmasuk = first_att.statusmasuk
                    ketmasuk = first_att.keterangan
                    ketpulang = last_att.keterangan
                    query_attachment = f"""SELECT id,name FROM ir_attachment WHERE res_model='ny.attendance.log' 
                        and res_field='foto' and res_id={first_att.id}"""
                    request.env.cr.execute(query_attachment)
                    attc_ids = request.env.cr.fetchone()
                    if attc_ids:
                        namafile = f"{base_url}/web/image/{attc_ids[0]}/{attc_ids[1]}"
                masuk = pulang = ""
                if att.check_in:
                    masuk = att.check_in.astimezone(timezone('Asia/Jakarta'))
                if att.check_out:
                    pulang = att.check_out.astimezone(timezone('Asia/Jakarta'))
                att_vals = {
                        "nip": employee_found.no_induk,
                        "masuk": f"{masuk.strftime('%H:%M')}{', '+str(round(att.distance_in,2))+' km' if att.distance_in else ''}{', '+ketmasuk}" if masuk else '',
                        "pulang": f"{pulang.strftime('%H:%M')}{', '+str(round(att.distance_out,2))+' km' if att.distance_out else ''}{', '+ketpulang}" if pulang else '',
                        "namafile": namafile,
                        "namahari": week_day_names.get(att.date.weekday(),"") if att.date else "",
                        "tanggal": att.date.strftime("%d %b %Y") if att.date else "",
                        "statusmasuk": statusmasuk
                }
                res_att.append(att_vals)
            return Response(json.dumps(res_att), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)