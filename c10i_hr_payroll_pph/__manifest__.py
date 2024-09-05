# -*- coding: utf-8 -*-
{
    'name': "Payroll PPH 21",
    'summary': """""",
    'description': """""",
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",
    'category': 'Payroll Localization',
    'version': '16.0.0',
    'license': 'LGPL-3',
    'depends': ['c10i_hr','c10i_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        
        'views/hr_salary_rule_view.xml',
        'views/hr_rate_pp58_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_payslip_pph_view.xml',
        'views/hr_payslip_view.xml',
        
        'views/menuitems.xml',

        'data/hr_salary_rule.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
