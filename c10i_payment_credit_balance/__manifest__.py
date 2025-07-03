# -*- coding: utf-8 -*-
{
    'name': "Payment Credit Balance",

    'summary': """
        This module allows users to allocate credit balances to payments in Odoo.""",

    'description': """
        This module provides functionality for allocating credit balances
        to customer payments, enhancing the payment process in Odoo.
    """,

    'author': "Hendra Saputra <hendrasaputra0501@gmail.com>",
    'website': "https://konsalten.co.id",

    'category': 'Accounting & Finance',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['c10i_payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        
        'views/res_config_settings.xml',
        'views/account_move_line_view.xml',
        'views/account_payment_view.xml',
        'views/menuitems.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
        # 'demo/demo.xml',
    # ],
}
