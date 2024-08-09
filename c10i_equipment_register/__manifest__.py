# -*- coding: utf-8 -*-
{
    'name': "c10i_equipment_register",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'maintenance', 'hr_maintenance', 'c10i_purchase_equipment', 'c10i_equipment_account_asset'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/equiment_register.xml',
        # 'views/purchase_order.xml',
        'views/maintenance_equipment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
