# -*- coding: utf-8 -*-
{
    'name': "Account Netting",

    'summary': """
        Account Netting for offsetting receivables and payables""",

    'description': """
        This module allows you to offset receivables and payables for the same partner
        through account netting operations.
    """,

    'author': "Hendra Saputra <hendrasaputra0501@gmail.com>",
    'website': "https://konsalten.co.id",

    'category': 'Accounting',
    'version': '16,0.0.1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        
        'wizard/wizard_set_netting_line_view.xml',
        'views/account_netting_view.xml',
        
        'views/menuitems.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
