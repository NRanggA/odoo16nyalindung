# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Closing Process",
    'summary': """""",
    'description': """""",
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",
    'category': 'Accounting',
    'version': '16.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'c10i_lhm_v16',
        'ny_plantation',
        'account',
        'c10i_plantation_seed'
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/account_move_line_view.xml',
        'views/running_workshop_view.xml',
        'views/running_vehicle_view.xml',
        'views/running_machine_view.xml',
        'views/closing_project_view.xml',
        'views/closing_nursery_view.xml',
        'views/lhm_plant_block_view.xml',
        'views/plantation_season_view.xml',
        'views/lhm_activity_view.xml',
        'views/closing_plantation_view.xml',
        'views/closing_production_view.xml',
        'views/closing_process_view.xml',
        'views/menuitems.xml',
        
        'data/account_journal.xml',
    ],
}
