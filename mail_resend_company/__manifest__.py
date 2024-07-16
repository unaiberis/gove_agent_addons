{
    "name": "Company Resend Mail",
    "version": "14.0.1.0.0",
    "category": "Custom",
    "summary": "Adds a resend_mail field to the company model "
    "and resends the mail to the company",
    "license": "AGPL-3",
    "author": "Unai Beristain - AvanzOSC",
    "website": "https://github.com/avanzosc/odoo-addons",
    "depends": ["base", "mail"],
    "data": [
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": False,
}
