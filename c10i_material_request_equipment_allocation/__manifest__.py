# -*- coding: utf-8 -*-
{
    'name': "Material Request with Equipment Allocation",
    'summary': "Konsalten Customized Material Request Module",
    'description': """
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'c10i_material_request',
        'c10i_equipment_allocation',
        'c10i_purchase_equipment',
    ],
    'data': [
                # 'data/sequences.xml',
                # 'security/ir.model.access.csv',
                'views/allocation_request_view.xml',
                'views/material_request_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
