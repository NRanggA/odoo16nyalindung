# -*- coding: utf-8 -*-
# from odoo import http


# class C10iPurchaseAsset(http.Controller):
#     @http.route('/c10i_purchase_asset/c10i_purchase_asset/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/c10i_purchase_asset/c10i_purchase_asset/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('c10i_purchase_asset.listing', {
#             'root': '/c10i_purchase_asset/c10i_purchase_asset',
#             'objects': http.request.env['c10i_purchase_asset.c10i_purchase_asset'].search([]),
#         })

#     @http.route('/c10i_purchase_asset/c10i_purchase_asset/objects/<model("c10i_purchase_asset.c10i_purchase_asset"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('c10i_purchase_asset.object', {
#             'object': obj
#         })
