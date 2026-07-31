# -*- coding: utf-8 -*-
{
    'name': "Plantation.AI Integration API",
    'summary': """""",
    'description': """""",
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",
    'category': 'Human Resources',
    'version': '16.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'c10i_base_api',
        'c10i_lhm_v16',
        'c10i_plantation_planning',
        'ny_hr_attendance',
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/ny_attendance_log_view.xml',
        # 'views/res_config_settings_view.xml',
        # 'views/menuitems.xml',
        'views/lhm_contractor_views.xml',
        'views/lhm_transaction_views.xml',
    ],
}
