# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Prepopulated Data",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

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
    'depends': ['base', 'account', 'base_export_import', 'l10n_id_efaktur'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/prepopulated_data.xml',
        'views/account_move.xml',
        'views/menu_items.xml',
        
        'wizard/wizard_import_prepopulated_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/nyalindung_prepopulated_data/static/src/**/*.js',   
            '/nyalindung_prepopulated_data/static/src/**/*.xml',
            ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
