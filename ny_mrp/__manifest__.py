# -*- coding: utf-8 -*-
{
    'name': "Nyalindung MRP",

    'summary': """
        Customization of MRP for PT Nyalindung""",

    'description': """
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    'category': 'Human Resources',
    'version': '16.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'c10i_lhm_v16',
        'mrp'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/mrp_manual_consume_view.xml',
        'views/mrp_production_view.xml',
        'views/mrp_bom_views.xml',
        'wizard/sheet_to_produce_view.xml',
    ],
}
