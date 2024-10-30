# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Payroll",

    'summary': """
        Customization of HR Payroll for PT Nyalindung""",

    'description': """
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    'category': 'Payroll Localization',
    'version': '16.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'resource',
        'ny_plantation',
        'ny_hr_attendance',
        'c10i_hr_payroll',
        'c10i_hr_payroll_other_inputs',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/other_input_type_data.xml',
        
        'views/hr_contract_view.xml',
        'views/ny_premi_penyadap_view.xml',
        'views/resource_calendar_view.xml',
        'views/hr_foreman_view.xml',
        'views/lhm_plant_block_view.xml',
        'views/lhm_transaction_nap_line_view.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
