# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Payroll Accounting",

    'summary': """
        Customization of HR Payroll for Accounting purpose at PT Nyalindung""",

    'description': """
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    'category': 'Payroll Localization',
    'version': '16.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'ny_hr_payroll'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/hr_salary_rule_view.xml',
        'views/hr_payslip_cost_map_view.xml',
        # 'views/hr_payslip_view.xml',
        'views/hr_payslip_run_view.xml',
        'views/account_cost_map_payroll_view.xml',
        'views/res_config_settings_view.xml',
    ],
}
