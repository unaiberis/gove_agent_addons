# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    "name": "Customer Order Comment",
    "author": "AppJetty",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/avanzosc/odoo-addons",
    "summary": "Know your customer's comments, view it on checkout page",
    "depends": ["website_sale"],
    "data": [
        "views/customer_comment_config_view.xml",
        "views/sale_order_view.xml",
        "views/template.xml",
    ],
    "images": ["static/description/customer-oder-comment-large.png"],
    # 'price': 10.00,
    # 'currency': 'EUR',
    "installable": True,
    "auto_install": False,
    "support": "support@appjetty.com",
}
