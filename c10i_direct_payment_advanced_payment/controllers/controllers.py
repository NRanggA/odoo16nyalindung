# -*- coding: utf-8 -*-
# from odoo import http


# class C10iAccount(http.Controller):
#     @http.route('/c10i_account/c10i_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_account/c10i_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_account.listing', {
#             'root': '/c10i_account/c10i_account',
#             'objects': http.request.env['c10i_account.c10i_account'].search([]),
#         })

#     @http.route('/c10i_account/c10i_account/objects/<model("c10i_account.c10i_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_account.object', {
#             'object': obj
#         })
