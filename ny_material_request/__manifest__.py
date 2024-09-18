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
    'depends': ['base', 'purchase', 'account', 'stock', 'c10i_material_request_equipment_allocation', 'c10i_lhm_v16', 'c10i_material_request_purchase_request'],
    'data': [
                # 'data/sequences.xml',
                # 'data/stock_data.xml',
                # 'security/material_request.xml',
                # 'security/ir.model.access.csv',
                'views/material_request_view.xml',
    ],
    
    'installable': True,
    'application': False,
}
