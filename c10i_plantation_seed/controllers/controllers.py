# -*- coding: utf-8 -*-
# from odoo import http


# class C10iPlantationSeed(http.Controller):
#     @http.route('/c10i_plantation_seed/c10i_plantation_seed', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_plantation_seed/c10i_plantation_seed/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_plantation_seed.listing', {
#             'root': '/c10i_plantation_seed/c10i_plantation_seed',
#             'objects': http.request.env['c10i_plantation_seed.c10i_plantation_seed'].search([]),
#         })

#     @http.route('/c10i_plantation_seed/c10i_plantation_seed/objects/<model("c10i_plantation_seed.c10i_plantation_seed"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_plantation_seed.object', {
#             'object': obj
#         })
