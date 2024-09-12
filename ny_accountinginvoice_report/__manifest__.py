{
    'name': 'Nyalindung Accounting Customers Invoice Report',
    'version': '1.0',
    'summary': 'Custom Accounting Customers Invoice Module for Report',
    'description': 'Menambahkan button report costum untuk Accounting Customers Invoice',
    'category': 'account',
    'author': 'Your Name',
    'depends': ['base','product','sale','account'],
    'data': [
        'reports/invoice_report_action.xml',
        'reports/invoice_report_template.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}