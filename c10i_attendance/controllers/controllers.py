# -*- coding: utf-8 -*-
# from odoo import http


# class C10iAttendance(http.Controller):
#     @http.route('/c10i_attendance/c10i_attendance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_attendance/c10i_attendance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_attendance.listing', {
#             'root': '/c10i_attendance/c10i_attendance',
#             'objects': http.request.env['c10i_attendance.c10i_attendance'].search([]),
#         })

#     @http.route('/c10i_attendance/c10i_attendance/objects/<model("c10i_attendance.c10i_attendance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_attendance.object', {
#             'object': obj
#         })
