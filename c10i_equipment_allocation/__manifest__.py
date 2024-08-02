# -*- coding: utf-8 -*-
{
    'name': "Konsalten Equipment Allocation",
    'summary': "Equipment Allocation",
    'description': """
Custom Equipment Allocation
====================================
* Create an Allocation request
* Create Return Allocation
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'base', 'hr', 'stock', 'maintenance', 'hr_maintenance'
    ],
    'data': [
                # 'data/sequences.xml',
                # 'security/ir.model.access.csv',
                # 'views/maintenance_view.xml',
                # 'views/allocation_request_view.xml',
                'security/ir.model.access.csv',
                'wizard/cancel_button_wizard.xml',
                'wizard/reject_button_wizard.xml',
                'wizard/warning_message_wizard.xml',
                'wizard/replace_wizard.xml',
                'views/allocation_request_view.xml',
                'views/hr_view.xml',
                'views/maintenance_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
