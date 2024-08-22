# -*- coding: utf-8 -*-
# from odoo import http


# class .\plantation\nyalindungPrepopulatedData(http.Controller):
#     @http.route('/.\plantation\nyalindung_prepopulated_data/.\plantation\nyalindung_prepopulated_data', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/.\plantation\nyalindung_prepopulated_data/.\plantation\nyalindung_prepopulated_data/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('.\plantation\nyalindung_prepopulated_data.listing', {
#             'root': '/.\plantation\nyalindung_prepopulated_data/.\plantation\nyalindung_prepopulated_data',
#             'objects': http.request.env['.\plantation\nyalindung_prepopulated_data..\plantation\nyalindung_prepopulated_data'].search([]),
#         })

#     @http.route('/.\plantation\nyalindung_prepopulated_data/.\plantation\nyalindung_prepopulated_data/objects/<model(".\plantation\nyalindung_prepopulated_data..\plantation\nyalindung_prepopulated_data"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('.\plantation\nyalindung_prepopulated_data.object', {
#             'object': obj
#         })
