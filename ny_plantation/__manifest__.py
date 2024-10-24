# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Plantation",

    'summary': """
        Customization of Plantation for PT Nyalindung""",

    'description': """
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    'category': 'Human Resources',
    'version': '16.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'c10i_lhm_v16',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',

        'views/hr_foreman_view.xml',
        'views/lhm_transaction_view.xml',
        'views/lhm_plant_block_view.xml',
    ],
}
