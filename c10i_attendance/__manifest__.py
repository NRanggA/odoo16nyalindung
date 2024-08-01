# -*- coding: utf-8 -*-
{
    'name': "c10i_attendance",

    'summary': """
        Modul Custom Absensi odoo 16
        """,

    'description': """
        Modul absensi (Attendance) Odoo versi 16
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance', 'c10i_lhm_v16', 'hr_holidays'],

    # always loaded
    'data': [
        # 'security/group_definitions.xml',
        'security/ir.model.access.csv',
        'views/import_attendance_views.xml',
        'views/attendance_sheet_views.xml',
        'views/attendance_correction_views.xml',
        'views/hr_attendance_type.xml',
        'views/menu_views.xml',
        'data/sequence_data.xml',
        'data/cron_attendance.xml',

 
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

}
