{
    'name': 'Material Request Report',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Report for Material Request Form',
    'description': 'This module provides a report template for material requests.',
    'author': 'Your Name',
    'depends': ['base', 'stock', 'c10i_material_request'],
    'data': [
        'reports/material_request_report_action.xml',
        'reports/material_request_report_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
