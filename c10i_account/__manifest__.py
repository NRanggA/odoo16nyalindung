# -*- coding: utf-8 -*-
{
    'name': "Konsalten Accounting",

    'summary': """
        Konsalten Customized Finance and Accounting Module""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscalyear_period_views.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_write_off_views.xml',
        'views/account_menuitem.xml',

        'data/sequence_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application' : True,
    'installable' : True
}
