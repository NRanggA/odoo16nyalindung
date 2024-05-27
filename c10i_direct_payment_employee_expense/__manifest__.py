# -*- coding: utf-8 -*-
{
    'name': "Konsalten Expense Advance and Settlement",
    'summary': "",
    'description': """
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'c10i_direct_payment'
    ],
    'data': [
                # 'data/sequences.xml',
                # 'security/payment_security.xml',
                'security/ir.model.access.csv',
                'views/account_employee_expense_view.xml',
                'views/res_config_settings_view.xml',
                # 'views/menuitems.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
