# -*- coding: utf-8 -*-
{
    'name': "nyalindung_direct_payment_expense",

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
    'depends': ['base', 'account', 'product', 'c10i_lhm_v16', 'c10i_direct_payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_expense.xml',
        'views/res_config_settings_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
