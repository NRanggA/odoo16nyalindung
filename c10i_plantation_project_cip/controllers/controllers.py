# -*- coding: utf-8 -*-
# from odoo import http


# class C10iPlantationProjectCip(http.Controller):
#     @http.route('/c10i_plantation_project_cip/c10i_plantation_project_cip', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_plantation_project_cip/c10i_plantation_project_cip/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_plantation_project_cip.listing', {
#             'root': '/c10i_plantation_project_cip/c10i_plantation_project_cip',
#             'objects': http.request.env['c10i_plantation_project_cip.c10i_plantation_project_cip'].search([]),
#         })

#     @http.route('/c10i_plantation_project_cip/c10i_plantation_project_cip/objects/<model("c10i_plantation_project_cip.c10i_plantation_project_cip"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_plantation_project_cip.object', {
#             'object': obj
#         })
