# -*- coding: utf-8 -*-
{
    'name': "Konsalten Direct Payment",
    'summary': "",
    'description': """
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'base', 'account', 'c10i_lhm_v16'   
    ],
    'data': [
                # 'data/sequences.xml',
                'security/payment_security.xml',
                'security/ir.model.access.csv',
                'views/account_journal.xml',
                'views/account_direct_payment_view.xml',
                'views/res_config_settings_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
