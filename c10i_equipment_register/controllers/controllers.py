# -*- coding: utf-8 -*-
# from odoo import http


# class C10iEquipmentRegister(http.Controller):
#     @http.route('/c10i_equipment_register/c10i_equipment_register', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_equipment_register/c10i_equipment_register/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_equipment_register.listing', {
#             'root': '/c10i_equipment_register/c10i_equipment_register',
#             'objects': http.request.env['c10i_equipment_register.c10i_equipment_register'].search([]),
#         })

#     @http.route('/c10i_equipment_register/c10i_equipment_register/objects/<model("c10i_equipment_register.c10i_equipment_register"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_equipment_register.object', {
#             'object': obj
#         })
