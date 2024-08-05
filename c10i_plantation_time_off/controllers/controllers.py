# -*- coding: utf-8 -*-
# from odoo import http


# class C10iPlantationTimeOff(http.Controller):
#     @http.route('/c10i_plantation_time_off/c10i_plantation_time_off', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_plantation_time_off/c10i_plantation_time_off/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_plantation_time_off.listing', {
#             'root': '/c10i_plantation_time_off/c10i_plantation_time_off',
#             'objects': http.request.env['c10i_plantation_time_off.c10i_plantation_time_off'].search([]),
#         })

#     @http.route('/c10i_plantation_time_off/c10i_plantation_time_off/objects/<model("c10i_plantation_time_off.c10i_plantation_time_off"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_plantation_time_off.object', {
#             'object': obj
#         })
