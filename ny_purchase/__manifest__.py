{
    'name': 'Nyalindung Purchase',
    'version': '1.0',
    'summary': 'Custom Purchase Module',
    'description': 'Costum Jurnal',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['purchase','account', 'purchase_request'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'wizard/wizard_purchase_order_outstanding_views.xml',
        'views/purchase_order_report_outstanding_views.xml',
        'views/purchase_request_report_outstanding_views.xml',
        # 'reports/report_outstanding_purchase_request.xml',
    ],
    'installable': True,
    'application': False,
}
