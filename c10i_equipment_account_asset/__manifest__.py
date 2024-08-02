# -*- coding: utf-8 -*-
{
    'name': "Konsalten Account Asset from Equipment",
    'summary': "Konsalten Account Asset from Equipment",
    'description': """
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'om_account_accountant',
        'om_account_asset',
        'c10i_account_asset',
        'c10i_purchase_equipment', 
    ],
    'data': [
                'data/sequences.xml',
                'security/ir.model.access.csv',
                'views/account_asset_acquisition_view.xml',
                'views/account_asset_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
