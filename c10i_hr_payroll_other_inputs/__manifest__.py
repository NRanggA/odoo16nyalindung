# -*- coding: utf-8 -*-
{
    'name': "Payroll Other Inputs",

    'summary': """
        Provide worksheet for input/upload Other Inputs that will be called inside Payslip""",

    'description': """
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    'category': 'Payroll Localization',
    'version': '16.0.0',

    'depends': ['c10i_hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_other_input_type_view.xml',
        'views/hr_payslip_batch_other_input_view.xml',
        'views/hr_payslip_view.xml',
        'views/menuitems.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
