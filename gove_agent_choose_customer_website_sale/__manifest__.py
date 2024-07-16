# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Gove Agent Choose Customer Website Sale",
    "summary": "Assign agent customer to cart in checkout process and more personalizations",
    "category": "Website",
    "version": "14.0.1.1.0",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "portal",
        "sale",
        "purchase",
        "sale_commission",
        "sale_commission_group",
        "website",
        "website_sale",
        "website_sale_multiple_coupon",
        "website_sale_checkout_extra_fields",
        "website_sale_assign_agent_customer",
        "woo_commerce_ept",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/my_account_page_remove_links.xml",
        "views/offer_category_pricelist_view.xml",
        "views/product_template_view.xml",
        "views/sale_order_show_draft_finished_column.xml",
        "views/sale_order_report_agent.xml",
        "views/website_front_page.xml",
        "views/website_sale.xml",
    ],
    "installable": True,
}
