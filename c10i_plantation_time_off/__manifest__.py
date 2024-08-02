# -*- coding: utf-8 -*-
{
    'name': "c10i_plantation_time_off",

    'summary': """
        Modul Custom Plantatatin Time Off     
    """,

    'description': """
        Customize Time Off modul
    """,

    'author': "PT. Konsulten Solusi Indonesia",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_holidays', 'c10i_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/time_off_type_views.xml',
        'views/all_time_off_views.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
