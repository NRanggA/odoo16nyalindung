# -*- coding: utf-8 -*-
# from odoo import http


# class C10iPayment(http.Controller):
#     @http.route('/c10i_payment/c10i_payment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_payment/c10i_payment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_payment.listing', {
#             'root': '/c10i_payment/c10i_payment',
#             'objects': http.request.env['c10i_payment.c10i_payment'].search([]),
#         })

#     @http.route('/c10i_payment/c10i_payment/objects/<model("c10i_payment.c10i_payment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_payment.object', {
#             'object': obj
#         })
