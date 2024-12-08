# -*- coding: utf-8 -*-
{
    'name': 'Account Parent',
    'version': '',
    'summary': """Account Parent Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['account'],
    "data": [
        "security/security.xml",
        "views/account_account_views.xml",
        "views/res_config_settings_views.xml"
    ],
    'assets': {
       
        'web.assets_backend': [
            # 'c10i_account_parent/static/src/js/account_parent_widgets.js',
            'c10i_account_parent/static/src/js/account_type_selection.js',

            # 'c10i_account_parent/static/src/xml/account_parent_line.xml',
            ]
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': '_assign_account_parent',
}
