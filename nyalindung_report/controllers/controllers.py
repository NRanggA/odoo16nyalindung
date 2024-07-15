# -*- coding: utf-8 -*-
# from odoo import http


# class NyReport(http.Controller):
#     @http.route('/ny_report/ny_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ny_report/ny_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ny_report.listing', {
#             'root': '/ny_report/ny_report',
#             'objects': http.request.env['ny_report.ny_report'].search([]),
#         })

#     @http.route('/ny_report/ny_report/objects/<model("ny_report.ny_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ny_report.object', {
#             'object': obj
#         })
