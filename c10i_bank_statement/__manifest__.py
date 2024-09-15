# -*- coding: utf-8 -*-
{
    'name': "Bank Statement Custom - Konsalten",

    'summary': """
        Customize bank statement flow.""",

    'description': """
        Customize bank statement flow.
    """,

    'author': "Konsulten Solusi Indonesia",
    'website': "https://www.yourcompany.com",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','account_statement_base', 'account_reconcile_oca'],

    'data': [
        'security/ir.model.access.csv',
        'data/cash_type.xml',
        'views/bank_statement.xml',
        'views/cash_type.xml',
        'views/menu_items.xml',
        'views/templates.xml',
    ],
}
