# -*- coding: utf-8 -*-
# from odoo import http


# class C10iPlantationContract(http.Controller):
#     @http.route('/c10i_plantation_contract/c10i_plantation_contract', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_plantation_contract/c10i_plantation_contract/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_plantation_contract.listing', {
#             'root': '/c10i_plantation_contract/c10i_plantation_contract',
#             'objects': http.request.env['c10i_plantation_contract.c10i_plantation_contract'].search([]),
#         })

#     @http.route('/c10i_plantation_contract/c10i_plantation_contract/objects/<model("c10i_plantation_contract.c10i_plantation_contract"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_plantation_contract.object', {
#             'object': obj
#         })
