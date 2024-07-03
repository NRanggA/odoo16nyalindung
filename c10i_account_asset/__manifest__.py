# -*- coding: utf-8 -*-
{
    'name': "Konsalten Account Asset",
    'summary': "Konsalten Additional Customized Account Asset Module",
    'description': "",
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'category': 'Accounting',
    'version': '14.1.0',
    'depends': [
        'base',
        'account',
        'om_account_asset'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/asset_acquisition_sequence.xml',
        'views/asset_acquisition_views.xml',
        'views/account_asset_views.xml',
        'views/account_asset_disposal_views.xml',

    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}