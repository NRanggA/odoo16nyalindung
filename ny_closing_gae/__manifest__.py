# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Closing GAE",
    'summary': """""",
    'description': """""",
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",
    'category': 'Accounting',
    'version': '16.0.0',
    'depends': [
        'ny_hr_payroll_account',
        'ny_closing',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/gae_plan_view.xml',
        'views/account_asset_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_salary_rule_view.xml',
        'views/hr_payslip_cost_map_view.xml',
        'views/account_move_line_view.xml',
        'views/closing_process_view.xml',
        'views/closing_gae_view.xml',

        'wizard/move_line_set_gea_view.xml',

        'views/menuitems.xml',
        
        'data/account_journal.xml',
    ],
}
