# -*- coding: utf-8 -*-
# from odoo import http


# class C10iAutoAccountMove(http.Controller):
#     @http.route('/c10i_auto_account_move/c10i_auto_account_move', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_auto_account_move/c10i_auto_account_move/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_auto_account_move.listing', {
#             'root': '/c10i_auto_account_move/c10i_auto_account_move',
#             'objects': http.request.env['c10i_auto_account_move.c10i_auto_account_move'].search([]),
#         })

#     @http.route('/c10i_auto_account_move/c10i_auto_account_move/objects/<model("c10i_auto_account_move.c10i_auto_account_move"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_auto_account_move.object', {
#             'object': obj
#         })
