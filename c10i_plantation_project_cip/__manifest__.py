# -*- coding: utf-8 -*-
{
    'name': "c10i_plantation_project_cip",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','c10i_lhm_v16', 'c10i_purchase_equipment', 'maintenance', 'nyalindung_equipment_asset'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/lhm_project_views.xml',
        'views/account_move_line_views.xml',

        'data/product_cip_data.xml'

        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
