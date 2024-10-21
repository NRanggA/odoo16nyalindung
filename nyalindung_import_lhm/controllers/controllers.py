# -*- coding: utf-8 -*-
# from odoo import http


# class NyalindungImportLhm(http.Controller):
#     @http.route('/nyalindung_import_lhm/nyalindung_import_lhm', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nyalindung_import_lhm/nyalindung_import_lhm/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nyalindung_import_lhm.listing', {
#             'root': '/nyalindung_import_lhm/nyalindung_import_lhm',
#             'objects': http.request.env['nyalindung_import_lhm.nyalindung_import_lhm'].search([]),
#         })

#     @http.route('/nyalindung_import_lhm/nyalindung_import_lhm/objects/<model("nyalindung_import_lhm.nyalindung_import_lhm"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nyalindung_import_lhm.object', {
#             'object': obj
#         })
