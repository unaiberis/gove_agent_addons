{
    'name': 'Company Resend Email',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Adds a resend_email field to the company model',
    'description': 'This module adds a unique resend_email field to each company in Odoo.',
    'author': 'Unai Beristain - AvanzOSC',
    'depends': ['base', 'mail'],
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
}
