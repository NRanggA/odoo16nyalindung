# -*- coding: utf-8 -*-
# from odoo import http


# class C10iHrPayrollAdd(http.Controller):
#     @http.route('/c10i_hr_payroll_add/c10i_hr_payroll_add', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_hr_payroll_add/c10i_hr_payroll_add/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_hr_payroll_add.listing', {
#             'root': '/c10i_hr_payroll_add/c10i_hr_payroll_add',
#             'objects': http.request.env['c10i_hr_payroll_add.c10i_hr_payroll_add'].search([]),
#         })

#     @http.route('/c10i_hr_payroll_add/c10i_hr_payroll_add/objects/<model("c10i_hr_payroll_add.c10i_hr_payroll_add"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_hr_payroll_add.object', {
#             'object': obj
#         })
