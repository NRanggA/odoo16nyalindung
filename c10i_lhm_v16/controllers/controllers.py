# -*- coding: utf-8 -*-
# from odoo import http


# class C10iLhmV16(http.Controller):
#     @http.route('/c10i_lhm_v16/c10i_lhm_v16', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_lhm_v16/c10i_lhm_v16/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_lhm_v16.listing', {
#             'root': '/c10i_lhm_v16/c10i_lhm_v16',
#             'objects': http.request.env['c10i_lhm_v16.c10i_lhm_v16'].search([]),
#         })

#     @http.route('/c10i_lhm_v16/c10i_lhm_v16/objects/<model("c10i_lhm_v16.c10i_lhm_v16"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_lhm_v16.object', {
#             'object': obj
#         })
