# -*- coding: utf-8 -*-
{
    'name': "Konsalten Laboratorium",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "http://konsaltenindonesia.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'c10i_lhm_v16', 'stock', 'report_xlsx', 'account'],
    'data': [
        'data/ir_sequence_data.xml',
        
        'security/ir.model.access.csv',

        'views/location_type_view.xml',
        'views/lab_product_view.xml',
        'views/lab_production_order_view.xml',
        'views/menuitems.xml',

        'data/location_type_data.xml',
    ],
}
