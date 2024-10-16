{
    'name': "Konsalten Advanced Payment",
    'summary': "",
    'description': """
    """,
    'author': "Konsalten Indonesia",
    'website': "http://konsaltenindonesia.com",
    'version': '14.1.0',
    'depends': [
        'base', 'sale','account','purchase'
    ],
    'data': [
                # 'data/sequences.xml',
                # 'security/payment_security.xml',
                'security/ir.model.access.csv',
                'views/views.xml',
                'views/purchase_order_views.xml',
                'views/sale_order_views.xml',
                'views/res_config_settings_views.xml',
                'views/account_move_views.xml',
                'wizard/purchase_make_invoice_advance_views.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}