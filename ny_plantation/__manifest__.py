# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Plantation",

    'summary': """
        Customization of Plantation for PT Nyalindung""",

    'description': """
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    'category': 'Human Resources',
    'version': '16.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'c10i_lhm_v16',
        'c10i_plantation_payroll',
        'hr',
        'stock',
    ],

    # always loaded
    'data': [
        'security/ny_security.xml',
        'security/ir.model.access.csv',
        'data/stock_location_data.xml',
        'data/picking_type_data.xml',

        'views/hr_foreman_view.xml',
        'views/lhm_transaction_view.xml',
        'views/lhm_plant_block_view.xml',
        'views/hr_employee.xml',
        'views/lhm_drc_view.xml',
        'views/lhm_nap_view.xml',
        'views/hr_employee_type.xml',
        'views/stock_ripening_pisang_view.xml',
    ],
}
