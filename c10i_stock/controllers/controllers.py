# -*- coding: utf-8 -*-
# from odoo import http


# class C10iStock(http.Controller):
#     @http.route('/c10i_stock/c10i_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_stock/c10i_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_stock.listing', {
#             'root': '/c10i_stock/c10i_stock',
#             'objects': http.request.env['c10i_stock.c10i_stock'].search([]),
#         })

#     @http.route('/c10i_stock/c10i_stock/objects/<model("c10i_stock.c10i_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_stock.object', {
#             'object': obj
#         })
