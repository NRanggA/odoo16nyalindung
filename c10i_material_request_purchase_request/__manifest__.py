# -*- coding: utf-8 -*-
{
    'name': "Purchase from Material Request",
    'summary': "Purchase from Material Request",
    'description': """
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'purchase_request', 
        'c10i_material_request', 
    ],
    'data': [
                # 'data/sequences.xml',
                'security/ir.model.access.csv',
                'wizard/internal_move_create_view.xml',
                'views/material_request_view.xml',
                'views/purchase_request_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
