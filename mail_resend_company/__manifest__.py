{
    'name': 'Company Resend Mail',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Adds a resend_mail field to the company model and resends the mail to the company',
    'description': 'This module adds a unique resend_mail field to each company in Odoo.',
    'author': 'Unai Beristain - AvanzOSC',
    'depends': ['base', 'mail'],
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
}
