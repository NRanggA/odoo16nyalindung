{
    'name': 'NY Sales',
    'version': '1.0',
    'summary': 'Custom Sales Module for dual pricelist and UI changes',
    'description': 'Menambahkan Fitur 2 Pricelist dll',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['base','product','sale','account', 'l10n_id_efaktur'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist_views.xml',
        'views/accountview_move_form.xml',
        'views/sale_order_views.xml',
        # 'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
}



# security 
# access_sale_order,access_sale_order,model_sale_order,,1,1,1,1