# -*- coding: utf-8 -*-
# from odoo import http


# class NyAccount(http.Controller):
#     @http.route('/ny_account/ny_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ny_account/ny_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ny_account.listing', {
#             'root': '/ny_account/ny_account',
#             'objects': http.request.env['ny_account.ny_account'].search([]),
#         })

#     @http.route('/ny_account/ny_account/objects/<model("ny_account.ny_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ny_account.object', {
#             'object': obj
#         })
