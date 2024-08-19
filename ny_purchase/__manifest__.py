{
    'name': 'Nyalindung Purchase',
    'version': '1.0',
    'summary': 'Custom Purchase Module',
    'description': 'Costum Jurnal',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['purchase','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}

# access_purchase_order,access.purchase.order,model_purchase_order,purchase.model_purchase_order,1,1,1,1
# access_account_move,access.account.move,model_account_move,account.model_account_move,1,1,1,1
# access_account_move_line,access.account.move.line,model_account_move_line,account.model_account_move_line,1,1,1,1
