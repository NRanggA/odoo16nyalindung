# -*- coding: utf-8 -*-
{
    'name': "Plantation Payroll",
    'summary': """
        Integration between LHM Plantation and Payslip""",
    'description': """
    """,
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",
    'category': 'Payroll Localization',
    'version': '0.1',
    'depends': ['c10i_hr_payroll', 
                'c10i_hr_payroll_pph', 
                'c10i_lhm_v16', 
                'c10i_hr_payroll_other_inputs'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_view.xml',
        'views/hr_employee_view.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
