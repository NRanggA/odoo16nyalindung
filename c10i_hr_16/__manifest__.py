# -*- coding: utf-8 -*-
{
    'name': "c10i_hr_16",

    'summary': """
        Modul Human Resource""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Konsulten Solusi Indonesia",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        # 'data/base_data.xml',
        # 'data/hide_menu_data.xml',
        'views/hr_bpjs_view.xml',
        'views/hr_pkp_view.xml',
        'views/hr_views.xml',
        # 'views/hr_contract_views.xml',
        # 'views/hr_public_holidays_view.xml',
        'views/res_company_views.xml',
        'security/ir.model.access.csv',

        'data/hr_bpjs_data.xml',
        'data/hr_pkp_data.xml',
        'data/hr_ptkp_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
