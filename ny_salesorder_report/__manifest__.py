{
    'name': 'Nyalindung Sales Order Report',
    'version': '1.0',
    'summary': 'Custom Sales Order Module for Report',
    'description': 'Menambahkan button report costum untuk Sales Order',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['base','product','sale','account'],
    'data': [
        # 'reports/sales_order_report.xml',
        'reports/sales_order_report_template.xml',
        'wizard/select_bank_wizard.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}