# -*- coding: utf-8 -*-
{
    'name': "Konsalten Purchase Order Equipment",
    'summary': "Konsalten Customized Purchase Asset Equipment Module",
    'description': """
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'purchase', 
        'purchase_request', 
        'maintenance',
        'c10i_equipment_allocation'
    ],
    'data': [
                'data/sequences.xml',
                'security/ir.model.access.csv',
                'views/equipment_register_view.xml',
                'views/purchase_view.xml',
                'views/maintenance_view.xml',
                'views/product_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
