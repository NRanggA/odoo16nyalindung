# -*- coding: utf-8 -*-
{
    'name': "Konsalten Stock",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'stock_account', 'purchase_stock', 'report_xlsx', 'product', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        
        # Stock Mutation
        'wizard/wizard_report_stock_mutation_views.xml',
        'report/report_stock_mutation_action.xml',

        # Stock Card
        'wizard/wizard_report_stock_card_views.xml',
        'report/report_stock_card_action.xml',

        # Detail Store Issue
        'wizard/wizard_store_issue_views.xml',
        'report/report_store_issue_action.xml',


        'views/stock_picking_views.xml',

        # Detail Receipt XLSX
        'wizard/wizard_report_detail_receipt_views.xml',
        'report/report_detail_receipt_action.xml',
        
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
