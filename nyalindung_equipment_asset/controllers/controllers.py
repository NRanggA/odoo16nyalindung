# -*- coding: utf-8 -*-
# from odoo import http


# class NyalindungEquipmentAsset(http.Controller):
#     @http.route('/nyalindung_equipment_asset/nyalindung_equipment_asset', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nyalindung_equipment_asset/nyalindung_equipment_asset/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nyalindung_equipment_asset.listing', {
#             'root': '/nyalindung_equipment_asset/nyalindung_equipment_asset',
#             'objects': http.request.env['nyalindung_equipment_asset.nyalindung_equipment_asset'].search([]),
#         })

#     @http.route('/nyalindung_equipment_asset/nyalindung_equipment_asset/objects/<model("nyalindung_equipment_asset.nyalindung_equipment_asset"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nyalindung_equipment_asset.object', {
#             'object': obj
#         })
