# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Employee Attendance",
    'summary': """
        Customization of Employee Attendance for PT Nyalindung""",
    'description': """
    """,
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",
    'category': 'Human Resources',
    'version': '16.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'c10i_attendance',
        'c10i_base_api'
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ny_attendance_log_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_attendance_sheet_view.xml',
        'views/res_config_settings_view.xml',
        'views/menuitems.xml',
    ],
}
