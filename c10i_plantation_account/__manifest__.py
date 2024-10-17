# -*- coding: utf-8 -*-
{
'name' : 'Plantation Management Finance',
'version' : '2.0.0',
'summary': 'Plantation Management Finance',
'sequence': 10,
'description': """ Plantation Management System
""",
'author': 'Konsalten Solusi Indonesia',
'website': 'https://konsaltenindonesia.com',
'depends' : [
    'account', 
    'account_operating_unit', 
    'c10i_direct_payment', 
    'c10i_direct_payment_employee_expense', 
    'c10i_plantation', 
],
'data': [
        # 'data/data.xml',
        'security/account_security.xml',
        'security/ir.model.access.csv',
        
        'views/account_direct_payment_view.xml',
        'views/account_move_line_view.xml',
        'views/account_move_view.xml',

        'views/plantation_closing_running_account_view.xml',
        'views/plantation_closing_account_allocation.xml',
        'views/plantation_closing_sequence_view.xml',
        
        'views/menuitems.xml',
        
        # 'data/ir_cron_data.xml',

        # 'wizards/wizard_views.xml',
        
        # 'reports/report_views.xml',
],

    'installable': False,
    'auto_install': False,
    'application': True,
}

# [DONE] Dashboard
# [????] Auto Cash Register from Payment
# [DONE] Direct Payment
# [DONE] Employee Advance & Settlement
# [????] Fund Request