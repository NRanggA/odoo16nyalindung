{
    'name': 'Nyalindung Equipment',
    'version': '1.0',
    'summary': 'Custom Equipment Module',
    'description': ' ',
    'category': 'Equipment',
    'author': 'Cimol KSI',
    'depends': ['base','product','sale','account', 'c10i_equipment_register'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_equipment_view.xml',
    ],
    'installable': True,
    'application': False,
}