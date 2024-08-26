# -*- coding: utf-8 -*-
# from odoo import http


# class .\plantation\nyalindungDirectPaymentExpense(http.Controller):
#     @http.route('/.\plantation\nyalindung_direct_payment_expense/.\plantation\nyalindung_direct_payment_expense', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/.\plantation\nyalindung_direct_payment_expense/.\plantation\nyalindung_direct_payment_expense/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('.\plantation\nyalindung_direct_payment_expense.listing', {
#             'root': '/.\plantation\nyalindung_direct_payment_expense/.\plantation\nyalindung_direct_payment_expense',
#             'objects': http.request.env['.\plantation\nyalindung_direct_payment_expense..\plantation\nyalindung_direct_payment_expense'].search([]),
#         })

#     @http.route('/.\plantation\nyalindung_direct_payment_expense/.\plantation\nyalindung_direct_payment_expense/objects/<model(".\plantation\nyalindung_direct_payment_expense..\plantation\nyalindung_direct_payment_expense"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('.\plantation\nyalindung_direct_payment_expense.object', {
#             'object': obj
#         })
