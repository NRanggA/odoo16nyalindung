# -*- coding: utf-8 -*-
{
'name' : 'Plantation Inventory Management',
'version' : '2.0.0',
'summary': 'Plantation Inventory Management',
'sequence': 10,
'description': """ Plantation Inventory Management
""",
'author': 'Konsalten Solusi Indonesia',
'website': 'https://konsaltenindonesia.com',
'depends' : [
    'stock', 
    'stock_account', 
    'purchase_stock', 
    'c10i_material_request', 
    # 'c10i_plantation', 
    'c10i_lhm_v16',
    'operating_unit',
],
'data': [
        # 'data/data.xml',
        # 'security/account_security.xml',
        'security/ir.model.access.csv',
        
        # 'views/stock_picking_view.xml',
        'views/material_request_view.xml',
        'views/product_view.xml',
        # 'views/stock_move_line_view.xml',
        # 'views/stock_move_view.xml',
        # 'views/menuitems.xml',
        
        # 'data/ir_cron_data.xml',

        # 'wizards/wizard_views.xml',
        
        # 'reports/report_views.xml',
],

    'installable': True,
    'auto_install': False,
    'application': False,
}

# [DONE] Material Request with Cost Center
# Material Request to SIV with Cot Center
# [DONE] GRN Receipt with Journal Entry