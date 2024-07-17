# -*- coding: utf-8 -*-
# from odoo import http


# class C10iAccountPeriod(http.Controller):
#     @http.route('/c10i_account_period/c10i_account_period', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_account_period/c10i_account_period/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_account_period.listing', {
#             'root': '/c10i_account_period/c10i_account_period',
#             'objects': http.request.env['c10i_account_period.c10i_account_period'].search([]),
#         })

#     @http.route('/c10i_account_period/c10i_account_period/objects/<model("c10i_account_period.c10i_account_period"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_account_period.object', {
#             'object': obj
#         })
