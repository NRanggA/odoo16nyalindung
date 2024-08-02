{
    'name': 'MRP Karet',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Modul MRP Karet',
    'depends': ['base', 'mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_karet_views.xml',
    ],
    'installable': True,
    'application': False,
}

