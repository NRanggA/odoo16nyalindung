# -*- coding: utf-8 -*-
# from odoo import http


# class BpdpksExportImport(http.Controller):
#     @http.route('/bpdpks_export_import/bpdpks_export_import/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bpdpks_export_import/bpdpks_export_import/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bpdpks_export_import.listing', {
#             'root': '/bpdpks_export_import/bpdpks_export_import',
#             'objects': http.request.env['bpdpks_export_import.bpdpks_export_import'].search([]),
#         })

#     @http.route('/bpdpks_export_import/bpdpks_export_import/objects/<model("bpdpks_export_import.bpdpks_export_import"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bpdpks_export_import.object', {
#             'object': obj
#         })
