# -*- coding: utf-8 -*-
{
    'name': "c10i_auto_account_move",

    'summary': """
        Modul Auto generate account move    
    """,

    'description': """
        Modul for automated create account move
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'c10i_lhm_v16'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/vendor_bill_views.xml',
        'views/auto_account_move_views.xml',
        'data/cron_auto_account_move.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
