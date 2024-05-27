# -*- coding: utf-8 -*-
{
    'name': "Konsalten Material Request",
    'summary': "Konsalten Customized Material Request Module",
    'description': """
Custom Purchase Order Asset Module
====================================
The specific and easy-to-use Purchase Order Asset module in Odoo that allow you to manage your purchase order asset business process
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'base', 'stock'
    ],
    'data': [
                'data/sequences.xml',
                'data/stock_data.xml',
                'security/material_request.xml',
                'security/ir.model.access.csv',
                'views/material_request_view.xml',
                # 'views/stock_picking_type_view.xml',
                # 'views/stock_picking_view.xml',
                # 'views/stock_move_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
