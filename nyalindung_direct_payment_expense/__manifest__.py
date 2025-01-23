# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Direct Payment Expense",

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
    'depends': ['base', 'contacts', 'account', 'product', 'c10i_lhm_v16', 'c10i_direct_payment', 'ny_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/rule_security.xml',
        'views/hr_employee_expense.xml',
        'views/account_direct_payment.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_views.xml',

        'wizard/wizard_action_confirm.xml',

        # Report
        'report/my_advance_report_template.xml',
        'report/my_advance_report_action.xml',



    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
