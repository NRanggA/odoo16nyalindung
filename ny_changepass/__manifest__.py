{
    'name': 'NY Change Password View',
    'version': '16.0.1.0.0',
    'category': 'Custom',
    'summary': 'Add an eye icon to view password on change password form.',
    'description': "",
    'author': 'CimolGans',
    'website': 'https://www.yourwebsite.com',
    'depends': ['base','web'],
    'data': [
        'views/ny_changepass_templates.xml',
        # 'views/ny_changepass_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ny_changepass/static/src/js/ny_changepass.js',
            'ny_changepass/static/src/components/*/*.js',
            'ny_changepass/static/src/components/*/*.xml',
            'ny_changepass/static/src/components/*/*.scss',
        ],
    },
    'installable': True,
    'application': False,
}
