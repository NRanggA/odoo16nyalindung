# -*- coding: utf-8 -*-
{
    'name': "Konsalten API Base",
    'description': """
* Base API Integration template
    """,
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://www.konsaltenindonesia.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/api_client_list_view.xml',
        
        'data/api_cron.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
