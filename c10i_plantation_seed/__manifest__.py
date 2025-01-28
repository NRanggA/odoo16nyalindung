# -*- coding: utf-8 -*-
{
    'name': "Konsalten Pembibitan",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "http://konsaltenindonesia.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'c10i_lhm_v16', 'stock', 'report_xlsx', 'account'],

    # always loaded
    'data': [
        'security/seed_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/seed_move_views.xml',
        'views/seed_transfer_views.xml',
        'views/lhm_nursery_views.xml',
        
        'report/report_seed_mutation_action.xml',
        'wizard/wizard_seed_mutation_report_views.xml',

        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
